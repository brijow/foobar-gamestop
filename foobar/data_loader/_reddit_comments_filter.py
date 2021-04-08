import os
import numpy as np
import pandas as pd

from _reddit_data_processing import *
from ._base import get_or_create_raw_data_dir

DATA_DIR = get_or_create_raw_data_dir()
DATASET_NAME = "wsb_comments_raw.csv"

SUB_IDS = pd.read_csv(DATA_DIR + "processed/" + "ids_" + "r_wallstreetbets_posts.csv")
LINK_IDS = "t3_" + SUB_IDS['id'].astype(str)
COMM_IDS = "t1_" + SUB_IDS['id'].astype(str)
LOOKUPS = pd.concat([SUB_IDS['id'], COMM_IDS, LINK_IDS])
LOOKUPS= set(LOOKUPS)

def filter_comments():
    chunksize = 50000
    chunkcounter = 0
    for df in pd.read_csv(DATA_DIR + "raw/" + DATASET_NAME, chunksize=chunksize):

        df = df.drop(columns=['author_flair_background_color', 
        'author_flair_css_class', 'author_flair_richtext',
        'author_flair_template_id', 'author_flair_text',
        'author_flair_text_color', 'author_flair_type',
        'author_patreon_flair', 'author_premium', 
        'awarders', 'send_replies', 'media_metadata'])
        # Same as Submissions - Arbitrary date selection : 
            # 1585699200 (Fri, 01 Apr 2020 00:00:00 GMT)
            # Gives 777164 Records
        df = df[df['created_utc'].apply(lambda x: str(x).isdigit())]
        df = df[df['created_utc'] >= 1585699200]

        # LOOK-UP FOR Existing submissions
        df = df[df['link_id'].isin(LOOKUPS)]

        # Title Text Preprocessing
        df['body'] = df['body'].apply(text_processing)
        df = df.dropna(subset=['body'])

        # Sentiment Analysis
        df['sentiments'] = df['body'].apply(sentilysis)
        df['Positive Sentiment']   = df['sentiments'].apply(lambda x: x['pos']+1*(10**-6)) 
        df['Neutral Sentiment']    = df['sentiments'].apply(lambda x: x['neu']+1*(10**-6))
        df['Negative Sentiment']   = df['sentiments'].apply(lambda x: x['neg']+1*(10**-6))    

        # Entity extraction - Noun Phrases
        df['tags'] = df['body'].apply(entity_extraction)

        print("Chunk ", chunkcounter)
        print(df.count())
        if not df.empty:
            df.to_csv(DATA_DIR + "processed/comment_chunks/_" + str(chunkcounter) + "_" + DATASET_NAME)
        chunkcounter += 1

if __name__ == "__main__":
    filter_comments()
