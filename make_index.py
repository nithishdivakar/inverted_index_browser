from collections import Counter,defaultdict
from pathlib import Path
import frontmatter, re, os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import math
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
import numpy as np
import argparse
from jinja2 import Environment, FileSystemLoader
import mistune
from nltk.tokenize import word_tokenize
import base64
import json

DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(os.path.join(DIR,"templates")))
index_template = env.get_template('index_template.html')
app_template = env.get_template('app_template.js')
stop_words = set(stopwords.words('english'))


parser = argparse.ArgumentParser(description="")
parser.add_argument('--src', '-i', type=str, help="input")
parser.add_argument('--out', '-o', default="assets", type=str, help="input")
# parser.add_argument('--out', '-o', default="data.json", type=str, help="input")
# parser.add_argument('--out1', '-m', default="index.html", type=str, help="input")
# parser.add_argument('--out2','-p', default="app.js", type=str, help="input")
args = parser.parse_args()


def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]  # Remove punctuation and numbers
    tokens = [word for word in tokens if word not in stop_words and len(word)>=3]  # Remove stop words
    return tokens

def encode_to_base64(input_string):
    encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def read_note(path):
    with open(path) as f:
        metadata, content = frontmatter.parse(f.read())
        return metadata, content

INVERTED_INDEX = defaultdict(list)
DOCUMENT_INDEX=defaultdict(dict)
for doc in Path(args.src).glob("*.md"):
    metadata, content = read_note(doc)
    prefix = f"[{metadata['index']}] " if metadata['index'] else ''

    # doc_id = metadata['index'] if metadata['index'] else str(doc)
    doc_id = str(doc.name)

    terms = metadata["tags"].copy()
    terms.extend(preprocess_text(metadata['title']))
    terms.extend(preprocess_text(content))
    terms = list(set(terms))


    DOCUMENT_INDEX[doc_id] = {"uri": doc_id, "terms": terms, "metadata": metadata, "content": encode_to_base64(mistune.html(content))}

    for term in terms:
        INVERTED_INDEX[term].append(doc_id)

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
            
