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
import utils
from jinja2 import Environment, FileSystemLoader
import mistune
from nltk.tokenize import word_tokenize


DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(DIR))
index_template = env.get_template('index_template.html')
stop_words = set(stopwords.words('english'))


parser = argparse.ArgumentParser(description="")
parser.add_argument('--src', '-i', type=str, help="input")
parser.add_argument('--out', '-o', default="index.html", type=str, help="input")
args = parser.parse_args()


def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]  # Remove punctuation and numbers
    tokens = [word for word in tokens if word not in stop_words and len(word)>=3]  # Remove stop words
    return tokens


INVERTED_INDEX = defaultdict(list)
DOCUMENT_INDEX=defaultdict(dict)
for doc in Path(args.src).glob("*.md"):
    metadata, content = utils.read_note(doc)
    prefix = f"[{metadata['index']}] " if metadata['index'] else ''

    doc_id = metadata['index'] if metadata['index'] else str(doc)

    terms = metadata["tags"].copy()
    terms.extend(preprocess_text(metadata['title']))
    terms.extend(preprocess_text(content))
    terms = list(set(terms))


    DOCUMENT_INDEX[doc_id] = {"uri": str(doc), "terms": terms, "metadata": metadata, "content": mistune.html(content)}

    for term in terms:
        INVERTED_INDEX[term].append(doc_id)

rendered_template = index_template.render(INVERTED_INDEX=INVERTED_INDEX, DOCUMENT_INDEX=DOCUMENT_INDEX)
print(f"Index size {len(INVERTED_INDEX)}")
with open(args.out,"w") as G:
    G.write(rendered_template)
            
