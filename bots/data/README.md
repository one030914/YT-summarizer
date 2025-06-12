# Data

## Datasets

We have prepared four labeled datasets to fine-tune models based on their language and task:

-   [x] BERTSUM chinese datasets
-   [x] BERTSUM english datasets
-   [x] MiniLM chinese datasets
-   [x] MiniLM english datasets

for fine-tuning in different models. All datasets have around 900 comments.

We'll go auto or manually to label the dataset.

Each dataset contains approximately **900 labeled comments**, collected from real YouTube videos across different genres. Labeling is done either **manually** or through a **semi-automated similarity-based approach**.

---

## BERTSUM Dataset Format

Used for extractive summarization.

```json
{
    "comments": ["comment1", "comment2", "comment3"],
    "labels": [0, 1, 0]
}
```

Each comment is associated with a binary label indicating whether it should be included in the summary (`1`) or not (`0`).

---

## MiniLM dataset

Used for fine-tuning semantic similarity models with sentence-pair structure:

```json
[
    {
        "sentence1": "這影片我笑到肚子痛",
        "sentence2": "真的超爆笑，完全戳中笑點",
        "avg_score": 0.91
    },
    {
        "sentence1": "剪輯太雜亂了",
        "sentence2": "這部片的節奏很奇怪",
        "avg_score": 0.78
    }
]
```

These sentence pairs are auto-labeled using pretrained similarity models (e.g., `text2vec` or multilingual MiniLM). High similarity scores indicate strong semantic closeness for contrastive fine-tuning.

---

## Deployment Usage

When deploying the system, the pipeline operates as follows:

1. **Input**: Raw YouTube comments are collected and cleaned.
2. **Language Detection**: The dominant language (zh / en) is determined.
3. **Model Inference**:
    - For **BERTSUM**, the cleaned comments are fed to the appropriate summarization model.
    - For **MiniLM + KeyBERT**, if the language is Chinese, we pass in tokenized comments (using `jieba`) as keyword candidates.
4. **Output**: The system returns the top 3 summary sentences and top 3 keywords, along with language distribution stats.

The trained models are fully integrated into a Discord bot and callable via slash commands.

---
