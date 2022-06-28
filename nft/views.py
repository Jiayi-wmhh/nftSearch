from ast import keyword
from urllib import response
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from urllib.request import urlopen, Request
import requests
import re
from requests.structures import CaseInsensitiveDict
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import json
from datetime import date,timedelta
from dateutil.relativedelta import *
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd                        
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Create your views here.

def search(request):
    return render(request,"nft/search.html")

def result(request):
    keyword = request.POST.get('keyword')
    res = []
    # twitter
    num_twitter = 100
    # change bearer token when the company account is created
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAM48aAEAAAAAi%2FLi%2ByJN40pC0y39uAGACG8joMw%3DWSvLjUQofW6rPSZoNaC9QWdJQfXy8EtTWdaUSIFePc4VWyT4mP"
    url = "https://api.twitter.com/2/tweets/search/recent?query="+keyword+"&max_results="+str(num_twitter)
    # add headers information to get request
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + bearer_token


    resp = requests.get(url, headers=headers).json()
    data = resp["data"]
    tweets = []

    for i in range(len(data)):
        parsed_tweet =[]
        parsed_tweet.append(keyword)
        tweet = data[i]["text"]
        parsed_tweet.append(tweet)
        tweets.append(parsed_tweet)

    columns = ['keyword','text']
    df = pd.DataFrame(tweets,columns=columns)
    vader = SentimentIntensityAnalyzer()
    # Iterate through the headlines and get the polarity scores using vader
    scores = df['text'].apply(vader.polarity_scores).tolist()
    # Convert the 'scores' list of dicts into a DataFrame
    scores_df = pd.DataFrame(scores)
    # Join the DataFrames of the news and the list of dicts
    df = df.join(scores_df, rsuffix='_right')
    result = df.to_json(orient = "records")

    weight_sum = 0
    for i in range(df.shape[0]):
        weight_sum += df["compound"][i] / df.shape[0]
    print(weight_sum)

    result_json = json.dumps(result)
    res.append(result_json)
   
   # Google search part
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[keyword])
    related_queries = pytrend.related_queries()

    #print(related_queries[keyword])

    top_list = []
    for i in range(related_queries[keyword]["top"].shape[0]):
        top_list.append(related_queries[keyword]["top"].loc[i,"query"])

    #print(top_list)
    res.append(top_list)

    text = " ".join(top_list)
    word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
    plt.figure()
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./nftSearch/nftSearch/static/top_search")

    rising_list = []
    for i in range(related_queries[keyword]["rising"].shape[0]):
        rising_list.append(related_queries[keyword]["rising"].loc[i,"query"])

    #print(rising_list)
    res.append(rising_list)

    text = " ".join(rising_list)
    word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./nftSearch/nftSearch/static/rising_search")

    related_topic = pytrend.related_topics()
    rising_topic_list = []
    for i in range(related_topic[keyword]["rising"].shape[0]):
        rising_topic_list.append(related_topic[keyword]["rising"].loc[i,"topic_title"])
    #print(rising_topic_list)
    res.append(rising_topic_list)

    text = " ".join(rising_topic_list)
    word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./nftSearch/nftSearch/static/related_topic_search")

    return render(request,"nft/result.html",{ "Result":res }) 
