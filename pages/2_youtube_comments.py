from anyio import Path
import streamlit as st
import dotenv

from services.prediction import get_all_comments, save_week_predictions
from services.utils import get_video_id_from_url, load_season_id, load_week_id
from services.temp_data_sources import get_teams, get_weekly_matches
from services.components import week_input



st.title("Comment Collector")

video_url = st.text_input("Video URL", key="video_url", persist_state ="session")

#TODO: load week and season from sidebar
week_id = load_week_id()
season_id = load_season_id()


if st.button("Collect Comments"):
    # TODO: season is hard coded for now, but should be set in the admin page
    # TODO: run colelction sevice and have a progress bar and 
    st.write(f"Collecting comments for video: {video_url}")
    season_id = st.session_state.get("season_id")  # Default season if not set
    week_id = st.session_state.get("week_id")  # Default week if not set

    # Extract video ID from the URL
    video_id = get_video_id_from_url(video_url)

    # Load API key from environment variable
    #api_key = st.secrets["YOUTUBE_API_KEY"]
    # temp for testing, load from .env file
    # check if .env exists


    api_key = st.session_state["api_key"]

    # Fetch comments using the YouTube comment collector service
    comments = get_all_comments(video_id, api_key)
    st.write(f"Collected {len(comments)} comments for video ID: {video_id}")

    # TODO: Temp hardcoding for week_id, teams, and weekly_games.

    dict_of_teams = get_teams()
    weekly_games = get_weekly_matches(week_id)
    

    output_path = save_week_predictions(
            comments=comments,
            dict_of_teams=dict_of_teams,
            weekly_games=weekly_games,
            week_id=week_id,
            output_dir=f"data/raw/{season_id}",
        )
    st.write(f"Predictions saved to: {output_path}")



