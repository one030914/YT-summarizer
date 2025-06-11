import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, InputExample, losses, util
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt

df = pd.read_csv("./data/datasets/datasets/MiniLM_english.csv")
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_examples = [
    InputExample(texts=[row['sentence1'], row['sentence2']], label=float(row['avg_score']))
    for _, row in train_df.iterrows()
]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)

train_loss = losses.CosineSimilarityLoss(model)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=10,
    warmup_steps=10,
    output_path="./minilm_english_finetuned"
)

model = SentenceTransformer("./minilm_english_finetuned", device=device)
preds, labels = [], []
for _, row in test_df.iterrows():
    emb1 = model.encode(row['sentence1'], convert_to_tensor=True)
    emb2 = model.encode(row['sentence2'], convert_to_tensor=True)
    cos_sim = util.cos_sim(emb1, emb2).item()
    preds.append(cos_sim)
    labels.append(float(row['avg_score']))

mse = mean_squared_error(labels, preds)
spearman_corr, _ = spearmanr(labels, preds)
pearson_corr, _ = pearsonr(labels, preds)

print("=== 評估結果 ===")
print(f"MSE: {mse:.4f}")
print(f"Spearman Correlation: {spearman_corr:.4f}")
print(f"Pearson Correlation: {pearson_corr:.4f}")

plt.figure(figsize=(8, 6))
plt.scatter(labels, preds, alpha=0.6)
plt.plot([0, 1], [0, 1], 'r--', label="Perfect Correlation")
plt.xlabel("Ground Truth (avg_score)")
plt.ylabel("Predicted Cosine Similarity")
plt.title("Predicted vs. True Similarity")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()