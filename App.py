import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
from googletrans import Translator
from googletrans import LANGUAGES
import io
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
nltk.download('punkt')
nltk.download('vader_lexicon')

st.set_page_config(page_title='NewsSaar: A Summarised News📰 Portal', page_icon='./Meta/newspaper.ico')

# Define supported languages
SUPPORTED_LANGUAGES = {
    lang_code: LANGUAGES[lang_code].capitalize() for lang_code in LANGUAGES
}

def fetch_news_search_topic(topic):
    site = 'https://news.google.com/rss/search?q={}'.format(topic)
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, use_column_width=True)


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    
    if sentiment['compound'] >= 0.1:
        return 'Positive'
    elif sentiment['compound'] <= -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def translate_summary(summary, target_language='en'):
    translator = Translator()
    try:
        translation = translator.translate(summary, dest=target_language)
        translated_summary = translation.text
        return translated_summary
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return "Translation Error"



def display_news(list_of_news, news_quantity):
    c = 0
    for index, news in enumerate(list_of_news):
        c += 1
      
        st.write('**({}) {}**'.format(c, news.title.text))
       
        # Set timeout for article download
        news_data = Article(news.link.text, timeout=10) 
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(f"Error: {e}")
        fetch_news_poster(news_data.top_image)

        with st.expander(news.title.text):
            st.markdown(
                '''<h6 style='text-align: justify;'>{}"</h6>'''.format(news_data.summary),
                unsafe_allow_html=True)
            st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))

            # Add a translation option here
            translation_widget_key = f"translation_{index}_{news.title.text}"
            supported_languages = list(SUPPORTED_LANGUAGES.keys())  # Get the list of supported language codes
            # Create a placeholder for the translated summary
            translated_summary_placeholder = st.empty()

            target_language = st.selectbox('Select Target Language', supported_languages, key=translation_widget_key, format_func=lambda x: SUPPORTED_LANGUAGES[x])
            
            if st.button("Translate Summary", key=f"translate_{index}"):
                if target_language != 'Select Language':
                    translated_summary = translate_summary(news_data.summary, target_language)
                    translated_summary_placeholder.markdown(
                        '''<h6 style='text-align: justify;'>{}"</h6>'''.format(translated_summary), 
                        unsafe_allow_html=True)
                else:
                    st.warning("Please select a target language before translating.")

          

        # Analyze sentiment and display
        sentiment = analyze_sentiment(news_data.summary)
        st.info(f"Sentiment: {sentiment}")
            
        st.success("Published Date: " + news.pubDate.text)

        if c >= news_quantity:
            break




def run():
    st.title("NewsSaar: A Summarised News📰")
    image = Image.open('./Meta/newsLogo.png')

    col1, col2, col3 = st.columns([3, 5, 3])

    with col1:
        st.write("")

    with col2:
        st.image(image, use_column_width=False)

    with col3:
        st.write("")
    category = ['--Select--', 'Trending News 🔥', 'Favourite Topics 💙', 'Search Topic 🔍']
    cat_op = st.selectbox('Select your Category', category)


    if cat_op == category[0]:
        st.warning('Please select Type!!')
    elif cat_op == category[1]:
        st.subheader("✅ Here is the Trending🔥 news for you")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news)
    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE',
                     'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(chosen_topic))
                display_news(news_list, no_of_news)
            else:
                st.error("No News found for {}".format(chosen_topic))

    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(user_topic.capitalize()))
                display_news(news_list, no_of_news)
            else:
                st.error("No News found for {}".format(user_topic))
        else:
            st.warning("Please write Topic Name to Search🔍")


run()


# ... streamlit run your_file_name.py
# .... http://localhost:8501/
