# YouTube 留言預處理 + 存檔版
import re
import emoji
import langid
import jieba
from bs4 import BeautifulSoup
from opencc import OpenCC
import unicodedata
import pandas as pd
from pathlib import Path
import re
from itertools import groupby

# 設定只辨識中文和英文，避免過度分類
langid.set_languages(['zh', 'en'])

# 初始化工具
cc = OpenCC('s2t')  # 簡體轉繁體 (Simplified Chinese to Traditional Chinese)

# ===== 基本預處理函數 =====

def clean_html(text):
    """移除 HTML 標籤"""
    # 確保輸入為字串
    if not isinstance(text, str):
        return ''
    return BeautifulSoup(text, "html.parser").get_text()

# ===== 預編譯正則 =====

URL_RE = re.compile(r'\b(?:https?://|www\.)\S+\b')
# 移除各種URL／URI  
SPECIAL_RE = re.compile(r'[^a-zA-Z0-9\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF\u2018\u2019\s\.,!%?]')
# 過濾除中英數、中文、日文（平假名\u3040-\u309F、片假名\u30A0-\u30FF）、空白及「.,!?」外的特殊符號
WHITESPACE_RE = re.compile(r'\s+') 
# 合併連續空白為單一空格  
TIME_RE = re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b')
# 去除 mm:ss 或 hh:mm:ss 格式時間  
ELLIPSIS_RE = re.compile(r'(?:…|\.{3})')
# 保護省略號（… 或 ...）以便還原  
DUP_PUNC_RE = re.compile(r'([^\w\s])\1+')
# 壓縮重複標點成單一符號
KANA_RE = re.compile(r'[ぁ-んァ-ン]')
# 平假名/片假名偵測
CHINESE_RE = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
# 中文字（CJK 統一漢字）範圍
TIME_PATTERN = re.compile(r'(\d{1,2})/(\d{1,2})\s*(上午|下午)\s*(\d{1,2}):(\d{2})')
# 抓日期時間格式

# ===== CC轉換修正表 =====

CUSTOM_FIXES = {
    "喫": "吃", 
    "纔": "才",
    "鬥內": "抖內",
    "傑哥": "杰哥"
}

# ===== 全形半形補充表 =====

FULL2HALF_CUSTOM = str.maketrans({
    '’': "'",'‘': "'"
})

# ===== 預處理子函數 =====

def remove_emoji(text):
    """移除表情符號"""
    return emoji.replace_emoji(text if isinstance(text, str) else '', replace='')

def remove_url(text):
    """移除網址"""
    return URL_RE.sub('', text if isinstance(text, str) else '')

def remove_special_chars(text):
    """移除特殊符號，只留中英文、數字和基本標點"""
    return SPECIAL_RE.sub('', text if isinstance(text, str) else '')

def remove_timestamps(text):
    """移除 YouTube 留言中的時間軸標記 (mm:ss 或 h:mm:ss)"""
    return TIME_RE.sub('', text if isinstance(text, str) else '')

def normalize_fullwidth_to_halfwidth(text):
    # 全形→半形補充字庫
    t = unicodedata.normalize('NFKC', text if isinstance(text, str) else '')
    # 補自訂映射
    return t.translate(FULL2HALF_CUSTOM)

def remove_extra_whitespace(text):
    """去除多餘空白"""
    return WHITESPACE_RE.sub(' ', text if isinstance(text, str) else '').strip()

def remove_repeated_punct(text: str) -> str:
    # 1. 用佔位符保護所有省略號
    ellipses = ELLIPSIS_RE.findall(text)
    placeholder = '<ELLIPSIS>'
    text = ELLIPSIS_RE.sub(placeholder, text)
    # 2. 把其他「同一個字元連 2 次以上」都縮成 1 次
    text = DUP_PUNC_RE.sub(r'\1', text)
    # 3. 還原所有省略號
    for _ in ellipses:
        text = text.replace(placeholder, '...')  # 或用 '…' 視你想用哪種
    return text

def japanese_ratio(text: str) -> float:
    # 回傳文字中日文（平假名+片假名）字元佔全部非空白字元的比例
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    jp_count = sum(1 for c in chars if KANA_RE.match(c))
    return jp_count / len(chars)

def remove_chinese_if_mostly_japanese(text: str, threshold: float = 0.15) -> str:
    # 只有當日文字元佔比 > threshold 時，才移除漢字
    return CHINESE_RE.sub('', text) if japanese_ratio(text) > threshold else text

def collapse_repeated_words(text: str, min_repeat: int = 3) -> str:
    # 把連續出現 min_repeat 次以上的同一詞，壓縮成單一詞。
    tokens = jieba.lcut(text)
    collapsed = []
    for w, grp in groupby(tokens):
        length = sum(1 for _ in grp)
        if length >= min_repeat:
            collapsed.append(w)
        else:
            collapsed.extend([w] * length)
    return ''.join(collapsed)

