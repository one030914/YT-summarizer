import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs

load_dotenv(verbose=True)
api_key = os.getenv("API_KEY")
youtube = build("youtube", "v3", developerKey=api_key)

def get_title(url: str) -> str:
    """
    取得影片標題
    :param video_id: 影片ID
    :return: 影片標題
    """
    video_id = extract_video_id(url)
    if not video_id:
        return None
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response["items"][0]["snippet"]["title"]


def extract_video_id(url: str) -> str:
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

if __name__ == "__main__":
    url = "11"
    title = get_title(url)
    print(f"Video Title: {title}")