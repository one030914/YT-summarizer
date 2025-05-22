import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import socket
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs

class API:
    def __init__(self):
        self.API_KEY     = "AIzaSyCJh4fHX2GS3dQaWpW6hqIdPH9Wk6Y9XvI"     # 你的 API 金鑰
        self.MAX_RESULTS = 100                                           # 一頁最多取 100 筆
        self.PAGE_LIMIT  = 5                                             # 最多拉 5 頁就停（視需求調整）
        self.MIN_LIKES = 100                                             # 按讚數最少標準

    def get_comments(self, video_url) -> list:

        VIDEO_ID = self.extract_video_id(video_url)                  # 換成實際的影片 ID
        # 1. 建立帶逾時設定的 HTTP 物件
        http = httplib2.Http(timeout=10)  # 10 秒逾時
        # 2. 把 http 傳給 build，API 呼叫就會有逾時機制
        youtube = build("youtube", "v3", developerKey=self.API_KEY, http=http)

        comments = []
        next_page_token = None
        page_count = 0

        while True:
            page_count += 1
            if page_count > self.PAGE_LIMIT:
                print(f"已達頁數上限 {self.PAGE_LIMIT}，提前結束")
                break

            try:
                response = (
                    youtube.commentThreads()
                        .list(
                            part="snippet",
                            videoId=VIDEO_ID,
                            maxResults=self.MAX_RESULTS,
                            order="relevance",
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
                text = s["textDisplay"]
                likes = s.get("likeCount", 0)
                
                if likes > self.MIN_LIKES:
                    comments.append({
                        "原留言":        s["textDisplay"],
                        "按讚數":   s.get("likeCount", 0),
                        "回覆數":  item["snippet"].get("totalReplyCount", 0)
                    })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return comments
    def extract_video_id(self, url: str) -> str:
        parsed_url = urlparse(url)

        # 處理 youtu.be 短網址
        if parsed_url.netloc == "youtu.be":
            return parsed_url.path.strip("/")

        # 處理 youtube.com/watch?v=xxxx
        if parsed_url.path == "/watch":
            query = parse_qs(parsed_url.query)
            return query.get("v", [None])[0]

        # 處理其他可能格式（如嵌入）
        match = re.search(r"(?:v=|\/embed\/|\/v\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)

        return None
'''
if __name__ == "__main__":
    # 輸出 CSV
    out_dir = Path('LAST/CSV')
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(comments)
    df.to_csv( out_dir/ f'{VIDEO_ID}.csv', index=False, encoding="utf-8-sig")
    print(f"已匯出 {len(df)} 筆留言到 {VIDEO_ID}.csv")
'''