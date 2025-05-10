from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer

# 初始化語意模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 留言資料
comments = [
    "I love this song so much!",
    "This video made me cry.",
    "Such a beautiful melody.",
    "Can't stop dancing to this beat!",
    "The singer's voice is amazing.",
    "The rhythm is very energetic!",
    "I cried listening to this song.",
    "This song makes me so happy!",
    "The beat is so powerful!",
    "Her voice is so emotional and deep.",
    "This performance blew my mind!",
    "Absolutely stunning visuals.",
    "The lyrics are so relatable.",
    "I’ve listened to this 10 times today.",
    "This deserves more views!",
    "His vocals are on another level.",
    "The harmony is just perfect.",
    "Goosebumps every time I hear it.",
    "This reminds me of my childhood.",
    "Masterpiece!"
]

# 把留言轉向量
embeddings = model.encode(comments)

# ✅ 使用 HDBSCAN 聚類（自動找群數）
clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
labels = clusterer.fit_predict(embeddings)

# ✅ 印出結果
num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f"✅ HDBSCAN 自動找到 {num_clusters} 個群組")
print()

for comment, label in zip(comments, labels):
    group = f"群組 {label}" if label != -1 else "❌ 噪音"
    print(f"【{group}】 {comment}")