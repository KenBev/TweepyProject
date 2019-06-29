from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy.auth import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import twitter_credentials
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

#### TWITTER CLIENT ####
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticatior().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list


    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

#### TWITTER AUTHENTICATOR #####
class TwitterAuthenticatior():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth



class TwitterStreamer():
    """
        Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticatior()

    def stream_tweets(self, fetched_tweets_filename, has_tag_list):
        #This handles Twitter authentication and the connection to the Twitter Streaming API.
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()

        stream = Stream(auth, listener)

        stream.filter(track=has_tag_list)

class TwitterListener(StreamListener):
    """
        Basic listener class that just prints recieved tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True


    def on_error(self, status):
        if status == 420:
            #Returning false on_data method in case rates limit occurs
            return False
        print(status)

class TweetAnalyser():
    """
    Functionality for analysing and categorising content from tweets
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyse_sentiment(self,tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['like'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['tweets']])

        return df

if __name__ == "__main__":


    twitter_client = TwitterClient()
    tweet_analyser = TweetAnalyser()
    api = twitter_client.get_twitter_client_api()



    tweets = api.user_timeline(screen_name="angryjoeshow", count=200)
    df = tweet_analyser.tweets_to_data_frame(tweets)


    print(df.head(10))

    positive_to_negative = df['sentiment'].value_counts()
    print(positive_to_negative)
    labels = 'Positive', 'Negative', 'Neutral'
    fig1, ax1 = plt.subplots()

    ax1.pie(positive_to_negative, labels=labels, autopct='%1.1f%%')
    plt.show()





    # Get average length of all tweets.

    #print(np.mean(df['len']))

    #Get the number of likes for most liked tweet

    #print(np.max(df['like']))

    #Get the number of retweets for most retweeted post

    #print(np.max(df['retweets']))


    # Time Series
    #time_likes = pd.Series(data=df['like'].values, index=df['date'])
    #time_likes.plot(figsize=(16,4), color='red')
    #plt.show()

    # Time Series reteets
    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    #time_retweets.plot(figsize=(16,4), color='red')
    #plt.show()

    time_likes = pd.Series(data=df['like'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), label='Likes', legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16,4), label='Retweets', legend=True)

    plt.show()

    #print(tweets[6].retweet_count)
    #print(dir(tweets[0]))
    #print(df.head(10))

    #has_tag_list = ['vegan', 'gluten free', 'dairy free', 'free from foods']
    #fetched_tweets_filename = "tweets.json"

    #twitter_client = TwitterClient("quornfoods")
    #print(twitter_client.get_user_timeline_tweets(1))


    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename, has_tag_list)
