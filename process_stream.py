import pyspark
import pyspark_stream
import re
import ast
import configparser
from pyspark.sql import SparkSession
from collections import namedtuple 
from textblob import TextBlob



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
                get_sentiment(tweet=tweet)

def stanitize_tweet(tweet:str):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                |(\w+:\/\/\S+)", " ", tweet).split())

def get_sentiment(tweet:str):
    try:
        tweet_sentiment = TextBlob(stanitize_tweet(tweet))
        sentiment_text = ""
        if tweet_sentiment.sentiment.polarity > 0:
            sentiment_text =  'positive'
        elif tweet_sentiment.sentiment.polarity == 0:
            sentiment_text = 'neutral'
        else:
            sentiment_text = 'negative'
        
        print("Sentiment for Tweet :" + stanitize_tweet(tweet) + "\n. sentiment_text :: " + sentiment_text + ". Polarity ::" + str(tweet_sentiment.sentiment.polarity))

        return (sentiment_text, tweet_sentiment.sentiment.polarity)
    except Exception as e:
        print('Error occurred while getting tweet sentiment. Error Details ::' + str(e))

if __name__ == "__main__":
    pysparkStream = pyspark_stream.pysparkStream()
    processStream(pysparkStream)
    #displayCapturedData(pysparkStream)