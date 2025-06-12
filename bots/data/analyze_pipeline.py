import langid
from collections import Counter
from data.preprocess import clean_text
from model.get_summary_zh import predict_summary_sentences_zh
from model.get_summary_en import predict_summary_sentences_en
from model.get_keywords_zh import extract_short_keywords
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
    cleaned = [clean_text(c) for c in raw_comments]
    cleaned = [c for c in cleaned if c.strip()]
    if not cleaned:
        return {}

    lang_dist = detect_lang_distribution(cleaned)
    zh_comments = [c for c in cleaned if detect_lang(c) == "zh"]
    en_comments = [c for c in cleaned if detect_lang(c) == "en"]
    main_lang = max(lang_dist, key=lang_dist.get)

    summary = []
    keywords = []

    def run_zh():
        nonlocal summary, keywords
        summary = predict_summary_sentences_zh(zh_comments, return_top_n=3)
        token_lists = [list(jieba.cut(c)) for c in zh_comments]
        kw_dict = extract_short_keywords(zh_comments, token_lists, top_n=3)
        keywords = list(set(w for group in kw_dict.values() for w in group))[:3]

    def run_en():
        nonlocal summary, keywords
        summary = predict_summary_sentences_en(en_comments, return_top_n=3)
        kw_dict = cluster_and_extract_keywords(en_comments, top_n=3)
        keywords = list(set(w for group in kw_dict.values() for w in group))[:3]

    # 判斷使用哪個語言的模型
    if main_lang == 'zh':
        run_zh()
    elif main_lang == 'en':
        run_en()
    elif zh_comments and not en_comments:
        run_zh()
    elif en_comments and not zh_comments:
        run_en()
    elif len(en_comments) >= len(zh_comments):
        run_en()
    else:
        run_zh()

    return {
        "summary": summary,
        "keywords": keywords,
        "lang_ratio": lang_dist
    }