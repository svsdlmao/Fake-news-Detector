"""Baseline fake news classifier: TF-IDF + Logistic Regression."""
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'models')

def preprocess_text(text):
    """Lowercase, remove special chars, remove stopwords, lemmatize."""
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return ' '.join(tokens)

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)

    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    if len(train_df) == 0 or len(test_df) == 0:
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

    print("Preprocessing text...")
    X_train = train_df['text'].apply(preprocess_text)
    X_test = test_df['text'].apply(preprocess_text)
    y_train = train_df['label']
    y_test = test_df['label']

    print("Fitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print("Training Logistic Regression...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, 'baseline.pkl')
    joblib.dump({'model': model, 'vectorizer': vectorizer}, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    main()
