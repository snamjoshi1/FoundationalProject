#!/usr/bin/env python
# coding: utf-8

# In[201]:


import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config
from wordcloud import WordCloud, STOPWORDS
import snscrape.modules.twitter as sntwitter
import re
from flask import Flask,request, url_for, redirect, render_template, jsonify,flash
import pickle
import numpy as np

nltk.download('vader_lexicon')


# In[202]:


def config():
    nltk.download('punkt')
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10
    
    return config


# In[203]:


def newsGoogle(CompanyName,yesterday,now):
    import time
    #As long as the company name is valid, not empty...
    if CompanyName != '':
        print(f'Searching for and analyzing {CompanyName}, Please be patient, it might take a while...')
        #Extract News with Google News
        googlenews = GoogleNews(start='01/11/2022',end='01/11/2022')
        #googlenews = GoogleNews(period='1d')
        googlenews.search(CompanyName)
        result = googlenews.result()
        df_New = pd.DataFrame()
        page_init=1
        while (page_init < 2):
            result=googlenews.page_at(page_init)
            page_init+=1
            time.sleep(3)
            #store the results
            df_New = df_New.append(result)
    return df_New


# In[204]:


def newsPerprocess(companyName):
    now = dt.date.today()
    now = now.strftime('%m-%d-%Y')
    yesterday = dt.date.today() - dt.timedelta(days = 2)
    print(yesterday)
    yesterday = yesterday.strftime('%m-%d-%Y')
    dfTest=newsGoogle(companyName,yesterday,yesterday)
    print(dfTest)
    try:
        from datetime import datetime
        dfTest['DateNew']=dfTest['datetime'].dt.date
        end = datetime.now()
        end=end.date()
        print(end)
        dfTest['DateNew'] = dfTest['DateNew'].fillna(end)
        list =[] #creating an empty list 
        for i in dfTest.index:
            dict = {} #creating an empty dictionary to append an article in every single iteration
            config=Config()
            article = Article(dfTest['link'][i],config=config) #providing the link
            try:
                article.download() #downloading the article 
                article.parse() #parsing the article
                article.nlp() #performing natural language processing (nlp)
            except:
                pass 
        #storing results in our empty dictionary
            dict['Date']=dfTest['DateNew'][i]
            dict['Media']=dfTest['media'][i]
            dict['Title']=article.title
            dict['Article']=article.text
            dict['Summary']=article.summary
            dict['Key_words']=article.keywords
            list.append(dict)
        check_empty = not any(list)
    # print(check_empty)
        if check_empty == False:
            news_df=pd.DataFrame(list) #creating dataframe
            print(news_df)

    except Exception as e:
    #exception handling
        #print("exception occurred:" + str(e))
        print('Looks like, there is some error in retrieving the data, Please try again or try with a different ticker.' )
        return
    newArt=news_df.groupby(['Date'], as_index = False).agg({'Summary': ','.join})
    return newArt


# In[205]:


def cleanTxt(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
    #text = re.sub(' ', '', text)
    text = re.sub('#', '', text) # Removing '#' hash tag
    text = re.sub('RT[\s]+', '', text) # Removing RT
    text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
    return text


# In[208]:


def getTweets(query,noOfTweets):
    query = query
    #As long as the query is valid (not empty or equal to '#')...
    if query != '':
        noOfTweet = noOfTweets
        if noOfTweet != '' :
            noOfDays = 1
            if noOfDays != '':
                #Creating list to append tweet data
                tweets_list = []
                now = dt.date.today()
                now = now.strftime('%Y-%m-%d')
                yesterday = dt.date.today() - dt.timedelta(days = int(noOfDays))
                yesterday = yesterday.strftime('%Y-%m-%d')
                for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query + ' lang:en since:' +  yesterday + ' until:' + now + ' -filter:links -filter:replies').get_items()):
                    if i > int(noOfTweet):
                        break
                    tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])

                #Creating a dataframe from the tweets list above 
                df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
                print(df)
                df["Text"] = df["Text"].apply(cleanTxt)
                df['DateNew'] = pd.to_datetime(df['Datetime']).dt.date
                df_new=df.groupby(['DateNew'], as_index = False).agg({'Text': ','.join})
                df_new.columns=['Date','Summary']
                return df_new


# In[209]:


def combineData(tweetText,ArtText):
    NewCombineDF=pd.concat([tweetText,ArtText])
    NewCombineDF['Date']=pd.to_datetime(NewCombineDF['Date'])
    NewCombineDF=NewCombineDF.groupby(['Date'], as_index = False).agg({'Summary': ','.join})
    NewCombineDF['Summary']=NewCombineDF['Summary'].str.cat(sep=' ')
    return NewCombineDF


# In[210]:


def polarity(NewCombineDF):
    #Assigning Initial Values
    positive = 0
    negative = 0
    neutral = 0
#Creating empty lists
#news_list = []
    polmap={}

#Iterating over the tweets in the dataframe
    for news in NewCombineDF['Summary']:
    #news_list.append(news)
        analyzer = SentimentIntensityAnalyzer().polarity_scores(news)
        neg = analyzer['neg']
        neu = analyzer['neu']
        pos = analyzer['pos']
        comp = analyzer['compound']
    #print(neg,pos,neu,comp)
        polmap.setdefault('Negative',[]).append(neg)
        polmap.setdefault('Positive',[]).append(pos)
        polmap.setdefault('Neutral',[]).append(neu)
        polmap.setdefault('Comp',[]).append(comp)
    polDF=pd.DataFrame(polmap)
    return polDF


# In[211]:


def finalData(NewCombineDF,PolDF):
    Pol=pd.concat([NewCombineDF,PolDF],axis=1)
    return Pol


# In[212]:


def model(Article,Tweet):
    ArtText=pd.DataFrame()
    ArtText=newsPerprocess(Article)
    tweetText=getTweets(Tweet,1000)
    NewCombineDF=combineData(tweetText,ArtText)
    poldf=polarity(NewCombineDF)
    final=finalData(NewCombineDF,poldf)
    return final


# In[213]:


# Initalise the Flask app
import pickle
app = Flask(__name__)
poldf=pd.DataFrame()


# In[214]:


@app.route('/')
def index():
    return render_template('base.html')

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or                 request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            #flash('You were successfully logged in')
            return redirect(url_for('predict'))
    return render_template('login.html', error=error)

@app.route('/pred',methods=['POST','GET'])
def predict():    
    if request.method == 'POST':
        article = request.form.get("Articles")
        print(article)
        tweets = request.form.get("Tweets")
        print(tweets)
        poldf=model(article,tweets)
        # load saved model
        with open('model_arima_pkl' , 'rb') as f:
            m_ar = pickle.load(f)
        # load saved model
        with open('rfc_pkl' , 'rb') as f:
            rfc_mod = pickle.load(f)
        print(poldf)
        positive=poldf[['Positive','Negative']]
        predicted_val=0.60*rfc_mod.predict(positive)+(1-0.60)*m_ar.predict(1)
        predicted_val
        return render_template('predict1.html', prediction_text='Your Predicted Stock Price is: {}'.format(predicted_val))
    return render_template('predict1.html')
if __name__ == "__main__":
    app.run()


