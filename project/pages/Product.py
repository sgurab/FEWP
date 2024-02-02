import streamlit as st
import pandas as pd
import numpy as np
from ntscraper import Nitter
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import plotly.express as px 

########################################
# model
## scraper = Nitter()

## def get_tweets(name, modes, no, min_likes=100):
 #   tweets = scraper.get_tweets(name, mode=modes, number=no)
#    analyzer = SentimentIntensityAnalyzer()
 #   final_tweets = []
#
 #   for tweet in tweets['tweets']:
 #       # Adiciona apenas tweets com mais de 100 likes
 #       if tweet['stats']['likes'] >= min_likes:
 #           data = [tweet['link'], tweet['text'], tweet['date'], tweet['stats']['likes'], tweet['stats']['comments']]
#
 #           # Formata a data para dd/mm/aa
 #           date_str = tweet['date'].split(' · ')[0]
 #           formatted_date = datetime.strpatime(date_str, '%b %d, %Y').strftime('%d/%m/%y')
 #           data.append(formatted_date)
#
#            # Calculate sentiment scores
#            sentiment_scores = analyzer.polarity_scores(tweet['text'])
#            data.append(sentiment_scores['compound'])  # Using compound score as overall sentiment
#            final_tweets.append(data)
#
#    data = pd.DataFrame(final_tweets, columns=['link', 'text', 'date', 'no_likes', 'no_tweets', 'formatted_date', 'sentiment'])
#    return data

#df = get_tweets('Financial Markets','term',100)
########################################

# loading the data and adjusting the types of columns (Prophylactic measure)
df = pd.read_csv('/Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/output.csv')
df_news = pd.read_csv('/Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/news.csv')


df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
df['no_likes'] = pd.to_numeric(df['no_likes'], errors='coerce')
df['no_tweets'] = pd.to_numeric(df['no_tweets'], errors='coerce')

df_news['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')

# creating a unique dataframe -> we'll need a function to do it

# general for the app
st.set_page_config(layout='wide', initial_sidebar_state='expanded', page_title="FEWP Sentiment Dashboard",page_icon="📈")

# sidebar
with open('/Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Dashboard `MVP`')

st.sidebar.subheader('Filters')
selected_name = st.sidebar.text_input("What are you searching for?") 
selected_mode = st.sidebar.selectbox('Type of search', ('term', 'hashtag','name')) 
selected_no = st.sidebar.number_input("Pick a number", 0, 10000)


st.sidebar.markdown('''
---
Created by [Bruno](https://www.linkedin.com/in/brunohsgura//), [Bora](https://youtube.com/dataprofessor/), [Kim](https://youtube.com/dataprofessor/).
''')

# page
st.title("Sentiment Analysis Dashboard")

with st.container():
    st.markdown('### Big Numbers')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("General Sentiment",round(np.mean(df['sentiment']),2))
    col2.metric("Likes", np.sum(df['no_likes']))
    col3.metric("Comments", np.sum(df['no_tweets']))
    #col3.metric("Tweets per day", 28)

with st.container():
    st.write("---")
    st.markdown('### Raw Data')
    st.markdown("Transparency and open sources are crucial to be well informed. Here you won't have just our analysis, you have easy access to our data too!")
    df_sorted = df.sort_values(by='no_likes', ascending=False)
    st.dataframe(df_sorted,use_container_width=True)

with st.container():
    st.write("---")
    st.markdown('### Plots')
    col1, col2 = st.columns(2)
    scatter_chart = px.scatter(
    df,
    x='no_likes',
    y='no_tweets',
    title='Gráfico de Dispersão Interativo',
    labels={'no_tweets': 'no_tweets', 'no_likes': 'no_likes'},
    hover_data=['no_likes', 'no_tweets']
)
    col1.plotly_chart(scatter_chart)
