import hdbscan
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd  # 如果您的数据源是 pandas 数据框

# 載入 fine-tuned MiniLM 模型（請確認路徑正確）
model = SentenceTransformer("minilm_english_finetuned")
kw_model = KeyBERT(model)

def cluster_and_extract_keywords(comments, top_n=5, min_cluster_size=2):
    """
    傳入留言列表，輸出每個群組的關鍵字摘要
    Args:
        comments (List[str]): 一組留言（同影片）
        top_n (int): 每群關鍵字數
        min_cluster_size (int): HDBSCAN 最小群組大小

    Returns:
        Dict[int, List[str]]: 群組編號對應的關鍵字清單
    """
    # 如果评论数小于最小群组大小，直接返回空字典
    if len(comments) < min_cluster_size:
        return {}

    # 确保所有评论都是字符串类型，处理缺失值
    comments = [str(comment) if not pd.isna(comment) else "" for comment in comments]

    # 向量化评论
    embeddings = model.encode(comments)

    # 使用 HDBSCAN 聚类
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)

    # 聚类并提取关键字
    cluster_keywords = {}
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue  # 忽略噪声
        cluster_comments = [c for c, l in zip(comments, labels) if l == cluster_id]
        # 将所有评论拼接成一条长文本，确保所有项都是字符串类型
        joined_text = "。".join([str(comment) for comment in cluster_comments])
        # 使用 KeyBERT 提取关键词
        keywords = kw_model.extract_keywords(joined_text, top_n=top_n)
        cluster_keywords[cluster_id] = [kw[0] for kw in keywords]

    return cluster_keywords
