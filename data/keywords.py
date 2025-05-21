# 關鍵字與語言比例分析程式範例
# 直接讀取 Cleaned_Comments.csv，將影片 ID、留言數、熱門關鍵字與詞頻，以及留言語言比例輸出到同一個 CSV，並在 keyword 與 language 間插入空白列

import pandas as pd
from collections import Counter
from pathlib import Path
from APIComments import VIDEO_ID

# 使用者設定區
CSV_FILE = Path('./data/datasets/cleanedComments') / f'{VIDEO_ID}.csv'  # 已預處理並包含 jieba 斷詞與語言欄位的 CSV 檔
STOPWORDS_FILE = ''              # 可選：停用詞檔（每行一個詞），若不需要停用詞可設定空字串
TOP_N = 5                        # 要列出的熱門關鍵字數量
SPLIT_SEP = ','                  # jieba 斷詞結果的分隔符
OUTPUT_DIR = Path('./data/datasets/Keywords')     # 輸出資料夾
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f'{VIDEO_ID}.csv'  # 同一輸出檔案


def extract_keywords(df, stopwords_file=None, top_k=10, sep=','):
    """
    從 DataFrame 中提取關鍵字。
    需包含「結巴斷詞」欄位；返回前 top_k 個 (詞, 頻次) 列表。
    """
    stopwords = set()
    if stopwords_file:
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            stopwords = {w.strip() for w in f if w.strip()}

    freq = Counter()
    for raw in df['結巴斷詞'].dropna():
        tokens = raw.split(sep)
        for token in tokens:
            token = token.strip()
            if len(token) <= 1 or token in stopwords:
                continue
            freq[token] += 1
    return freq.most_common(top_k)


def analyze_language_ratio(df):
    """
    計算留言的語言分佈比例。
    假設 df 含「語言」欄位，回傳各語言的 (language, count, ratio) 列表。
    """
    total = len(df)
    lang_counts = Counter(df['語言'].dropna())
    ratios = {lang: count / total for lang, count in lang_counts.items()}
    return [(lang, lang_counts[lang], ratios[lang]) for lang in sorted(lang_counts, key=lang_counts.get, reverse=True)]


def main():
    # 1. 讀取資料
    df = pd.read_csv(CSV_FILE, dtype=str)

    # 2. 計算留言總數
    comment_count = len(df)

    # 3. 提取熱門關鍵字
    keywords = extract_keywords(
        df,
        stopwords_file=STOPWORDS_FILE or None,
        top_k=TOP_N,
        sep=SPLIT_SEP
    )

    # 4. 分析語言比例
    lang_list = analyze_language_ratio(df)

    # 5. 組成輸出表格：
    records = []
    # 關鍵字部分
    for word, cnt in keywords:
        records.append({
            'video_id': VIDEO_ID,
            'comment_count': comment_count,
            'type': 'keyword',
            'item': word,
            'value': cnt
        })
    # 插入空白列
    records.append({
        'video_id': '',
        'comment_count': '',
        'type': '',
        'item': '',
        'value': ''
    })
    # 語言比例部分（comment_count 設為空白）
    for lang, count, ratio in lang_list:
        records.append({
            'video_id': VIDEO_ID,
            'comment_count': '',
            'type': 'language',
            'item': lang,
            'value': f"{count} ({ratio:.2%})"
        })

    summary_df = pd.DataFrame(records)
    summary_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f'已輸出關鍵字與語言比例摘要至 {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
