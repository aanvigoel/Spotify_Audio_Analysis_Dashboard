import streamlit as st
import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_data():
    try:
        df = pkl.load(open("processed_df.pkl", "rb"))
    except OSError:
        df = pd.read_csv("processed_data.csv")
    finally:
        print("No processed data file found")
    return df


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_unique(df):
    num = df.nunique()
    return num


# @st.cache(suppress_st_warning=True, allow_output_mutation=True)
def data_describe(df, features, row):
    stats = df.drop(features, axis=1)
    table = stats.describe()
    table = table.drop(row, axis=0)
    return table


feature_explanations = {'danceability': '''Danceability describes how suitable a track is for dancing based on a 
                        combination of musical elements including tempo, rhythm stability, beat strength, and overall 
                        regularity. A value of 0.0 is least danceable and 1.0 is most danceable.''',
                        'acousticness': '''A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 
                    1.0 represents high confidence the track is acoustic. >= 0, <= 1''',
                        'instrumentalness': '''Predicts whether a track contains no vocals. "Ooh" and "aah" sounds 
                        are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". 
                        The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no 
                        vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence 
                        is higher as the value approaches 1.0.''',
                        'loudness': '''The overall loudness of a track in decibels (dB). Loudness values are averaged 
                        across the entire track and are useful for comparing relative loudness of tracks. Loudness is 
                        the quality of a sound that is the primary psychological correlate of physical strength (
                        amplitude). Values typically range between -60 and 0 db.''',
                        'speechiness': '''Speechiness detects the presence of spoken words in a track. The more 
                        exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 
                        the attribute value. Values above 0.66 describe tracks that are probably made entirely of 
                        spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and 
                        speech, either in sections or layered, including such cases as rap music. Values below 0.33 
                        most likely represent music and other non-speech-like tracks.''',
                        'tempo': '''The overall estimated tempo of a track in beats per minute (BPM). In musical 
                        terminology, tempo is the speed or pace of a given piece and derives directly from the 
                        average beat duration.''',
                        'valence': '''A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a 
                        track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), 
                        while tracks with low valence sound more negative (e.g. sad, depressed, angry). >= 0, <= 1 ''',
                        'energy': '''Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of 
                        intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, 
                        death metal has high energy, while a Bach prelude scores low on the scale. Perceptual 
                        features contributing to this attribute include dynamic range, perceived loudness, timbre, 
                        onset rate, and general entropy. '''
                        }

img = Image.open('spotify_logo.png')
st.set_page_config(page_title='Spotify Analytics Dashboard', page_icon=img, layout='wide')

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

'''st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)
'''
st.markdown(""" <style> .font {
font-size:40px; color:#5cb85c; font-family: "Proxima Nova"; font-weight:bold} 
</style> """, unsafe_allow_html=True)
st.markdown('<p class="font">Spotify Streaming Analytics Dashboard</p>', unsafe_allow_html=True)

df = load_data()

## Section 1: Dataset info
st.sidebar.header('Data Snippets', anchor='center')

num_unique = get_unique(df)
st.sidebar.write('Total no. of tracks analyzed:', num_unique['name'])
st.sidebar.write('Total no. of artists analyzed:', num_unique['artists'])

list_of_years = np.sort(df.year.unique())
st.sidebar.write('Tracks across years:', list_of_years[0], '-', list_of_years[-1])

st.sidebar.subheader('Choose Analysis:')
checkbox1 = st.sidebar.checkbox('Display Audio Feature Trends')
checkbox2 = st.sidebar.checkbox('Display Data Statistics')

st.sidebar.subheader('Audio Features')
st.sidebar.text('Mood:\nDanceability, Valence,\nEnergy, Tempo')
st.sidebar.text('Properties:\nLoudness, Speechiness,\nInstrumentalness')
st.sidebar.text('Context:\nAcousticness')

## Section 2: Feature Trends by Year
c1, c2 = st.columns(2)
select_year = c1.selectbox('Select Year', list_of_years)
df_year = df.query("year == @select_year")

list_of_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
                    'valence', 'tempo']

if checkbox1:
    st.subheader('Top Tracks per Audio Feature')
    select_feature = c2.selectbox('Select Feature', list_of_features)

    df_track = df_year.sort_values(by=select_feature, ascending=False)
    df_track_top = df_track.head(10)

    # Plotting top tracks for each feature category
    fig = px.bar(df_track_top, x=select_feature, y="name", hover_data=["artists"], text="name",
                 title='Top tracks for {} for in year {}'.format(select_feature, select_year))
    fig.update_xaxes(title_text=select_feature.capitalize())
    fig.update_yaxes(title_text="Track", showticklabels=False)
    fig.update_traces(marker_color='#d9534f', marker_line_color='rgb(0, 2, 1)', textposition="inside", textfont_size=35)
    fig.update_layout(title=dict(font_size=16, x=0.5), hoverlabel=dict(bgcolor="white", font_size=14),
                      xaxis=dict(showgrid=False), yaxis=dict(zeroline=False, showgrid=False))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("See feature explanation"):
        st.write(feature_explanations[select_feature])

## Section 3: Feature stats
exclude_features = ["mode", "key", "duration_ms", "year", "liveness"]
exclude_stats = ["25%", "50%", "std", "count"]

table_style = [
    dict(selector='td:hover',
         props=[('background-color', '#d9534f')]),
    dict(selector='.index_name',
         props='font-style: italic; color: darkgrey; font-weight:normal;'),
    dict(selector='th:not(.index_name)',
         props='background-color: #5cb85c; color: white;')
]

if checkbox2:
    st.subheader('Data Statistics by Year')
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    d1 = data_describe(df_year, exclude_features, exclude_stats)
    st.table(d1.style.set_table_styles(table_style))
