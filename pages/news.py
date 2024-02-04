import nltk

nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')

from datetime import date
import dateutil.parser
import feedparser as fp
import newspaper
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import streamlit as st
from wordcloud import WordCloud

class NewsScraper:
    def __init__(self, sources, news_date=date.today()):
        self.news_date = news_date
        self.sources = sources

    def scrape(self, num_articles=None):
        articles_list = []
        analyzer = SentimentIntensityAnalyzer()

        for source, content in self.sources.items():
            for url in content['rss']:
                d = fp.parse(url)
                for entry in d.entries:
                    article = {}
                    if num_articles is not None and len(articles_list) >= num_articles:
                        break

                    if hasattr(entry, 'published'):
                        article_date = dateutil.parser.parse(getattr(entry, 'published'))
                        if article_date.date() == self.news_date:
                            try:
                                content = newspaper.Article(entry.link)
                                content.download()
                                content.parse()
                                content.nlp()

                                sentiment_scores = analyzer.polarity_scores(content.text)

                                article['source'] = source
                                article['url'] = entry.link
                                article['title'] = content.title
                                article['summary'] = content.summary
                                article['date'] = article_date.strftime('%Y-%m-%d')
                                article['sentiment'] = sentiment_scores['compound']

                                articles_list.append(article)
                            except Exception as e:
                                print(e)
                                print('continuing...')

        return articles_list

# Add the sources of the news
sources = {
    "CNN": {"rss": ["http://rss.cnn.com/rss/cnn_latest.rss"]},
    "CBN": {"rss": ["https://www1.cbn.com/rss-cbn-articles-cbnnews.xml",
                    "https://www1.cbn.com/rss-cbn-news-finance.xml"]},
    "Financial Times":
  	      {"rss": ["https://www.ft.com/rss/home/uk"]},
    "MarketWatch":
          {"rss": ["http://feeds.marketwatch.com/marketwatch/topstories/",
		             "http://feeds.marketwatch.com/marketwatch/marketpulse/"]},
    "Fortune":
  	      {"rss": ["https://fortune.com/feed"]},
    "BBC Business":
          {"rss": ["https://feeds.bbci.co.uk/news/world/rss.xml"]},
    "The Economists":
          {"rss": ["https://www.economist.com/finance-and-economics/rss.xml"]},
    "CNBC":
          {"rss": ["https://www.cnbc.com/id/100727362/device/rss/rss.html"]},
    "Wall Street Journal":
          {"rss": ["https://www.wsj.com/news/rss-news-and-feeds"]}
}

# Create a Streamlit web app
st.set_page_config(layout='wide', initial_sidebar_state='collapsed', page_title="News Sentiment Dashboard", page_icon="📰")
st.title("News Sentiment Analysis Dashboard")
st.write("Let's explore the sentiment analysis of today's news.")

# Sidebar for user input
st.sidebar.header('Explore Today\'s News')
num_articles = st.sidebar.slider('Number of Articles', 10, 50, 100)

# Instantiate the NewsScraper
news_scraper = NewsScraper(sources)

# Scrape news data
news_data = news_scraper.scrape(num_articles)

# Display sentiment analysis metrics
with st.container():
    st.markdown('### Big Numbers')
    col1, col2 = st.columns(2)
    st.metric("Average Sentiment", round(pd.DataFrame(news_data)['sentiment'].mean(), 2))
    st.metric("Number of Articles processed", len(news_data))
    st.write("---")


# Word Cloud
all_titles_str = ' '.join(pd.DataFrame(news_data)['title'])
with st.container():
    st.write("---")
    st.markdown('### Wordcloud')

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_titles_str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_axis_off()

    st.pyplot(fig)

# Display news data in a DataFrame
with st.container():
    st.write("---")
    st.markdown('### Data')
    st.markdown("Transparency and open sources are crucial to be well informed. Here you won't have just our analysis, you have easy access to our data too!")
    st.dataframe(pd.DataFrame(news_data))
