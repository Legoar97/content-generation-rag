# app/ml_model.py
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def train_model(texts, labels):
    preprocessed_texts = [preprocess_text(text) for text in texts]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(preprocessed_texts)
    model = SVC(kernel='linear')
    model.fit(X, labels)
    return vectorizer, model

def predict_fake_news(text, vectorizer, model):
    preprocessed_text = preprocess_text(text)
    X = vectorizer.transform([preprocessed_text])
    prediction = model.predict(X)
    return prediction[0]
