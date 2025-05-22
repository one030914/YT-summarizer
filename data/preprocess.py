# YouTube 留言預處理 + 存檔版
import re
from itertools import groupby
import unicodedata
import emoji
import langid
import jieba
import jieba.posseg
import pandas as pd
from bs4 import BeautifulSoup,MarkupResemblesLocatorWarning
import warnings
from pathlib import Path
from opencc import OpenCC
from APIComments import VIDEO_ID
import contractions

# OpenCC語言轉換
cct2s = OpenCC('t2s')
ccs2t = OpenCC('s2t')

# 去除bs4提醒刪除HTML的警告
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

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
SPECIAL_RE = re.compile(
    r"[^0-9A-Za-z"               # 英數
    r"\u3400-\u4DBF\u4E00-\u9FFF" # CJK 擴展 A + 基本漢字
    r"\u3040-\u309F\u30A0-\u30FF" # 日文假名
    r"\u2018\u2019'"              # 撇號
    r"\s\.,!%?…"                  # 空白 + 常用標點
    r"]"
)
# 過濾除中英數、中文、日文（平假名\u3040-\u309F、片假名\u30A0-\u30FF）、空白及「.,!?」外的特殊符號
WHITESPACE_RE = re.compile(r'\s+') 
# 合併連續空白為單一空格  
TIME_RE = re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b')
# 去除 mm:ss 或 hh:mm:ss 格式時間  
ELLIPSIS_RE = re.compile(r'(?:…|\.{3,6})')
# 保護省略號（… 或 ...）以便還原  
DUP_PUNC_RE = re.compile(r'([^\w\s])\1+')
# 壓縮重複標點成單一符號
KANA_RE = re.compile(r'[ぁ-んァ-ン]')
# 平假名/片假名偵測
CHINESE_RE = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
# 中文字（CJK 統一漢字）範圍
TIME_PATTERN = re.compile(r'(\d{1,2})/(\d{1,2})\s*(上午|下午)\s*(\d{1,2}):(\d{2})')
# 抓日期時間格式
LEADING_PUNC_RE = re.compile(r'^[\!\?\.\,\;\:\…]+')
# 選取位於開頭的 ! ? . , ; : … 等符號

# ===== CC轉換修正表 =====
CUSTOM_FIXES = {
	"喫": "吃", 
	"纔": "才",
	"鬥內": "抖內",
	"傑哥": "杰哥",
	"孃": "娘",
	"穫": "獲",
	"裏": "裡",
	"三文治": "三明治",
	"面": "麵"
}
def cc_convert_with_fixes(text: str) -> str:
		for wrong, right in CUSTOM_FIXES.items():
			text = text.replace(wrong, right)
		return text

# ===== 結巴保護字庫 =====
Jieba_Protected = [
	"臺灣"
	]

# ===== 結巴濾除字庫補充 =====
stopwords = {"是","的","了","有","没","在","也","都","为","能","不","好","像","咧","袂","著","希望","人","听","歌","会","吃","要","看","爱","让","拍","到","说","没有","有","讲","大","小","首歌","不到"}

# ===== 全形半形補充表 =====
FULL2HALF_CUSTOM = str.maketrans({
	'’': "'",'‘': "'"
})

# ===== 預處理子函數 =====
def remove_emoji(text):
	# 移除表情符號
	return emoji.replace_emoji(text if isinstance(text, str) else '', replace='')

def remove_url(text):
	# 移除網址
	return URL_RE.sub('', text if isinstance(text, str) else '')

def remove_special_chars(text):
	# 移除特殊符號，只留中英文、數字和基本標點
	return SPECIAL_RE.sub('', text if isinstance(text, str) else '')

def remove_timestamps(text):
	# 移除 YouTube 留言中的時間軸標記 (mm:ss 或 h:mm:ss)
	return TIME_RE.sub('', text if isinstance(text, str) else '')

def normalize_fullwidth_to_halfwidth(text):
	# 全形→半形補充字庫
	t = unicodedata.normalize('NFKC', text if isinstance(text, str) else '')
	# 補自訂映射
	return t.translate(FULL2HALF_CUSTOM)

def remove_extra_whitespace(text):
	# 去除多餘空白
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

def to_chinese_datetime(match: re.Match) -> str:
	# 把 match.group(1–5) 轉成「M月D日上午H點xx分」格式
	month, day, meridiem, hour, minute = match.groups()
	minute_text = "整" if minute == "00" else f"{int(minute)}分"
	return f"{int(month)}月{int(day)}日{meridiem}{int(hour)}點{minute_text}"

def convert_all_datetimes(text: str) -> str:
	# 把所有符合 TIME_PATTERN 的子串（m/d 上午/下午 h:mm）用 to_chinese_datetime() 轉成中文敘述。
	# 這裡傳 self.to_chinese_datetime 作為 callback
	return TIME_PATTERN.sub(to_chinese_datetime, text)

