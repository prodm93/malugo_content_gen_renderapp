import nltk
nltk.download('stopwords')
nltk.download('punkt')
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from db_utils import *

def remove_string_special_characters(s):
    # removes special characters with ' '
    stripped = re.sub('[^a-zA-z\s]', '', s)
    stripped = re.sub('_', '', stripped)
    stripped = re.sub('``', '', stripped)

    # Change any white space to one space
    stripped = re.sub('\s+', ' ', stripped)

    # Remove start and end white spaces
    stripped = stripped.strip()
    if stripped != '':
            return stripped.lower()

def remove_stopwords(posts):       
    # Stopword removal
    stop_words = set(stopwords.words('english'))
    your_list = ['title', 'opening', 'objective', 'purpose', 'main content',
                'engaging hook', 'example', 'conclusion', 'call-to-action', 'like',
                'share', 'follow', 'comments', 'comment', 'visit', 'click', 'slide',
                'content']
    posts_nostop = ''
    if len(posts) > 0:
        for txt in posts:
            for i, line in enumerate(txt):
                if txt is not None:
            #line = remove_string_special_characters(line)  
                    txt[i] = ' '.join([x for x in nltk.word_tokenize(line) if 
                                       ( x.lower() not in stop_words ) and ( x.lower() not in your_list )])
                    posts_nostop += txt[i]
    return [remove_string_special_characters(posts_nostop)]

def get_freq_terms(posts_nostop, num_terms, min_ngram, max_ngram):
    count_vectorizer = CountVectorizer(ngram_range=(min_ngram, max_ngram))
    try:
        X1 = count_vectorizer.fit_transform(posts_nostop)
        features = (count_vectorizer.get_feature_names_out())
        tfidf_vectorizer = TfidfVectorizer(ngram_range = (1,3))
        X2 = tfidf_vectorizer.fit_transform(posts_nostop)
        #scores = (X2.toarray())
        sums = X2.sum(axis = 0) 
        data1 = [] 
        for col, term in enumerate(features): 
            data1.append( (term, sums[0, col] )) 
        ranking = pd.DataFrame(data1, columns = ['term', 'rank']) 
        words = (ranking.sort_values('rank', ascending = False)) 
        return dict(zip(words['term'][:num_terms].tolist(), words['rank'][:num_terms].tolist()))
    except (ValueError, AttributeError) as e:
        return {}

client = get_client()
