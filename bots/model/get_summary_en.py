import torch
from transformers import BertTokenizer
import torch.nn as nn
from torch.nn import Sigmoid

class BERTSentenceClassifier(nn.Module):
    def __init__(self, pretrained_model='bert-base-uncased'):
        super().__init__()
        from transformers import BertModel
        self.bert = BertModel.from_pretrained(pretrained_model)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output)
        return logits.squeeze(-1)

def load_model_en(model_dir="bots/model/BERTSUM_english_finetuned"):
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model = BERTSentenceClassifier()
    model.load_state_dict(torch.load(f"{model_dir}/pytorch_model.bin", map_location="cpu"))
    model.eval()
    return tokenizer, model

def predict_summary_sentences_en(sentences, threshold=0.5, return_top_n=3):
    tokenizer, model = load_model_en()
    results = []
    scored = []

    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(inputs["input_ids"], inputs["attention_mask"])
            prob = Sigmoid()(logits).item()
            scored.append((sentence, prob))

    top = sorted(scored, key=lambda x: x[1], reverse=True)[:return_top_n]
    results = [s for s, p in top if p > threshold]
    return results