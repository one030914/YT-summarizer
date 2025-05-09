import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os
import pandas as pd
import socket
import sys
from pathlib import Path

load_dotenv(verbose=True)
API_KEY     = os.getenv("API_KEY") # 你的 API 金鑰
VIDEO_ID    = "" # 換成實際的影片 ID
MAX_RESULTS = 100           # 一頁最多取 100 筆
PAGE_LIMIT  = 5             # 最多拉 5 頁就停（視需求調整）

# 1. 建立帶逾時設定的 HTTP 物件
http = httplib2.Http(timeout=10)  # 10 秒逾時
# 2. 把 http 傳給 build，API 呼叫就會有逾時機制
youtube = build("youtube", "v3", developerKey=API_KEY, http=http)

comments = []
next_page_token = None
page_count = 0

while True:
    page_count += 1
    if page_count > PAGE_LIMIT:
        print(f"已達頁數上限 {PAGE_LIMIT}，提前結束")
        break

    try:
        response = (
            youtube.commentThreads()
                   .list(
                       part="snippet",
                       videoId=VIDEO_ID,
                       maxResults=MAX_RESULTS,
                       pageToken=next_page_token,
                       textFormat="plainText"
                   )
                   .execute()
        )
    except HttpError as e:
        print(f"HTTP 錯誤：{e.status_code}，{e.error_details}")
        break
    except socket.timeout:
        print("網路逾時（timeout），請稍後再試")
        break
    except Exception as e:
        print(f"其他錯誤：{e}")
        break

    for item in response["items"]:
        top = item["snippet"]["topLevelComment"]
        s   = top["snippet"]
        comments.append({
            "threadId":    item["id"],
            "commentId":   top["id"],
            "author":      s["authorDisplayName"],
            "text":        s["textDisplay"],
            "publishedAt": s["publishedAt"],
            "likeCount":   s.get("likeCount", 0),
            "replyCount":  item["snippet"].get("totalReplyCount", 0)
        })

    next_page_token = response.get("nextPageToken")
    if not next_page_token:
        break

# 輸出 CSV
out_dir = Path('APItoCSV')
df = pd.DataFrame(comments)
df.to_csv( out_dir/"youtube_comments.csv", index=False, encoding="utf-8-sig")
print(f"已匯出 {len(df)} 筆留言到 youtube_comments.csv")
