import re
import nltk

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# =========================================
# Lowercase
# =========================================

def lowercase_text(text):

    return text.lower()


# =========================================
# Remove Punctuation
# =========================================

def remove_punctuation(text):

    cleaned_text = re.sub(
        r'[^\w\s]',
        '',
        text
    )

    return cleaned_text


# =========================================
# Stopwords
# =========================================

STOP_WORDS = set(
    stopwords.words("english")
)


def remove_stopwords(text):

    words = text.split()

    filtered_words = []

    for word in words:

        if word not in STOP_WORDS:

            filtered_words.append(
                word
            )

    return " ".join(
        filtered_words
    )


# =========================================
# Lemmatization
# =========================================

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


# =========================================
# Query Preprocessing
# =========================================

def preprocess_query(text):

    # Safety check
    if text is None:

        return ""

    text = str(text).strip()

    # Empty question check
    if not text:

        return ""

    # Lowercase
    text = lowercase_text(
        text
    )

    # Remove punctuation
    text = remove_punctuation(
        text
    )

    # Remove stopwords
    text = remove_stopwords(
        text
    )

    # Lemmatization
    text = lemmatize_text(
        text
    )

    return text.strip()