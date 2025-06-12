from collections import Counter
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.feature_extraction.text import CountVectorizer


def cluster_and_extract_keywords(comments: list[str], top_n: int=5):
    model = SentenceTransformer("bots/model/minilm_english_finetuned")
    kw_model = KeyBERT(model)
    if not comments:
        return {}

    embeddings = model.encode(comments)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)

    cluster_keywords = {}
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue
        cluster_comments = [c for c, l in zip(comments, labels) if l == cluster_id]
        joined_text = " ".join(cluster_comments)
        keywords = kw_model.extract_keywords(joined_text, top_n=top_n)
        cluster_keywords[cluster_id] = [k[0] for k in keywords]

    if not cluster_keywords:
        vectorizer = CountVectorizer(stop_words="english")
        X = vectorizer.fit_transform(comments)
        sum_words = X.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        fallback_keywords = [w for w, _ in words_freq[:top_n]]
        cluster_keywords = {"fallback": fallback_keywords}

    return cluster_keywords