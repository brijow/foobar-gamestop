import re
import nltk
#   Do:
    # >>> import nltk
    # >>> nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.util import ngrams
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# For Spacy:
#     pip install -U pip setuptools wheel
#     pip install -U spacy
#     python -m spacy download en_core_web_sm
#     or
#     conda install -c conda-forge spacy
#     python -m spacy download en_core_web_sm

import spacy as sp
nlps = sp.load('en_core_web_sm')
sid = SIA()

def text_processing(text):
    # Remove handlers
    text = str(text)
    text = re.sub('@[^\s]+', '', text)
    # Remove URLS
    text = re.sub(r"http\S+", "", text)
    # Remove all the special characters
    text = ' '.join(re.findall(r'\w+', text))
    # Remove all single characters
    text = re.sub(r'\s+[a-zA-Z]\s+', '', text)
    # Substituting multiple spaces with single space
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    return text

def entity_extraction(text):
    doc = nlps(text)
    return [chunk.text for chunk in doc.noun_chunks]

def sentilysis(text):
    return sid.polarity_scores(' '.join(re.findall(r'\w+', text.lower())))
