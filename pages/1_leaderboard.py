import streamlit as st

from services.leaderboard import open_leaderboard_csv
from services.utils import load_season_id

st.title("Leaderboard")

## Display the leaderboard 
# TODO: Implement the leaderboard display logic.
season_id = load_season_id()
# Load the leaderboard data
leaderboard_df = open_leaderboard_csv(season_id)

if leaderboard_df.empty:
    st.write("No leaderboard data available for this season.")
else:
    st.dataframe(leaderboard_df)