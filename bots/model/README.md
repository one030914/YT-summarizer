# Model

This system provides automated YouTube comment analysis including summarization and keyword extraction, with multilingual support via a Discord bot.

---

## Keywords

### MiniLM

Each YouTube comment is converted into a high-dimensional semantic vector using a fine-tuned MiniLM. This ensures semantic similarity is captured even when different wording is used.

### HDBSCAN

It clusters similar sentence embeddings into semantically coherent groups without requiring a predefined number of clusters. This flexibility helps capture real-world diversity in opinions.

### KeyBERT

For each cluster, comments are merged into a single document, then passed to KeyBERT. KeyBERT extracts keywords by comparing the sentence embedding of the cluster center with candidate word embeddings using cosine similarity.

### Fallback Mechanism

When clustering fails or comments are too sparse or noisy, the system automatically falls back to selecting the top N most frequent words across all comments.

---

## Summaries

### BERTSUM (Extractive Summarization)

We fine-tune two BERTSUM models (one for Chinese, one for English) to identify which comments are most representative. For each comment, the model predicts whether it should be included in the summary based on contextual importance and sentence-level salience.

---

## Discord Bot

### Input

Users interact with the system via a slash command:

`/summarize <YouTube_URL>`
