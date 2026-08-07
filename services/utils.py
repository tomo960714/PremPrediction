import pandas as pd
from datetime import date
import streamlit as st
from dotenv import load_dotenv
import os


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

def save_dataframe_to_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)
    #print(f"Saved DataFrame to {filename}")

def load_dataframe_from_csv(filename: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filename)
        #print(f"Loaded DataFrame from {filename}")
        return df
    except FileNotFoundError:
        #print(f"File {filename} not found. Returning empty DataFrame.")
        return pd.DataFrame()

def get_current_season():
    today = date.today()
    if today.month < 8:
        season=f"{str(today.year-1)[-2:]}_{str(today.year)[-2:]}"
    else:
        season=f"{str(today.year)[-2:]}_{str(today.year+1)[-2:]}"

    return season

def load_week_id():

    week_id = st.session_state.get("week_id")
    if week_id is None:
        st.error("Select a game week and try again!", icon="🚨" )
    return week_id

def load_season_id():
    season_id = st.session_state.get("season_id")
    if season_id is None:
        season_id = get_current_season()
    return season_id

