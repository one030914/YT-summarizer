from model.get_keywords_en import cluster_and_extract_keywords
import pandas as pd
from collections import Counter
df = pd.read_csv("./data/datasets/english/VBhOumCHKac.csv")
comments = df['清理後留言'].tolist()
keywords = cluster_and_extract_keywords(comments)
 
print(keywords)
# 把所有關鍵字丟進一個列表
all_keywords = sum(keywords.values(), [])  # 扁平化 list of lists
top_keywords = Counter(all_keywords).most_common(5)

for word, count in top_keywords:
    print(f"{word} ({count} 次)")