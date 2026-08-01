import json
import pandas as pd
# Gets the video ID from a YouTube URL.
#
# Args:
#   url (str): The YouTube URL.
# 
# Returns:
#  str: The video ID.
#  

def get_video_id_from_url(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")


def load_json(file_path: str) -> dict:
    """
    Loads a JSON file containing weekly game data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dataframe_to_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)
    print(f"Saved DataFrame to {filename}")