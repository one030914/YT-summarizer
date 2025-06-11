import langid
from collections import Counter
from data.preprocess import clean_text
from model.get_summary_zh import predict_summary_sentences_zh
from model.get_summary_en import predict_summary_sentences_en
from model.get_keyword_zh import extract_short_keywords
from model.get_keywords_en import cluster_and_extract_keywords
import jieba

def detect_lang(text):
    lang, _ = langid.classify(text)
    return lang

def detect_lang_distribution(comments):
    langs = [detect_lang(c) for c in comments]
    count = Counter(langs)
    total = sum(count.values())
    zh = sum([v for k, v in count.items() if k == 'zh'])
    en = sum([v for k, v in count.items() if k == 'en'])
    other = total - zh - en
    return {
        "zh": round(zh / total * 100, 1),
        "en": round(en / total * 100, 1),
        "other": round(other / total * 100, 1)
    }

def analyze_comments(raw_comments: list[str]) -> dict:
    # 清洗留言
    cleaned = [clean_text(c) for c in raw_comments]
    cleaned = [c for c in cleaned if c.strip()]
    if not cleaned:
        return {}

    # 分語言
    lang_dist = detect_lang_distribution(cleaned)
    zh_comments = [c for c in cleaned if detect_lang(c) == "zh"]
    en_comments = [c for c in cleaned if detect_lang(c) == "en"]
    main_lang = max(lang_dist, key=lang_dist.get)

    summary = []
    keywords = []

    if main_lang == 'zh' or (main_lang not in ['zh', 'en'] and zh_comments):
        summary = predict_summary_sentences_zh(zh_comments, return_top_n=3)
        token_lists = [list(jieba.cut(c)) for c in zh_comments]
        kw_dict = extract_short_keywords(zh_comments, token_lists, top_n=3)
        keywords = list(set(w for group in kw_dict.values() for w in group))[:3]
    elif main_lang == 'en' or (main_lang not in ['zh', 'en'] and en_comments):
        summary = predict_summary_sentences_en(en_comments, return_top_n=3)
        kw_dict = cluster_and_extract_keywords(en_comments, top_n=3)
        keywords = list(set(w for group in kw_dict.values() for w in group))[:3]

    return {
        "summary": summary,
        "keywords": keywords,
        "lang_ratio": lang_dist
    }