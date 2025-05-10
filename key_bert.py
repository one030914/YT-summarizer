import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np

# 留言資料
comments = [
    "I love this song so much!",
    "This video made me cry.",
    "Such a beautiful melody.",
    "Can't stop dancing to this beat!",
    "The singer's voice is amazing.",
    "The rhythm is very energetic!"
]

# 初始化語意模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(comments)

# 試不同群數，看誤差
sse = []
k_range = range(1, 10)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(embeddings)
    sse.append(kmeans.inertia_)  # inertia_ = 群內總誤差

# 畫圖
plt.plot(k_range, sse, marker='o')
plt.xlabel('群數 (K)')
plt.ylabel('總平方誤差 (SSE)')
plt.title('Elbow Method to Choose K')
plt.show()
