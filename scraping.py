import streamlit as st
import time
import pandas as pd
import numpy as np
import praw
import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
from io import BytesIO
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('vader_lexicon')


def get_reddit_posts(search_term, no_posts, delay_seconds=2, sort_type='new'):
    reddit = praw.Reddit(client_id='yfNKzQkvSYry4HKSLyt18g',
                         client_secret='2FCneK8y0Wd8F0wCAj-mYmgxIgZuxg',
                         user_agent='fewp/v0')

    # Substituído a busca por subreddit.new por reddit.subreddit(search_term).search
    posts = reddit.subreddit('all').search(query=search_term, sort=sort_type, time_filter='all', limit=no_posts)

    final_posts = []

    for post in posts:
        data_point = [post.url, post.title, post.selftext, pd.to_datetime(post.created_utc, unit='s').strftime('%Y-%m-%d'), post.score, post.num_comments, post.subreddit.display_name]
        final_posts.append(data_point)

        # Adicione um atraso entre as solicitações
        time.sleep(delay_seconds)

    while len(final_posts) < no_posts:
        # Obtém o ID da última postagem recuperada
        last_post_id = final_posts[-1][0].split('/')[-1]
        # Faz uma nova solicitação com o parâmetro 'after' para paginar
        posts = reddit.subreddit('all').search(query=search_term, limit=no_posts - len(final_posts), params={'after': last_post_id})
        
        for post in posts:
            data_point = [post.url, post.title, post.selftext, pd.to_datetime(post.created_utc, unit='s').strftime('%Y-%m-%d'), post.score, post.num_comments, post.subreddit.display_name]
            final_posts.append(data_point)

            # Adicione um atraso entre as solicitações
            time.sleep(delay_seconds)

    # Garanta que tenhamos exatamente no_posts linhas
    data = pd.DataFrame(final_posts[:no_posts], columns=['link', 'title', 'text', 'date', 'score', 'num_comments', 'subreddit'])
    return data

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    processed_text = ' '.join(lemmatized_tokens)
    return processed_text

analyzer = SentimentIntensityAnalyzer()

def get_sentiment_compound(text):
    scores = analyzer.polarity_scores(text)
    return scores['compound']

# Função para classificar com base na soma de sentimentos
def classify_sentiment(sum_sentiment):
    if sum_sentiment > 0:
        return 1
    elif sum_sentiment < 0:
        return -1
    else:
        return 0

# Função para gerar o PDF
def generate_pdf(data):
    pdf_filename = "output.pdf"

    # Criar um buffer de bytes para o PDF
    pdf_buffer = BytesIO()

    # Criar um arquivo PDF usando o buffer
    c = canvas.Canvas(pdf_buffer)

    # Adicionar conteúdo ao PDF
    c.drawString(100, 750, "Meu Relatório em PDF")
    c.drawString(100, 730, "Outro texto aqui...")

    # Adicionar informações do DataFrame
    c.drawString(100, 710, "Dataframe:")
    df_table = data.to_string()
    c.drawString(100, 690, df_table)

    # Fechar o arquivo PDF
    c.save()

    # Salvar o buffer como um arquivo PDF
    pdf_buffer.seek(0)
    with open(pdf_filename, 'wb') as f:
        f.write(pdf_buffer.read())

    return pdf_filename


# Criar a página em si e seu comportamento
st.set_page_config(layout='wide', initial_sidebar_state='collapsed', page_title="FEWP Sentiment Dashboard",page_icon="📈")
# page
st.title("Reddit Sentiment Analysis Dashboard")

# Criar uma barra lateral para a entrada do usuário
st.sidebar.header('Lets sea whats going on')
search_term = st.sidebar.text_input('Term', 'finance')
no_posts = st.sidebar.slider('Sample Size', 1, 100, 50)
delay_seconds = st.sidebar.slider('Delay (sec)', 1, 10, 1)
sort_type = st.sidebar.selectbox('Sort Type', ['hot', 'new', 'top', 'rising'], index=1)

# Chame a função e armazene o DataFrame resultante
data = get_reddit_posts(search_term, no_posts, delay_seconds, sort_type)
data['title'] = data['title'].apply(preprocess_text)
data['text'] = data['text'].apply(preprocess_text)

# Aplique o método compound nas colunas 'title' e 'text'
data['sentiment_title'] = data['title'].apply(get_sentiment_compound)
data['sentiment_text'] = data['text'].apply(get_sentiment_compound)

# Criar uma coluna que contém a soma das colunas de sentimento
data['sentiment_sum'] = data['sentiment_title'] + data['sentiment_text']
# Aplicar a função para criar a coluna de classificação final
data['final_sentiment'] = data['sentiment_sum'].apply(classify_sentiment)

# Criar uma coluna que contém o sentimento como str
data['final_sent_str'] = data['final_sentiment'].astype(str)


# Extrair apenas a parte da data (sem o tempo)
data['date'] = pd.to_datetime(data['date']).dt.date

