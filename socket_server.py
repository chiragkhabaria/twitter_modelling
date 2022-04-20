from ftplib import MAXLINE
import socket_tweet_streamer
import socket
import configparser

hash_tag_list = ["ukraine","russia","war"]

def openSocket(host, port, maxListener = 10):
    try:
        print("*** Opening Socket at host " + host + " and port # " + str(port))
        tweetSocket = socket.socket()
        tweetSocket.bind((host, port))
        tweetSocket.listen(maxListener)
        return tweetSocket.accept()
    except Exception as e:
        print('Error occurred while opening port: Error Details ::' + str(e))

def getSocketTweetStreamer() -> socket_tweet_streamer.socketTweetStreamer:
    try:
        config = configparser.ConfigParser()
        config.read('model.ini')
        socketStreamer = socket_tweet_streamer.socketTweetStreamer(
                c_socket = openSocket(
                    host = config['SOCKET']['host'],
                    port = int(config['SOCKET']['port']),
                    maxListener = 1 
                )[0],
                consumer_key = config['TWITTER']['twitter_api_key'], 
                consumer_secret = config['TWITTER']['twitter_api_key_secret'], 
                access_token= config['TWITTER']['twitter_token_key'], 
                access_token_secret = config['TWITTER']['twitter_token_secret']
            
        )
        return socketStreamer
    except Exception as e:
        print('Error occurred while opening socket port: Error Details ::' + str(e))

def startSocketStreamer():
    try:
        socketStreamer = getSocketTweetStreamer()
        socketStreamer.filter(track = hash_tag_list)
    except Exception as e:
        print('Error occurred wile starting socket streamer. Error Details ::' + str(e))

if __name__ == "__main__":
    startSocketStreamer()