from collections import Counter
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import hdbscan

def extract_short_keywords(token_lists: list[list[str]]) -> dict:
    model = SentenceTransformer("bots/model/minilm_chinese_finetuned")
    kw_model = KeyBERT(model)

    cluster_keywords = {}

    if not token_lists:
        return {}

    docs = [" ".join(tokens) for tokens in token_lists]
    embeddings = model.encode(docs)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)

    for cluster_id in set(labels):
        if cluster_id == -1:
            continue
        cluster_docs = [docs[i] for i, l in enumerate(labels) if l == cluster_id]
        joined = "。".join(cluster_docs)
        cluster_tokens = [token for i, l in enumerate(labels) if l == cluster_id for token in token_lists[i]]
        if not cluster_tokens:
            continue
        keywords = kw_model.extract_keywords(joined, candidates=cluster_tokens, top_n=5)
        cluster_keywords[cluster_id] = [k[0] for k in keywords]

    if not cluster_keywords:
        all_tokens = [t for group in token_lists for t in group]
        most_common = Counter(all_tokens).most_common(5)
        cluster_keywords = {"fallback": [w for w, _ in most_common]}

    return cluster_keywords