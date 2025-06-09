import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import torch

# 讀取 CSV（請確認路徑與檔名正確）
df = pd.read_csv("./data/datasets/datasets/MiniLM_chinese.csv")

# 將每筆資料轉成 InputExample
train_examples = [
    InputExample(texts=[row['sentence1'], row['sentence2']], label=float(row['avg_score']))
    for _, row in df.iterrows()
]

# 建立 DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# 啟用 GPU（若有）
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)

# 使用 Cosine Similarity Loss 訓練
train_loss = losses.CosineSimilarityLoss(model)

# 開始訓練
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=10,
    output_path="./minilm_chinese_finetuned"
)