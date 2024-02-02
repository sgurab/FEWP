import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image

st.set_page_config(
    page_title="FEWP Sentiment Project",
    page_icon="📈",
    layout="wide",
)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottieurl("https://lottie.host/30a69606-11f6-4bdf-8371-7f9a8fd5df32/t2yoazbJ4n.json")
img_contact_form = Image.open("/Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/images/npl.png")
img_twitter = Image.open("/Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/images/tx.jpeg")

with st.container():
    st.title("FEWP Sentiment")
    st.write(
        "This application was made as a useful tool for busy students and any beginner in the financial markets to understand whats happening and,specially, what is *relevant*!"
    )
    st.write("[Learn More >](https://docs.google.com/document/d/1eojI3JhtzxqBNFDk9k5EO15k2YHdk49nWE2al9bg1t4/edit)")

st.sidebar.success("Select a page above.")

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("A platform to stay tuned with markets!")
        st.subheader("Here you will find:")
        st.write(
            """
            
            - news and articles from renowned vehicles
            - opinions and comments of analysts and specialists on social media
            - everything together and _simple_ with an NPL based sentiment analysis!
            
            """
        )
    
    with right_column:
        st_lottie(lottie_coding, height=200, key="coding")

with st.container():
    st.write("---")
    st.header("Our features")
    st.write("##")
    image_column, text_column = st.columns((1,2))
    with image_column:
        st.image(img_twitter, use_column_width=True)
    
    with text_column:
        st.subheader("Web Scraping")
        st.write(
            """
            Our data comes directely from the original sources, in other words, from twitter and the most reliable vehicles!
            """
        )

with st.container():
    image_column, text_column = st.columns((1,2))
    with image_column:
        st.image(img_contact_form, use_column_width=True)
    
    with text_column:
        st.subheader("NPL Based Sentment Analysis")
        st.write(
            """
            After the scraping process, we use a well known feature to set the sentiment of each new, Vader. Sentiment analysis is a natural language processing (NLP) technique used to determine the sentiment of a piece of text.
            """
        )
        st.write("[Learn More >](https://medium.com/@saikirankalidindi/a-comprehensive-guide-for-natural-language-processing-nlp-for-beginners-39faa26ad4d9)")
