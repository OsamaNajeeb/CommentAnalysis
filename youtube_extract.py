
"""
youtube_comments_extract.py
Extracts: Video Name, Channel Name, Username (commenter), Comment text, Likes
Requires: google-api-python-client, pandas
pip install google-api-python-client pandas
"""

import os
import sys
import pandas as pd
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build

# Prefer environment variable for safety. You can set YT_API_KEY or hardcode (not recommended).
API_KEY = os.getenv("YT_API_KEY", None)  # set YT_API_KEY env var, e.g. export YT_API_KEY="..." on Unix
if not API_KEY:
    # fallback: if you insist on hardcoding, put it here (not recommended)
    API_KEY = "AIzaSyBcAh0fh2UmK92MnHbb_yxQxbwIBGW1YQM"

def get_video_id_from_url(url_or_id: str) -> str | None:
    """Return video id from a full URL or return the string if already an id."""
    if not url_or_id:
        return None
    # if it already looks like an ID (11+ chars, no / or ?), return it
    if ("youtube.com" not in url_or_id and "youtu.be" not in url_or_id) and ("/" not in url_or_id and "?" not in url_or_id):
        return url_or_id.strip()

    parsed = urlparse(url_or_id)
    # youtube.com/watch?v=...
    if "youtube.com" in parsed.netloc:
        q = parse_qs(parsed.query)
        return q.get("v", [None])[0]
    # youtu.be/ID
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    return None

def get_video_details(youtube, video_id: str):
    """Get video title and channel title for given id."""
    resp = youtube.videos().list(part="snippet", id=video_id).execute()
    items = resp.get("items", [])
    if not items:
        return None
    s = items[0]["snippet"]
    return {"video_name": s.get("title", ""), "channel_name": s.get("channelTitle", "")}

def get_comments(youtube, video_id: str, max_comments: int = 1000):
    """
    Fetch top-level comments for a video up to max_comments.
    Returns list of dicts: user_name, comment_text, likes
    """
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,  # API max per page
        textFormat="plainText"
    )
    while request and len(comments) < max_comments:
        resp = request.execute()
        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "user_name": top.get("authorDisplayName", ""),
                "comment_text": top.get("textDisplay", ""),
                "likes": int(top.get("likeCount", 0)),
                "date": top.get("publishedAt", "")
            })
            if len(comments) >= max_comments:
                break
        # get next page
        request = youtube.commentThreads().list_next(previous_request=request, previous_response=resp)
    return comments

def extract_from_videos(video_inputs, output_csv="youtube_comments_simple.csv", max_comments_per_video=500):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    all_rows = []

    for entry in video_inputs:
        vid = get_video_id_from_url(entry)
        if not vid:
            print(f"[WARN] Could not parse video id from: {entry}")
            continue

        details = get_video_details(youtube, vid)
        if not details:
            print(f"[WARN] No details found for video id {vid}")
            continue

        print(f"[INFO] Processing: {details['video_name']}  (channel: {details['channel_name']})")
        comments = get_comments(youtube, vid, max_comments=max_comments_per_video)
        for c in comments:
            all_rows.append({
                "Video Name": details["video_name"],
                "Channel Name": details["channel_name"],
                "User Name": c["user_name"],
                "Comment": c["comment_text"],
                "Likes": c["likes"],
                "Date": c["date"]
            })
        print(f"[INFO] Fetched {len(comments)} comments for video id {vid}")

    if not all_rows:
        print("[INFO] No data collected.")
        return

    df = pd.DataFrame(all_rows)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[DONE] Saved {len(df)} rows to {output_csv}")

if __name__ == "__main__":
    # You can provide a list here, or pass file path(s) as command line arguments
    # Example: python youtube_comments_extract.py https://www.youtube.com/watch?v=abc123 https://youtu.be/xyz456
    if len(sys.argv) > 1:
        inputs = sys.argv[1:]
    else:
        # default list - replace or edit
        inputs = [
            "https://www.youtube.com/watch?v=h8Tsiefa_Bo",
            "https://www.youtube.com/watch?v=QmIgSYALo2k",
            "https://www.youtube.com/watch?v=4bskZYoO0N0",
            "https://www.youtube.com/watch?v=bt0zJCMjrB8",
            "https://www.youtube.com/watch?v=bt0zJCMjrB8"
            "4bskZYoO0N0"  # you can use direct IDs as well
        ]

    # adjust as needed
    extract_from_videos(inputs, output_csv="youtube_comments_simple.csv", max_comments_per_video=200)
