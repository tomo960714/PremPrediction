import requests
from dotenv import load_dotenv
import os
import re
import json
from pathlib import Path

def get_all_comments(video_id: str, api_key: str) -> list:
    """
    Fetches all comments for a given YouTube video ID using the YouTube Data API.

    Args:
        video_id (str): The YouTube video ID.
        api_key (str): The API key for accessing the YouTube Data API.

    Returns:
        list: A list of comments.
    """
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    comments = []
    page_token = None
    while True:
        params = {
            "key": api_key,
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "order": "time",
            "textFormat": "plainText",
        }
    
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        for thread in data.get("items", []):
            comment = thread["snippet"]["topLevelComment"]
            snippet = comment["snippet"]

            comments.append({
                "id": comment["id"],
                "author": snippet.get("authorDisplayName"),
                "text": snippet.get("textDisplay"),
                "likes": snippet.get("likeCount", 0),
                "published_at": snippet.get("publishedAt"),
            })

        page_token = data.get("nextPageToken")

        if not page_token:
            break
    
    return comments