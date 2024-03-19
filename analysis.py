import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag, RegexpParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def analyze_reviews(df):
    def tokenize_text(text):
        return word_tokenize(text)

    def remove_stopwords(tokens):
        stop_words = set(stopwords.words('english'))
        return [token for token in tokens if token.lower() not in stop_words]

    def pos_tagging(tokens):
        return pos_tag(tokens)

    def extract_noun_phrases(tagged_tokens):
        grammar = r"""
            NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
        """
        cp = RegexpParser(grammar)
        tree = cp.parse(tagged_tokens)
        noun_phrases = [' '.join([leaf[0] for leaf in subtree.leaves()])
                        for subtree in tree.subtrees() if subtree.label() == 'NP']
        return noun_phrases

    def remove_named_entities(text):
        doc = nlp(text)
        return ' '.join([token.text for token in doc if token.ent_type_ == ''])

    analyzer = SentimentIntensityAnalyzer()
    df['tokens'] = df['review_content'].apply(tokenize_text)
    df['tokens'] = df['tokens'].apply(remove_stopwords)
    df['tagged_tokens'] = df['tokens'].apply(pos_tagging)
    df['noun_phrases'] = df['tagged_tokens'].apply(extract_noun_phrases)
    df['review_content'] = df['review_content'].apply(remove_named_entities)
    tfidf_matrix, feature_names = calculate_tfidf(df['review_content'].tolist())
    cosine_similarities = calculate_cosine_similarity(tfidf_matrix)
    df['cosine_similarity'] = cosine_similarities.tolist()
    df['sentiment_score'] = df['review_content'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

    def sentiment_category(score):
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        else:
            return "neutral"
    df['review_category'] = df['sentiment_score'].apply(sentiment_category)

    return df  # Or modify as needed to return the results in your preferred format

def calculate_tfidf(texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names()
    return tfidf_matrix, feature_names

def calculate_cosine_similarity(tfidf_matrix):
    return cosine_similarity(tfidf_matrix, tfidf_matrix)
