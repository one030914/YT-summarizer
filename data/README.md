## Data

### Datasets
We will have four datasets:
- [X] BERTSUM chinese datasets
- [X] BERTSUM english datasets
- [X] MiniLM chinese datasets
- [X] MiniLM english datasets

for fine-tuning in different models. All datasets have around 900 comments.

We'll go semi-auto or manually to label the dataset.

### BERTSUM dataset
The labels format:
```json
{
    "comments":[
        "comment1",
        "comment2",
        "comment3",
        ...
    ],
    "labels": [0, 1, 0, ...]
}
```

### MiniLM dataset
The labels format:
```json
[
  {
    "sentence1": "這影片我笑到肚子痛",
    "sentence2": "真的超爆笑，完全戳中笑點",
    "score": 0.91
  },
  {
    "sentence1": "剪輯太雜亂了",
    "sentence2": "這部片的節奏很奇怪",
    "score": 0.78
  },
  ...
]

```

### Deploy
In deployment, we'll pass the cleaned comment and keyword (for Chinese models) to the model for prediction.