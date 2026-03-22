from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import streamlit as st
import os


@st.cache_resource
def train_career_model():

    # 🔥 correct path
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "career_dataset.csv")

    df = pd.read_csv(file_path)

    X = df["skills"]
    y = df["role"]

    vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=500)
    X_vec = vectorizer.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vec, y)

    return model, vectorizer


def predict_role(model, vectorizer, user_skills):

    text = " ".join(user_skills)

    vec = vectorizer.transform([text])

    prediction = model.predict(vec)
    probs = model.predict_proba(vec)

    confidence = max(probs[0]) * 100

    return prediction[0], confidence
