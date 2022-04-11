from tweepy import OAuthHandler
from tweepy import Stream
import tweepy 
import logging 
from time import sleep 
import json

class socketTweetStreamer(tweepy.Stream):
    __bootstrap_servers = None 
    __tweetProducer = None
    __c_socket = None 
    def __init__(self, c_socket,consumer_key, consumer_secret, access_token, access_token_secret, **kwargs):
        self.__c_socket = c_socket
        print(str(c_socket))
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, **kwargs)

    def on_status(self, status):
        try:
            #1 Getting the tweet details from the streamer 
            if status.retweeted or 'RT @' in status.text:
                return
            if status.truncated:
                text = status.extended_tweet['full_text']
            else:
                text = status.text
            location = status.coordinates
            if location:
                location = str(status.coordinates['coordinates'])
            if status.id_str:
                id_str = status.id_str
            #2  Creating the Tweet Dictionary from the tweet object 
            _tweet_dict = {"tweetText" : text,
            "tweetLocation" : location,
            "id_str": id_str}
            #3 send using producer
            text = (str(_tweet_dict) + "\n") 
            print(text.encode('utf-8'))
            self.__c_socket.send(text.encode('utf-8'))
            return True
        except Exception as e:
            on_status_error = 'Error occurred in on_status event. Error Detais :: '  + str(e)
            logging.error(on_status_error)
            raise Exception(on_status_error)
    
    # def on_data(self, data):
    #   try:
    #       msg = json.loads( data )
    #       print(str(msg))
    #       #print(msg["text"] + '\n')
    #       self.__c_socket.send( (msg['text'] + '\n').encode('utf-8') )
    #       return True
    #   except BaseException as e:
    #       print("Error on_data: %s" % str(e))
    #   return True
