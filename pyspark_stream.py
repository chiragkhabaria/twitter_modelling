from tempfile import NamedTemporaryFile
import time 
import configparser
from argparse import _AppendAction
from pyspark import SparkContext,SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext, SparkSession,Row
from pyspark.sql.functions import desc
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as F


class pysparkStream():
    __sparkContext = None
    __sparkStreamingContext = None 
    __sparkSQLContext = None
    __sparkSession = None 

    def __init__(self, appName = "twitterApp") -> None:
        self.__appName = appName
    
    
    @property
    def sparkContext (self)-> SparkContext:
        if (self.__sparkContext == None):
            self.__sparkContext = self.__getSparkContext()
        return self.__sparkContext
    
    @property 
    def sparkStreamingContext(self) -> StreamingContext:
        if (self.__sparkStreamingContext == None):
            self.__sparkStreamingContext = self.__getSparkStreamingContext()
        return self.__sparkStreamingContext
    
    @property
    def sparkSQLContext(self) -> SQLContext:
        if(self.__sparkSQLContext == None):
            self.__sparkSQLContext = self.__getSparkSQLContext()
        return self.__sparkSQLContext

    @property 
    def sparkSession(self) -> SparkSession:
        if (self.__sparkSession == None):
            self.__sparkSession = self.__getSparkSession()
        return self.__sparkSession

    def __getSparkContext (self) -> SparkContext:
        try:
            conf = SparkConf()
            conf.setAppName(self.__appName) 
            return SparkContext.getOrCreate(conf = conf)
        except Exception as e:
            print("Error occurred while fetching the spark context. Error Details ::" + str(e))

    def __getSparkStreamingContext(self) ->StreamingContext:
        try:
            streamingContext = StreamingContext(sparkContext = self.sparkContext,batchDuration=5)
            streamingContext.checkpoint("checkpoint_twitterApp")
            return streamingContext
        except Exception as e:
            print("Error occurred while fetching the spark streaming context. Error Details :: " + str(e))

    def __getSparkSQLContext (self) -> SQLContext:
        try:
            return SQLContext(
                                sparkContext = self.sparkContext
                            ).getOrCreate(
                                self.sparkContext
                            )
        except Exception as e:
            print("Error occurred while opening the SQL Context. Error Details ::" + str(e))
        
    def __getSparkSession(self) -> SparkSession:
        try:
            return SparkSession.builder.appName(
                name = self.__appName
            ).getOrCreate()
        except Exception as e:
            print('Error occurred while creating the spark session. Error Details ::' + str(e))

