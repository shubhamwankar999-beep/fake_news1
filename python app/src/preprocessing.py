import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# NLTK Downloads
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def clean_text(text):
    """
    Cleans the input text for NLP tasks.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercasing
    text = text.lower()
    
    # Removing punctuation
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    
    # Removing numbers
    text = re.sub(r'\d+', '', text)
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Removing stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    return " ".join(tokens)

def prepare_data(df):
    """
    Preprocess the entire dataframe.
    """
    import pandas as pd
    # Combining title and text for better context
    df['combined_content'] = df['title'].fillna('') + " " + df['text'].fillna('')
    
    # Applying cleaning
    df['cleaned_content'] = df['combined_content'].apply(clean_text)
    
    return df

