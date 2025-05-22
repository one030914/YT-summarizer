## clean_text

[clean_html, normalize_fullwidth_to_halfwidth, convert_all_datetimes, remove_timestamps, remove_emoji, remove_url, remove_special_chars, remove_repeated_punct, remove_extra_whitespace]


def clean_html(text):
	"""移除 HTML 標籤"""
	# 確保輸入為字串
	if not isinstance(text, str):
		return '' 
	return BeautifulSoup(text, "html.parser").get_text()

def normalize_fullwidth_to_halfwidth(text):
	# 全形→半形補充字庫
	t = unicodedata.normalize('NFKC', text if isinstance(text, str) else '')
	# 補自訂映射
	return t.translate(FULL2HALF_CUSTOM)

def convert_all_datetimes(text: str) -> str:
	# 把所有符合 TIME_PATTERN 的子串（m/d 上午/下午 h:mm）用 to_chinese_datetime() 轉成中文敘述。
	# 這裡傳 self.to_chinese_datetime 作為 callback
	return TIME_PATTERN.sub(to_chinese_datetime, text)

def to_chinese_datetime(match: re.Match) -> str:
	# 把 match.group(1–5) 轉成「M月D日上午H點xx分」格式
	month, day, meridiem, hour, minute = match.groups()
	minute_text = "整" if minute == "00" else f"{int(minute)}分"
	return f"{int(month)}月{int(day)}日{meridiem}{int(hour)}點{minute_text}"

def remove_timestamps(text):
	# 移除 YouTube 留言中的時間軸標記 (mm:ss 或 h:mm:ss)
	return TIME_RE.sub('', text if isinstance(text, str) else '')

def remove_emoji(text):
	# 移除表情符號
	return emoji.replace_emoji(text if isinstance(text, str) else '', replace='')

def remove_url(text):
	# 移除網址
	return URL_RE.sub('', text if isinstance(text, str) else '')

def remove_special_chars(text):
	# 移除特殊符號，只留中英文、數字和基本標點
	return SPECIAL_RE.sub('', text if isinstance(text, str) else '')

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

def remove_extra_whitespace(text):
	# 去除多餘空白
	return WHITESPACE_RE.sub(' ', text if isinstance(text, str) else '').strip()