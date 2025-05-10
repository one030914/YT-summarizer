from keybert import KeyBERT
import jieba

# 初始化 KeyBERT 模型（支援中英文）
model = KeyBERT('paraphrase-multilingual-MiniLM-L12-v2')

# 假設有很多條留言
comments = [
    'keshi是我最喜歡的歌手',
    '這首歌旋律太好聽了',
    '他的聲音真的超治癒',
    '聽到這首歌就想跳舞',
    '旋律好輕快',
    '唱功超級厲害',
    'e04',
    '我不喜歡這個歌手',
    '我討厭這首歌',
    '我喜歡這歌 但我討厭歌手'
]

# 對每條留言提取關鍵詞
for i, text in enumerate(comments):
    tokens = list(jieba.cut(text))
    segmented_text = " ".join(tokens)
    keywords = model.extract_keywords(segmented_text, keyphrase_ngram_range=(1, 1), top_n=3)
    
    # 只印關鍵詞，不印分數
    keyword_list = [kw for kw, score in keywords]
    print(f"留言 {i+1}: {text}")
    print(f"➡️ 關鍵詞：{keyword_list}\n")
