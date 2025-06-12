from sentence_transformers import SentenceTransformer, util, InputExample
import pandas as pd
from itertools import combinations
from tqdm import tqdm

# 初始化兩個模型
text2vec_model = SentenceTransformer("shibing624/text2vec-base-multilingual")
mini_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 中英兼容長度判斷
def is_valid_length(text, min_len=5):
    text = text.strip()
    if any('\u4e00' <= ch <= '\u9fff' for ch in text):
        return len(text) >= min_len
    return len(text.split()) >= min_len

# 嵌入方法（不同模型）
def encode_text2vec(text):
    return text2vec_model.encode(text.strip(), convert_to_tensor=True)

def encode_mini(text):
    return mini_model.encode(text.strip(), convert_to_tensor=True)

# 載入留言資料
df = pd.read_csv("./data/datasets/datasets/English.csv")
comments = df["清理後留言"].dropna().astype(str).tolist()
comments = [c for c in comments if len(c) >= 2]

# 建立 text2vec 向量
print("🔄 建立 text2vec 向量...")
text2vec_embeds = {text: encode_text2vec(text) for text in tqdm(comments)}

# 建立 MiniLM 向量
print("🔄 建立 MiniLM 向量...")
mini_embeds = {text: encode_mini(text) for text in tqdm(comments)}

# 雙模型打分 + 篩選條件
examples = []
for s1, s2 in tqdm(combinations(comments, 2), desc="🔍 雙模型相似度計算"):
    if not is_valid_length(s1) or not is_valid_length(s2):
        continue

    score1 = util.cos_sim(text2vec_embeds[s1], text2vec_embeds[s2]).item()
    score2 = util.cos_sim(mini_embeds[s1], mini_embeds[s2]).item()

    # 雙模型都要達門檻才保留（你可自行調整）
    if 0.1 <= score1 <= 0.95 and 0.1 <= score2 <= 0.95:
        avg_score = round((score1 + score2)/2, 4)
        examples.append({
            "sentence1": s1,
            "sentence2": s2,
            "avg_score": avg_score
        })

# 輸出
df_out = pd.DataFrame(examples)
output_path = "./data/datasets/datasets/MiniLM_english.csv"
df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"✅ 已儲出 {len(df_out)} 筆雙模型句子對至：{output_path}")
