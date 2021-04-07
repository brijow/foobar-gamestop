import os
import numpy as np
import pandas as pd

from _reddit_data_processing import *
from ._base import get_or_create_raw_data_dir

DATA_DIR = get_or_create_raw_data_dir()
DATASET_NAME = "r_wallstreetbets_posts.csv"

def filter_submission():
    df = pd.read_csv(DATA_DIR + "raw/" + DATASET_NAME)

    # Arbitrary date selection : 
        # 1585699200 (Fri, 01 Apr 2020 00:00:00 GMT)
        # Gives 777164 Records
    df = df[df['created_utc'] >= 1585699200]

    # Arbitrary score selection :
        # Posts with score > 2 or < -2
        # Gives 39868 Records
    df = df[abs(df['score']) > 2] 

    # Title Text Preprocessing
    # df['title'] = df['title'].str.lower()
    df['title'] = df['title'].apply(text_processing)
    # df = df.dropna(subset=['title'])

    # Sentiment Analysis
    df['sentiments'] = df['title'].apply(sentilysis)
    df['Positive Sentiment']   = df['sentiments'].apply(lambda x: x['pos']+1*(10**-6)) 
    df['Neutral Sentiment']    = df['sentiments'].apply(lambda x: x['neu']+1*(10**-6))
    df['Negative Sentiment']   = df['sentiments'].apply(lambda x: x['neg']+1*(10**-6))    

    # Entity extraction - Noun Phrases
    df['tags'] = df['title'].apply(entity_extraction)

    # print(df.count())

    df.to_csv(DATA_DIR + "processed/" + DATASET_NAME)
    df['id'].to_csv(DATA_DIR + "processed/" + "ids_" + DATASET_NAME)

if __name__ == "__main__":
    filter_submission()
