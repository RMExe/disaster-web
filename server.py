import flask
from newsapi import NewsApiClient
import pandas as pd 
import numpy as np 
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

#make flask app
app = flask.Flask(__name__)


# Init newsapi
# newsapi docs from here: https://newsapi.org/docs/client-libraries/python

#Insert appropriate API key here
newsapi = NewsApiClient(api_key='API_KEY_HERE')

#Load in model
with open("./modelpkl/model.pkl","rb") as fp:
    model = pickle.load(fp)

#Render home page with input form
@app.route('/')
def form():
    return flask.render_template("index.html")

#Take input form, query news sources, use model to filter to relevant articles
@app.route('/result', methods=['POST', 'GET'])
def make_news():
    #get form inputs
    result = flask.request.form
    q = result["q"]
    from_date = result["from_date"]
    to_date = result["to_date"]

    #query newsAPI
    if from_date == "" and to_date == "":
        articles = newsapi.get_everything(q=q,page_size=100)
    elif to_date == "":
        try:
            articles = newsapi.get_everything(q=q,page_size=100,from_param=from_date)
        except:
            print("Date was likely out of range")
            articles = newsapi.get_everything(q=q,page_size=100)
    elif from_date == "":
        try:
            articles = newsapi.get_everything(q=q,page_size=100,to=to_date)
        except:
            print("Date was likely out of range")
            articles = newsapi.get_everything(q=q,page_size=100)
    else:
        try:
            articles = newsapi.get_everything(q=q,page_size=100,from_param=from_date,to=to_date)
        except:
            print("Date was likely out of range")
            articles = newsapi.get_everything(q=q,page_size=100)
    
    article_df = pd.DataFrame(articles["articles"])

    #filter results to relevant
    X = article_df["title"]
    article_df["label"] = model.predict(X)
    article_df = article_df[article_df["label"] == 1]

    #pass to results page
    article_dict = list(article_df.T.to_dict().values())
    return flask.render_template("result.html", article_dict=article_dict)

if __name__ == '__main__':

	HOST = '127.0.0.1'
	PORT = 4000
	app.run(HOST, PORT)