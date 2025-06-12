# Discord bot

This bot provides automated comment summarization for YouTube videos through a slash command interface.

## Input

The user can type a slash command like:

`/summarize <YouTube_URL>`

This triggers the bot to fetch and analyze comments from the given YouTube video.

---

### Process

1. The bot extracts the video ID from the provided URL.
2. It fetches up to 100 YouTube comments using the YouTube Data API.
3. The comments are passed into `analyze_pipeline.py`, which performs:
    - **Preprocessing**: Cleaning and normalization
    - **Language Detection**: Identifies comment language proportions
    - **Keyword Extraction**:
        - Chinese comments → `jieba` tokenization + KeyBERT + fallback
        - English comments → Sentence embedding + clustering + fallback
    - **Summarization**:
        - Chinese → fine-tuned BERTSUM
        - English → fine-tuned BERTSUM

---

### Output

The bot responds with a formatted Discord Embed message that includes:

-   **Video Title**
-   **Summarized Comments** (Top 3 highlight sentences)
-   **Extracted Keywords** (Top 3 per language)
-   **Language Distribution** (e.g., zh/en/others %)
-   A button linking back to the original video

All outputs are automatically adjusted based on the detected dominant language of the video’s comment section.
