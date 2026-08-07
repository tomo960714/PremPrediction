import streamlit as st

st.title("Home Page")

if st.button("Go to Leaderboard"):
    st.switch_page("pages/1_leaderboard.py")

if st.button("Go to Comment Collector"):
    st.switch_page("pages/2_youtube_comments.py")

if st.button("Go to Analytics"):
    st.switch_page("pages/3_analytics.py")

if st.button("Go to Admin"):
    st.switch_page("pages/4_admin.py")