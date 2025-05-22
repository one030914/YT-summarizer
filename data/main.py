from APIComments import API
from Preprocess import batch_preprocess_comments
from pathlib import Path

if __name__ == "__main__":
    out_path = Path('LAST/CSV')
    video_url = input()
    video_id = API().extract_video_id(video_url)
    comments = API().get_comments(video_url)
    df = batch_preprocess_comments(comments)
    df.to_csv( out_path / f'{video_id}.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 輸出到：{out_path}")