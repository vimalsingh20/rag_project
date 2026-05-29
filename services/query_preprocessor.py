import re
import nltk 
nltk.download("stopwords")

from nltk.corpus import stopwords
nltk.download("wordnet")
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
     
def lowercase_text(text):
    return text.lower()

def remove_punctuation(text):
    cleaned_text = re.sub(
        r'[^\w\s]',
        '',
        text)
    return cleaned_text


STOP_WORDS = set(stopwords.words('english'))

def remove_stopwords(text):
    words = text.split()
    filtered_words = []
    for word in words:
        if word not in STOP_WORDS:
            filtered_words.append(word)
            
    return " ".join(filtered_words)    


lemmatizer = WordNetLemmatizer()
def lemmatize_text(text):
    words = text.split()
    lemmatized_words = []
    for word in words:
        lemmatized_words.append(
            lemmatizer.lemmatize(word)
        )
     
    return " ".join(
        lemmatized_words
    )    
    
def preprocess_query(text):
    text = lowercase_text(text)
    text = remove_punctuation(text)
    text = remove_stopwords(text)
    text = lemmatize_text(text)
    
    return text 