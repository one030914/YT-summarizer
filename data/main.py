from APIComments import API
from Preprocess import batch_preprocess_comments
from pathlib import Path
import os

if __name__ == "__main__":
    out_path = Path('./data/datasets/english')
    os.makedirs(out_path, exist_ok=True)
    video_url = input()
    max_comments = 10000000
    pages = 10
    min_likes = 1
    
    video_id = API().extract_video_id(url=video_url)
    comments = API().get_comments(url=video_url, max_comments=max_comments, pages=pages, min_likes=min_likes)
    df = batch_preprocess_comments(comments)
    df.to_csv( out_path / f'{video_id}.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 輸出到：{out_path}")