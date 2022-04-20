import pyspark
import pyspark_stream
import re
import ast
import configparser
import datetime
from pyspark.sql import SparkSession
from collections import namedtuple 
from textblob import TextBlob
from pyspark.sql.types import *
from pyspark.sql.functions import col, lit
import pyspark.sql.functions as F
import os


def processStream(pysparkStream:pyspark_stream.pysparkStream, captureStream = 60) -> None:
    try:
        #load the config 
        config = configparser.ConfigParser()
        config.read('model.ini')
        #initialize pyspark_stream 
        ##start the streaming context 
        
        if pysparkStream.sparkContext == None:
            raise Exception('Failed to initialize Spark Context')
        
        sparkSession = SparkSession(pysparkStream.sparkContext)
        
        sparkSocketStream = pysparkStream.sparkStreamingContext.socketTextStream(
            hostname=config["SOCKET"]["host"],
            port = int(config["SOCKET"]["port"])
        )
        #capture the stream
        dataLines = sparkSocketStream.window(windowDuration = 20)
    
        lines = dataLines.map( lambda text: text.split("\n"))
        #lines.pprint()
        
        lines.foreachRDD(
            processTweet
        )
        ##start the stream     
        pysparkStream.sparkStreamingContext.start()
        pysparkStream.sparkStreamingContext.awaitTermination(timeout= captureStream)
        #displayCapturedData(pysparkStream)
    except Exception as e:
        print("Error occurred while processing the streaming. Error Details :: "+ str(e))

def processTweet(rdd:pyspark.RDD):
    if not rdd.isEmpty():
        data_collect = rdd.toDF().collect()
        for row in data_collect:
            print("printing Rows :::" + str(row[0]))
            data = ast.literal_eval(str(row[0]))
            print("TweetText ::" + str(data))
            if (data != None):
                tweet = data["tweetText"]
                sanitized_tweet, sentiment_text , polarity = get_sentiment(tweet=tweet)
                add_analytics_data(
                                    id_str = data["id_str"], 
                                    tweet = data["tweetText"],
                                    sanitized_tweet = sanitized_tweet,
                                    sentiment_text=sentiment_text, 
                                    polarity=polarity,
                                    df = rdd.toDF()
                                )
            
def add_analytics_data(id_str :str,tweet :str,sanitized_tweet:str, sentiment_text:str,polarity : float, df):
    try:
        sparkSession = pyspark_stream.pysparkStream().sparkSession
        data_path = os.getcwd() + "/data/tweets/all_tweets.parquet"
        print("*****adding analytics data*****")
        columns = ["id_str","tweet","cleaned_tweet","sentiment_text","polarity","row_add_timestamp"]
        data = [
            (id_str,tweet,sanitized_tweet,sentiment_text,polarity,datetime.datetime.now())
        ]
        
        spark_df = sparkSession.createDataFrame(data, columns)
        # spark_df = df.withColumn("id_str",lit((id_str)))\
        #             .withColumn("tweet",lit((tweet)))\
        #             .withColumn("sanitized_tweet", lit((sanitized_tweet)))\
        #             .withColumn("sentiment_text", lit((sentiment_text)))\
        #             .withColumn("polarity", lit((polarity)))\
        #             .withColumn("row_add_timestamp",lit((datetime.datetime.now())))
        print("*****Created Spark DataSet*****")
        final_spark_df = spark_df.withColumn("date",F.date_format(F.col("row_add_timestamp"),"yyyyMMDdd"))\
                                .withColumn("hour",F.date_format(F.col("row_add_timestamp"),"HH"))
        print("*****Final Spark DataSet*****")
        final_spark_df.write.mode("append").partitionBy("date","hour").parquet(data_path) 
    except Exception as e:
        print('Error occurred while adding analytics data to parquet. Error Details :: ' + str(e))

def load_data_from_df():
    try:
        data_path = "/data/tweets/all_tweets.parquet"

    except Exception as e:
        print("***Error occurred while loading data from dataframe ***. Error Details ::" + str(e))

def sanitized_tweet(tweet:str):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                |(\w+:\/\/\S+)", " ", tweet).split())

def get_sentiment(tweet:str):
    try:
        sanitizedTweet = sanitized_tweet(tweet)
        tweet_sentiment = TextBlob(sanitizedTweet)
        sentiment_text = ""
        if tweet_sentiment.sentiment.polarity > 0:
            sentiment_text =  'positive'
        elif tweet_sentiment.sentiment.polarity == 0:
            sentiment_text = 'neutral'
        else:
            sentiment_text = 'negative'
        
        print("Sentiment for Tweet :" + sanitized_tweet(tweet) + "\n. sentiment_text :: " + sentiment_text + ". Polarity ::" + str(tweet_sentiment.sentiment.polarity))

        return (sanitizedTweet, sentiment_text, tweet_sentiment.sentiment.polarity)
    except Exception as e:
        print('Error occurred while getting tweet sentiment. Error Details ::' + str(e))

if __name__ == "__main__":
    pysparkStream = pyspark_stream.pysparkStream()
    processStream(pysparkStream, captureStream=600)
    #displayCapturedData(pysparkStream)