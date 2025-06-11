import torch
from transformers import BertTokenizer
import torch.nn as nn
from torch.nn import Sigmoid

class BERTSentenceClassifier(nn.Module):
    def __init__(self, pretrained_model='bert-base-chinese'):
        super().__init__()
        self.bert = nn.Module()
        from transformers import BertModel
        self.bert = BertModel.from_pretrained(pretrained_model)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output)
        return logits.squeeze(-1)

def load_model(model_dir="output_bertsum_metrics"):
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model = BERTSentenceClassifier()
    model.load_state_dict(torch.load(f"{model_dir}/pytorch_model.bin", map_location="cpu"))
    model.eval()
    return tokenizer, model

def predict_summary_sentences(sentences, tokenizer, model, threshold=0.5):
    results = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(inputs["input_ids"], inputs["attention_mask"])
            prob = Sigmoid()(logits).item()
            results.append((sentence, prob, prob >= threshold))
    return results

if __name__ == "__main__":
    example_comments = [
        "這部影片真的太感人了",
        "剪輯還可以更好",
        "音樂搭得非常棒",
        "不知道為什麼最後一段很出戲",
        "我看到哭出來"
    ]

    tokenizer, model = load_model("BERTSUM_chinese_finetuned")
    output = predict_summary_sentences(example_comments, tokenizer, model)

    print("📌 預測結果：")
    for sent, score, is_sum in output:
        mark = "✓" if is_sum else "✗"
        print(f"{mark} {sent} (score={score:.2f})")