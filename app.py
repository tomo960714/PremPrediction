from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from services.utils import get_current_season




st.set_page_config(
    #page_title="PremPrediction",
    page_icon="⚽",
    layout="wide",
)

home_page = st.Page(
    "pages/0_home.py",
    title="Home",
    icon="🏠",
    default=True,
)

leaderboard_page = st.Page(
    "pages/1_leaderboard.py",
    title="Leaderboard",
    icon="📊",
)

comments_page = st.Page(
    "pages/2_youtube_comments.py",
    title="Comments",
    icon="💬",
)

analytics_page = st.Page(
    "pages/3_analytics.py",
    title="Analytics",
    icon="📈",
)

admin_page = st.Page(
    "pages/4_admin.py",
    title="Admin",
    icon="🔒",
)

selected_pages = st.navigation(
    [home_page, leaderboard_page, comments_page, analytics_page, admin_page],
)


st.sidebar.text_input(
    "Game Week:",
    key = "week_id"
)




st.sidebar.text_input(
    "Season:",
    key = "season_id",
    value=get_current_season()
)

load_dotenv()
env_state = os.getenv("APP_ENV")

if env_state == "local":
    local_api_key = os.getenv("YOUTUBE_API_KEY")
    if local_api_key:
        st.session_state["api_key"] = local_api_key
    else:
        # deployed prototype
        st.sidebar.text_input(
            "YouTube API key:",
            type="password",
            key = "api_key"
        )
else:
    # deployed prototype
    st.sidebar.text_input(
        "YouTube API key:",
        type="password",
        key = "api_key"
    )


selected_pages.run()

def normalize_team_name(value: object) -> str:
    return str(value).replace("_", " ")
