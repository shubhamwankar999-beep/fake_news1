import os
import sys

# Ensure the root directory is in sys.path so 'src' is importable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

import pandas as pd
from src.preprocessing import prepare_data
from src.bert_model import FakeNewsBERT
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

def train_baseline(df):
    print("Training baseline Logistic Regression model...")
    # Drop rows where 'cleaned_content' or 'label' is NaN
    df = df.dropna(subset=['cleaned_content', 'label'])
    
    tfidf = TfidfVectorizer(max_features=5000)
    X = tfidf.fit_transform(df['cleaned_content'])
    y = df['label']
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Save model and vectorizer
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/model.pkl')
    joblib.dump(tfidf, 'models/tfidf.pkl')
    print("Baseline model saved to models/model.pkl")

def train_bert(df):
    """
    BERT Training logic.
    For this demo, we'll mention it's a structural placeholder for full GPU training.
    """
    print("Initializing BERT model for training...")
    # full training loop logic using HuggingFace trainer here
    pass

if __name__ == "__main__":
    # Load sample data
    df = pd.read_csv('data/news.csv')
    
    # Preprocess
    df = prepare_data(df)
    
    # Train
    train_baseline(df)
    # train_bert(df) # Requires GPU and longer time
