from collections import Counter,defaultdict
from pathlib import Path
import frontmatter, re, os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, regexp_tokenize
from nltk.stem import PorterStemmer

import math
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
import numpy as np
import argparse
from jinja2 import Environment, FileSystemLoader
import mistune
from nltk.tokenize import word_tokenize
import base64
import json


stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Define regular expression patterns for special tokens
    special_token_pattern = r'[@#]\w+'
    
    # Tokenize text using regular expression pattern and standard word tokenization
    tokens = regexp_tokenize(text, pattern=special_token_pattern) + word_tokenize(text)
    
    # Remove punctuation (while keeping special tokens)
    tokens = [token for token in tokens if token.isalnum() or re.match(special_token_pattern, token)]
    
    # Remove stop words
    tokens = [word for word in tokens if not (word in stop_words or  len(word)<3 or word.isdigit())]
    
    # Stemming
    # ps = PorterStemmer()
    # tokens = [ps.stem(word) for word in tokens]
    
    return tokens

# def preprocess_text(text):
#     tokens = word_tokenize(text.lower())
#     tokens = [word for word in tokens if word.isalpha()]  # Remove punctuation and numbers
#     tokens = [word for word in tokens if word not in stop_words and len(word)>=3]  # Remove stop words
#     return tokens

def encode_to_base64(input_string):
    encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def read_note(path):
    with open(path) as f:
        metadata, content = frontmatter.parse(f.read())
        return metadata, content

def doc_to_payload(doc):
    metadata, content = read_note(doc)
    doc_id = str(doc.name)
    terms = metadata["tags"].copy()
    terms.extend(preprocess_text(metadata['title']))
    terms.extend(preprocess_text(content))
    terms = list(set(terms))
    return {
        "uri": doc_id, 
        "terms": terms, 
        "metadata": metadata, 
        "content": encode_to_base64(mistune.html(content))
    }


if __name__ == "__main__":
    DIR = os.path.dirname(os.path.abspath(__file__))

    env = Environment(loader=FileSystemLoader(os.path.join(DIR,"templates")))
    index_template = env.get_template('index_template.html')
    app_template = env.get_template('app_template.js')

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--src', '-i', type=str, help="input")
    parser.add_argument('--out', '-o', default="assets", type=str, help="input")
    args = parser.parse_args()

    INVERTED_INDEX = defaultdict(list)
    DOCUMENT_INDEX=defaultdict(dict)
    for doc in Path(args.src).glob("*.md"):
        payload = doc_to_payload(doc)
        DOCUMENT_INDEX[payload["uri"]] = payload
        for term in payload["terms"]:
            INVERTED_INDEX[term].append(payload["uri"])

    DATA = {
        'documents': DOCUMENT_INDEX,
        'invertedIndex': INVERTED_INDEX
    }

    OUT_DIR = Path(args.out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_DIR/"ii_data.json","w") as G:
        json.dump(DATA, G)

    rendered_template = index_template.render(INVERTED_INDEX=INVERTED_INDEX, DOCUMENT_INDEX=DOCUMENT_INDEX)
    print(f"Index size {len(INVERTED_INDEX)}")

    with open(OUT_DIR/"ii_index.html","w") as G:
        G.write(rendered_template)

    rendered_template = app_template.render(INVERTED_INDEX=INVERTED_INDEX, DOCUMENT_INDEX=DOCUMENT_INDEX)

    with open(OUT_DIR/"ii_app.js","w") as G:
        G.write(rendered_template)
            
