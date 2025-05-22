# YouTube 留言預處理 + 存檔版
import re
import unicodedata
import emoji
import langid
import jieba
import jieba.posseg
import pandas as pd
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
from pathlib import Path
from opencc import OpenCC
from APIComments import VIDEO_ID
import contractions

# 初始化轉換器
cct2s = OpenCC('t2s')
ccs2t = OpenCC('s2t')
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# 正則表達式
PATTERNS = {
    'url': re.compile(r'\b(?:https?://|www\.)\S+\b'),
    'special': re.compile(r'[^0-9A-Za-z\u3400-\u4DBF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\u2018\u2019\'\s\.,!%?…]'),
    'whitespace': re.compile(r'\s+'),
    'time': re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b'),
    'ellipsis': re.compile(r'(?:…|\.{3,6})'),
    'dup_punc': re.compile(r'([^\w\s])\1+'),
    'kana': re.compile(r'[ぁ-んァ-ン]'),
    'leading_punc': re.compile(r'^[\!\?\.\,\;\:\…]+'),
    'repeated': re.compile(r'(?P<grp>.+?)\1+')
}

# 自定義轉換表
CUSTOM_FIXES = {
    "喫": "吃", "纔": "才", "鬥內": "抖內", "傑哥": "杰哥",
    "孃": "娘", "穫": "獲", "裏": "裡", "三文治": "三明治", "面": "麵"
}

# 結巴設定
JIEBA_PROTECTED = ["臺灣"]
STOPWORDS = {"是", "的", "了", "有", "没", "在", "也", "都", "为", "能", "不", "好", "像", "咧", "袂", "著", 
             "希望", "人", "听", "歌", "会", "吃", "要", "看", "爱", "让", "拍", "到", "说", "没有", "有", 
             "讲", "大", "小", "首歌", "不到"}

def clean_text(text):
    """基本文本清理"""
    if not isinstance(text, str):
        return ''
    
    # HTML清理
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # 基本清理
    text = unicodedata.normalize('NFKC', text)
    text = PATTERNS['url'].sub('', text)
    text = PATTERNS['special'].sub('', text)
    text = PATTERNS['time'].sub('', text)
    text = emoji.replace_emoji(text, replace='')
    
    # 處理重複標點
    ellipses = PATTERNS['ellipsis'].findall(text)
    text = PATTERNS['ellipsis'].sub('<ELLIPSIS>', text)
    text = PATTERNS['dup_punc'].sub(r'\1', text)
    for _ in ellipses:
        text = text.replace('<ELLIPSIS>', '...')
    
    # 清理空白
    return PATTERNS['whitespace'].sub(' ', text).strip()

class TextNormalizer:
    def __init__(self):
        for word in JIEBA_PROTECTED:
            jieba.add_word(word)
    
    def normalize_chinese(self, text):
        """中文正規化"""
        # 繁轉簡
        text = cct2s.convert(text)
        
        # 分詞處理
        words = []
        for w, flag in jieba.posseg.lcut(text):
            if (flag.startswith(('n','v','a')) or flag in ('i','l')) and w not in STOPWORDS:
                words.append(w)
        
        # 合併並清理
        text = ''.join(words)
        text = PATTERNS['leading_punc'].sub('', text)
        
        # 處理重複片段
        while True:
            new = PATTERNS['repeated'].sub(r'\g<grp>', text)
            if new == text:
                break
            text = new
            
        return text
    
    def normalize_english(self, text):
        """英文正規化"""
        text = text.lower()
        text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text)
        return contractions.fix(text)

def preprocess_comment(raw_comment):
    """單則留言預處理"""
    cleaned = clean_text(raw_comment)
    if not cleaned or PATTERNS['kana'].search(cleaned):
        return {"text": cleaned, "language": "unknown"}
    
    lang = langid.classify(cleaned)[0]
    normalizer = TextNormalizer()
    tokens = []
    
    if lang == 'zh':
        cleaned = normalizer.normalize_chinese(cleaned)
        cleaned = normalizer.normalize_english(cleaned)
        tokens = [w for w in jieba.lcut(cleaned) if re.match(r'[\w\u4E00-\u9FFF0-9]', w) and w.strip()]
        tokens = [ccs2t.convert(w) for w in tokens]
        tokens = [CUSTOM_FIXES.get(w, w) for w in tokens]
    elif lang == 'en':
        cleaned = normalizer.normalize_english(cleaned)
        tokens = []
    else:
        lang = 'unknown'
    
    return {"text": cleaned, "language": lang, "tokens": tokens}

def batch_preprocess_comments(json_data):
    """批次處理留言"""
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
                "語言": proc['language'],
                "結巴斷詞": ",".join(f"'{w}'" for w in proc.get("tokens", []))
            })
    
    return pd.DataFrame(comments).drop_duplicates(subset=['清理後留言'])

if __name__ == "__main__":
    in_path = Path('Youtube_Comments') / f'{VIDEO_ID}.csv'
    df_in = pd.read_csv(in_path, encoding='utf-8-sig')
    if 'text' in df_in.columns and 'commentText' not in df_in.columns:
        df_in = df_in.rename(columns={'text': 'commentText'})
    
    print("🔵 開始批次預處理留言...")
    df_out = batch_preprocess_comments(df_in[['commentText']].fillna('').to_dict(orient='records'))
    print("🟢 預處理完成，結果前幾筆：")
    print(df_out.head())
    
    out_dir = Path('Cleaned_Comments')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{VIDEO_ID}.csv'
    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"✅ 輸出到：{out_path}")
