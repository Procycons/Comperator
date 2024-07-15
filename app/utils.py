import re
import random

import nltk 
nltk.download('stopwords')
from nltk.corpus import stopwords


nltk_lan_mapper = {
    'en': 'english',
    'de': 'german',
    'fr': 'french',
    'es':'spanish',
    'it': 'italian'
}


def normalize_text(text, languages):
    pattern = r'(?:https?://|www\.|[^\w.\s])'
    text = re.sub(pattern, '', text)
                                    
    # Remove stopwords from the text
    # stopwords = []
    # for lang in languages:
    #    sws = set(stopwords.words(lang))
    #    stopwords.append(sws)
    # text = ' '.join([word for word in text.split() if word.lower() not in stop_words])
    # logger.info(f"Text content cleaned (len: before={len(text_org)}, after={len(text)}).")
    return text


def sample_words(words, sample_size):
    # Take a random sample of words
    sample = random.sample(words, min(sample_size, len(words)))
    return sample