def to_chinese_datetime(match):
    # 日期時間轉為中文敘述
    month, day, meridiem, hour, minute = match.groups()
    minute_text = "整" if minute == "00" else f"{int(minute)}分"
    return f"{int(month)}月{int(day)}日{meridiem}{int(hour)}點{minute_text}"

def convert_all_datetimes(text: str) -> str:
    return TIME_PATTERN.sub(to_chinese_datetime, text)

def clean_text(text):
    """執行基本清洗流程"""
    # 處理 NaN 或非字串
    text = text if isinstance(text, str) else ''
    steps = [clean_html, normalize_fullwidth_to_halfwidth, expand_english_contractions, remove_chinese_if_mostly_japanese, convert_all_datetimes, remove_timestamps, remove_emoji, remove_url, remove_special_chars, remove_repeated_punct, collapse_repeated_words, remove_extra_whitespace]
    for fn in steps:
        text = fn(text)
    return text

# ===== 中文正規化 =====

def remove_chinese_particles(text):
    """移除中文語助詞"""
    particles = ["啊啊","呀","阿阿","吧","嘛","啦","唄","喔","噢","哦","咧","哇!","哇","嘍","哩","哈哈","嘿","唷","咦","唉","哎","嗨","嗚","嗯","嗚喔","噓","喔耶","嘶","咻","痾","哼","哼哼","嘖","嘖嘖","嘿嘿","喔唷","呃","呃…","嗯哼","恩哼","吼","嗚呼","唔","噢耶","噢不","欸欸","咩","嘶…","哞","咯","咯咯","嘻","嘻嘻","嗚哇","哎哎","吶","噗","噗通","嘿呦","咻咻","哧","唏","唏噓","咕","咕嚕","咚","咚咚","噠","噠噠","哐","哐當","咔","咔嚓","啪","啪啪","嘭","砰","喔莫"]

    for p in particles:
        text = text.replace(p, '')
    return text

def normalize_chinese(text):
    """中文正規化：簡轉繁、去語助詞"""
    text = cc.convert(text)
    return remove_chinese_particles(text)

def cc_convert_with_fixes(text: str) -> str:
    for wrong, right in CUSTOM_FIXES.items():
        text = text.replace(wrong, right)
    return text

# ===== 英文正規化 =====

def expand_english_contractions(text):
    """展開英文縮寫"""
    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "don't": "do not",
        "didn't": "did not",
        "isn't": "is not",
        "aren't": "are not",
        "it's": "it is",
        "i'm": "i am",
        "you're": "you are",
        "they're": "they are",
        "we're": "we are"
    }
    for k, v in contractions.items():
        text = text.replace(k, v)
    return text


def normalize_english(text):
    """英文正規化：小寫化、展開縮寫"""
    text = text.lower()
    return expand_english_contractions(text)

# ===== 單則預處理 =====

def preprocess_comment(raw_comment):
    """單則留言完整預處理，不回傳 confidence"""
    # 確保為字串
    raw_comment = raw_comment if isinstance(raw_comment, str) else ''
    raw_comment = remove_chinese_if_mostly_japanese(raw_comment)
    cleaned = clean_text(raw_comment)
    if cleaned == '':
        return {"text": "", "language": "unknown"}
    if japanese_ratio(cleaned) > 0.85:
        return {"text": cleaned, "language": "unknown"}
    lang = langid.classify(cleaned)[0]

    if lang == 'zh':
        cleaned = cc_convert_with_fixes(normalize_chinese(cleaned))
    elif lang == 'en':
        cleaned = normalize_english(cleaned)
    else:
        lang = 'unknown'

    return {"text": cleaned, "language": lang}

# ===== 批次處理 =====

def batch_preprocess_comments(json_data):
    """保留中英文，移除重複"""
    comments = []
    for entry in json_data:
        raw = entry.get('commentText', '')
        if not isinstance(raw, str):
            continue
        proc = preprocess_comment(raw)
        if proc['language'] in ['zh', 'en', 'unknown']:
            comments.append({
                "原始留言": raw,
                "清理後留言": proc['text'],
                "語言": proc['language']
            })
    df = pd.DataFrame(comments).drop_duplicates(subset=['清理後留言'])
    return df

# ===== 主程式 =====

if __name__ == "__main__":
    # 1. 從 CSV 讀取原始留言欄位
    in_path = Path('APItoCSV') / 'youtube_comments.csv'
    df_in = pd.read_csv(in_path, encoding='utf-8-sig')
    if 'text' in df_in.columns and 'commentText' not in df_in.columns:
        df_in = df_in.rename(columns={'text': 'commentText'})
    raw_json = df_in[['commentText']].fillna('').to_dict(orient='records')

    # 2. 處理並存檔
    print("🔵 開始批次預處理留言...")
    df_out = batch_preprocess_comments(raw_json)
    print("🟢 預處理完成，結果前幾筆：")
    print(df_out.head())

    out_dir = Path('Preprocess')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'cleaned_comments.csv'
    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"✅ 輸出到：{out_path}")