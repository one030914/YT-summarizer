from model.get_keyword_zh import extract_short_keywords
import pandas as pd
from collections import Counter
# 讀取 CSV 文件
df = pd.read_csv("data/datasets/english/gNNox-nemsY.csv")

# 讀取留言和分詞後的留言
segmented_comments = df['結巴斷詞'].tolist()
comments = df['清理後留言'].tolist()

keywords = extract_short_keywords(comments,segmented_comments)
# 輸出關鍵字
print(keywords)

# 把所有關鍵字丟進一個列表
all_keywords = sum(keywords.values(), [])  # 扁平化 list of lists
top_keywords = Counter(all_keywords).most_common(5)

for word, count in top_keywords:
    print(f"{word} ({count} 次)")
