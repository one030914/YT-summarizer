# Model
The input will have three arguments: languages, comments, and Chinese keywords.
The output will have keywords and summaries.

## Keywords

### MiniLM
Each YouTube comment is converted into a high-dimensional semantic vector using a fine-tuned MiniLM. This process captures the meaning of each sentence in vector form and ensures we're comparing true meaning, not just word overlap.

### HDBSCAN
It organizes semantically similar comments into clusters without needing to specify the number of clusters. This enables flexible and adaptive grouping of semantically identical ideas.

### KeyBERT
For each cluster, we combine the comments into a single block of text. Then, we apply KeyBERT to extract the most relevant keywords from this combined text.

KeyBERT computes the sentence embedding of the entire block (the "semantic center" of the cluster). It also generates embeddings for candidate keywords from the text and selects keywords based on cosine similarity between the sentence embedding and each keyword vector. This approach highlights the most informative words in each cluster, offering clear summaries of discussion themes.

## Summaries

### BERTSUM
