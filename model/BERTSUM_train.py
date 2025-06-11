import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from torch.optim import AdamW
import torch.nn as nn
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
import matplotlib.pyplot as plt
import os

class BERTSumCSVDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len=512):
        self.samples = []
        for _, row in dataframe.iterrows():
            sentence = str(row["清理後留言"])
            label = int(row["label"])
            tokenized = tokenizer(
                sentence,
                padding='max_length',
                truncation=True,
                max_length=max_len,
                return_tensors='pt'
            )
            self.samples.append({
                'input_ids': tokenized['input_ids'].squeeze(0),
                'attention_mask': tokenized['attention_mask'].squeeze(0),
                'label': torch.tensor(label, dtype=torch.float)
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]

class BERTSentenceClassifier(nn.Module):
    def __init__(self, pretrained_model='bert-base-chinese'):
        super().__init__()
        self.bert = BertModel.from_pretrained(pretrained_model)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output)
        return logits.squeeze(-1)

def train(csv_path, model_save_path, pretrained_model='bert-base-chinese', epochs=10, batch_size=16):
    df = pd.read_csv(csv_path).dropna(subset=["label", "清理後留言"])
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    tokenizer = BertTokenizer.from_pretrained(pretrained_model)
    train_dataset = BERTSumCSVDataset(train_df, tokenizer)
    val_dataset = BERTSumCSVDataset(val_df, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BERTSentenceClassifier(pretrained_model).to(device)

    optimizer = AdamW(model.parameters(), lr=2e-5)
    criterion = nn.BCEWithLogitsLoss()

    train_losses, val_losses, val_accs, val_f1s = [], [], [], []

    for epoch in range(epochs):
        model.train()
        total_train_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} [Train]"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)

            optimizer.zero_grad()
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()

        model.eval()
        total_val_loss = 0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in tqdm(val_loader, desc=f"Epoch {epoch+1} [Val]"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)

                logits = model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                total_val_loss += loss.item()

                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).long().cpu().tolist()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().int().tolist())

        acc = accuracy_score(all_labels, all_preds)
        f1 = f1_score(all_labels, all_preds)

        train_losses.append(total_train_loss / len(train_loader))
        val_losses.append(total_val_loss / len(val_loader))
        val_accs.append(acc)
        val_f1s.append(f1)

        print(f"Epoch {epoch+1} | Train Loss: {train_losses[-1]:.4f} | Val Loss: {val_losses[-1]:.4f} | Acc: {acc:.4f} | F1: {f1:.4f}")

    os.makedirs(model_save_path, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_save_path, "pytorch_model.bin"))
    tokenizer.save_pretrained(model_save_path)

    # plot metrics
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.legend()
    plt.title("Loss")

    plt.subplot(1, 2, 2)
    plt.plot(val_accs, label="Val Accuracy")
    plt.plot(val_f1s, label="Val F1")
    plt.legend()
    plt.title("Accuracy / F1")
    plt.tight_layout()
    plt.savefig(os.path.join(model_save_path, "training_metrics.png"))
    print(f"Model and training plot saved to {model_save_path}")

if __name__ == "__main__":
    train(
        csv_path="./data/datasets/datasets/BERTSUM_chinese.csv",
        model_save_path="./BERTSUM_chinese_finetuned"
    )