def clean_text(text):
	# 執行基本清洗流程
	text = text if isinstance(text, str) else ''
	steps = [clean_html, normalize_fullwidth_to_halfwidth, convert_all_datetimes, remove_timestamps, remove_emoji, remove_url, remove_special_chars, remove_repeated_punct, remove_extra_whitespace]
	for fn in steps:
		text = fn(text)
	return text

# ===== 中文正規化 =====
class ChineseNormalizer:
	
	def tc2sc(self, text: str) -> str:
		# 中文正規化：繁轉簡
		text = cct2s.convert(text)
		return text
	
	def remove_leading_punct(self, text: str) -> str:
		# 移除因去除贅字後開頭的標點符號（如 ! ? . , ; : …）
		return LEADING_PUNC_RE.sub('', text)

	def collapse_repeated_segments(self, text: str) -> str:
		#將任意連續重複出現兩次以上的子串，只保留一次。
		# (?P<grp>.+?) 以非貪婪方式匹配最短子串
		# \1+          後面跟著一個以上完全相同的重複
		pattern = re.compile(r'(?P<grp>.+?)\1+')
		# 多次 apply，直到不再變化
		while True:
			new = pattern.sub(r'\g<grp>', text)
			if new == text:
				break
			text = new
		return text

	def normalize(self, text: str) -> str:
		t = text if isinstance(text, str) else ''
		t = self.tc2sc(t)
		t = self.remove_leading_punct(t)
		t = self.collapse_repeated_segments(t)
		return t

# ===== 英文正規化 =====
class EnglishNormalizer:
	def expand_english_contractions(self, text: str) -> str:
		# 使用 contractions 套件將英文縮寫正確展開
		if not isinstance(text, str):
			return ""
		return contractions.fix(text)
	
	def normalize_english(self, text: str) -> str:
		# 英文正規化：小寫化、展開縮寫
		text = text.lower()
		return text
	
	def collapse_elongated_to_one(self, text: str) -> str:
		# 把連續重複 3 次以上的字母，縮減到剩一個：
		return re.sub(r'([A-Za-z])\1{2,}', r'\1', text)

	def normalize(self, text: str) -> str:
		t = text if isinstance(text, str) else ''
		t = self.normalize_english(t)
		t = self.collapse_elongated_to_one(t)
		t = self.expand_english_contractions(t)
		return t

# ===== 結巴斷詞 =====
def Jieba_Keywords(text: str) -> list:
		filtered = []
		# 確保保護詞已加入詞典（可放在 module 初始化時做一次）
		for w in Jieba_Protected:
			jieba.add_word(w)

		# 分詞＋詞性標注
		for w, flag in jieba.posseg.lcut(text):
			# 只保留 n*、v*、a*、i、l
			if flag.startswith(('n','v','a')) or flag in ('i','l'):
				if w not in stopwords and w.strip():
					filtered.append(w)

		return filtered

# ===== 單則預處理 =====
def preprocess_comment(raw_comment):
	# 確保為字串
	raw_comment = raw_comment if isinstance(raw_comment, str) else ''
	cleaned = clean_text(raw_comment)
	if cleaned == '':
		return {"text": "", "language": "unknown"}
	
	lang = langid.classify(cleaned)[0]
	tokens = []

	if lang == 'zh':
		tokens = ChineseNormalizer().normalize(cleaned)
		tokens = Jieba_Keywords(cleaned)
		tokens = [ccs2t.convert(w) for w in tokens]
		tokens = [cc_convert_with_fixes(w) for w in tokens]
		cleaned = ''.join(tokens)
	elif lang == 'en':
		cleaned = EnglishNormalizer().normalize(cleaned)
		tokens = []
	else:
		lang = 'unknown'

	return {"text": cleaned, "language": lang ,"tokens": tokens}

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
				"語言":      proc['language'],
				"結巴斷詞": ",".join(f"'{w}'" for w in (proc.get("tokens", [])))
			})
	df = pd.DataFrame(comments).drop_duplicates(subset=['清理後留言'])
	return df

# ===== 主程式 =====

if __name__ == "__main__":
	# 1. 從 CSV 讀取原始留言欄位
	in_path = Path('Youtube_Comments') / f'{VIDEO_ID}.csv'
	df_in = pd.read_csv(in_path, encoding='utf-8-sig')
	if 'text' in df_in.columns and 'commentText' not in df_in.columns:
		df_in = df_in.rename(columns={'text': 'commentText'})
	raw_json = df_in[['commentText']].fillna('').to_dict(orient='records')

	# 2. 處理並存檔
	print("🔵 開始批次預處理留言...")
	df_out = batch_preprocess_comments(raw_json)
	print("🟢 預處理完成，結果前幾筆：")
	print(df_out.head())
	
	out_dir = Path('Cleaned_Comments')
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f'{VIDEO_ID}.csv'
	df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
	print(f"✅ 輸出到：{out_path}")