# big numbers
with st.container():
    st.markdown('### Big Numbers')
    col1, col2, col3 = st.columns(3)
    col1.metric("General Sentiment",round(np.mean(data['sentiment_sum']),2))
    col2.metric("AVG Score", round(np.mean(data['score']),2))
    col3.metric("AVG Comments", round(np.mean(data['num_comments']),2))

# boxplot e scatter
c1, c2 = st.columns((5,5))

with c1:
    st.markdown('### Box Plot Analysis')
    fig = go.Figure()

    # Adicionar caixa para o total de publicações com cor azul escura
    fig.add_trace(go.Box(y=data['score'], name='Total Posts', boxpoints='all', jitter=0.3, pointpos=-1.8, marker_color='#1f77b4'))

    # Definir a ordem de exibição e cores para os sentimentos
    sentiment_order = [1, 0, -1]
    sentiment_colors = ['#3498db', '#85c1e9', '#e74c3c']

    for sentiment in sentiment_order:
        subset = data[data['final_sentiment'] == sentiment]
        sentiment_label = 'Sentiment {}'.format(sentiment)
        fig.add_trace(go.Box(y=subset['score'], name=sentiment_label, boxpoints='all', jitter=0.3, pointpos=-1.8, marker_color=sentiment_colors[sentiment_order.index(sentiment)]))

    # Atualizar layout do boxplot
    fig.update_layout(title='Score Boxplot', showlegend=True, boxmode='group', boxgap=0.001, margin=dict(l=20))
    st.plotly_chart(fig)

with c2:
    st.write("---")
    fig = go.Figure()

    # Adicionar caixa para o total de publicações com cor azul escura
    fig.add_trace(go.Box(y=data['num_comments'], name='Total Posts', boxpoints='all', jitter=0.3, pointpos=-1.8, marker_color='#1f77b4'))

    # Definir a ordem de exibição e cores para os sentimentos
    sentiment_order = [1, 0, -1]
    sentiment_colors = ['#3498db', '#85c1e9', '#e74c3c']

    for sentiment in sentiment_order:
        subset = data[data['final_sentiment'] == sentiment]
        sentiment_label = 'Sentiment {}'.format(sentiment)
        fig.add_trace(go.Box(y=subset['num_comments'], name=sentiment_label, boxpoints='all', jitter=0.3, pointpos=-1.8, marker_color=sentiment_colors[sentiment_order.index(sentiment)]))

    # Atualizar layout do boxplot
    fig.update_layout(title='Comments Boxplot', showlegend=True, boxmode='group', boxgap=0.001, margin=dict(l=20))
    st.plotly_chart(fig)

# scatter plot
with st.container():
    st.write("---")
    st.markdown('### Data')
    st.markdown("Find out which sentiment is more relevant with a scatter plot:")
    fig = px.scatter(data, x="score", y="num_comments", color="final_sent_str",
                     title='Scatter Plot: Relevance',
                     color_discrete_map={"1": '#3498db', "0": '#85c1e9', "-1": '#e74c3c'})

    # Atualizar a legenda do gráfico de dispersão para combinar com o boxplot
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

# word cloud
all_titles_str = ' '.join(data['title'])
with st.container():
    st.write("---")
    st.markdown('### Wordcloud')

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_titles_str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_axis_off()

    st.pyplot(fig)

# sankey dyagram
total_posts = len(data)    
subreddit_counts = data['subreddit'].value_counts()
sentiment_counts = data['final_sentiment'].value_counts()

with st.container():
    st.write("---")
    st.markdown('### Sankey Diagram')
    # Criar um diagrama de Sankey
    color_mapping = {
    1: '#3498db',   # Cor para Sentiment 1
    0: '#85c1e9',  # Cor para Sentiment 0
    -1: '#e74c3c'    # Cor para Sentiment -1
    }

    label = list(data['subreddit'].unique()) + [f'Sentiment {sentiment}' for sentiment in sorted(data['final_sentiment'].unique())]
    source = [data['subreddit'].unique().tolist().index(subreddit) for subreddit in data['subreddit']]
    target = [len(data['subreddit'].unique()) + sorted(data['final_sentiment'].unique()).index(sentiment) for sentiment in data['final_sentiment']]
    value = [1] * len(data)

    node_colors = ['#ffffff'] * len(data['subreddit'].unique()) + [color_mapping[sentiment] for sentiment in sorted(data['final_sentiment'].unique())]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=label,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    # Atualizar o layout do gráfico
    fig.update_layout(title='Sankey Diagram')

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Imprimir o DataFrame
with st.container():
    st.write("---")
    st.markdown('### Data')
    st.markdown("Transparency and open sources are crucial to be well informed. Here you won't have just our analysis, you have easy access to our data too!")

    st.dataframe(data)

# Download button
st.title("Gerar PDF no Streamlit")
# Botão para gerar o PDF
if st.button("Gerar PDF"):
    # Chame a função de geração do PDF
    pdf_file = generate_pdf(data)
    # Gere um link de download para o arquivo PDF
    st.success(f"PDF gerado com sucesso: [Download PDF]({pdf_file})")

# streamlit run /Users/brunosgura/Documents/Graduação/Intercâmbio/FEWP/project/scraping.py --server.address 172.24.212.200 --server.port 8501
