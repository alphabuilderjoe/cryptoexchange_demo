"""
Example python app with the Flask framework: http://flask.pocoo.org/
"""

from os import environ

from flask import Flask, request
from flask import render_template



# //////////////////////////////News Feed//////////////////////////////


#google

import requests
from bs4 import BeautifulSoup
import pandas as pd

import time
import unicodedata


google_url = 'https://news.google.com/news/search/section/q/bitcoin'

content = requests.get(google_url).text
soup = BeautifulSoup(content,"html.parser")

def news_scrap():
    global g_df
    g_news_list=[]
    g_url_list=[]
    g_timestamp_list=[]

    a_tags = soup.find_all("a", {'class':"nuEeue hzdq5d ME7ew"})
    for a_tag in a_tags:
        

        raw_url = a_tag.get("href").encode("utf-8").decode("utf-8")
        new_url = "<a href='{}'>Link</a>".format(raw_url)
        g_url_list.append(new_url)
        #g_url_list.append(a_tag.get("href").encode("utf-8").decode("utf-8"))
        content =a_tag.text
#         print(content)
        #.encode("utf-8")
        title =unicodedata.normalize('NFKD', content).encode('ascii','ignore').decode("utf-8")
        g_news_list.append(title)


    span_tags = soup.find_all("span", {'class':'d5kXP YBZVLb'})
    for span_tag in span_tags:
        g_timestamp_list.append(span_tag.get_text().split(" ago")[0].encode("utf-8").decode("utf-8"))

    pd.set_option('display.max_colwidth', -1)
    g_df = pd.DataFrame(data = list(zip(g_news_list,g_url_list,g_timestamp_list)), columns=["Title", "URL", "Timestamp"])

    print(g_df)
    return g_df
# # to get live feed
# while True:
#     print(news_scrap())
#     time.sleep(8)
    
#news_scrap()

#g_df.to_html("news.html")

# //////////////////////Flask///////////////////////////////////////



app = Flask(__name__)


@app.route('/')
def indexshortcut():
    news_df = news_scrap()  

    return render_template('index.html',tables=[news_df.to_html(escape=False)],
    titles = ['na', ' '])


@app.route('/news')
def index():
    news_df = news_scrap()  

    return render_template('news.html',tables=[news_df.to_html(escape=False)],
    titles = ['na', 'Bitcoin News'])


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5010.
    port = int(environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port)














