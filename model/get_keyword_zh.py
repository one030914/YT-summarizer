from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import hdbscan

# 用 multilingual 模型，支援中文
model = SentenceTransformer("minilm_chinese_finetuned")
kw_model = KeyBERT(model)

def extract_short_keywords(comments, segmented_comments, top_n=5, max_keyword_length=3, min_cluster_size=2):
    # 如果评论数小于最小群组大小，直接返回空字典
    if len(comments) < min_cluster_size:
        return {}

    # 確保所有的分詞結果都是字符串類型
    segmented_comments = [str(comment) for comment in segmented_comments]

    # 向量化
    embeddings = model.encode(comments)

    # 使用 HDBSCAN 進行聚類
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)

    # 儲存每個簇的關鍵字
    cluster_keywords = {}

    # 遍歷每個簇
    for cluster_id in set(labels):
        if cluster_id == -1:  # 跳過噪聲點
            continue

        # 對於每個簇，提取該簇的評論
        cluster_comments = [c for c, l in zip(segmented_comments, labels) if l == cluster_id]

        # 合併該簇內的所有評論
        joined_text = " ".join(cluster_comments)

        # 用 KeyBERT 提取關鍵字
        keywords = kw_model.extract_keywords(joined_text, top_n=top_n, stop_words=None)

        # 過濾掉過長的關鍵字，僅保留長度小於等於 max_keyword_length 的關鍵字
        short_keywords = [kw[0] for kw in keywords if len(kw[0]) <= max_keyword_length]

        # 儲存該簇的關鍵字
        cluster_keywords[cluster_id] = short_keywords

    return cluster_keywords

