import streamlit as st

def week_input(page_name:str, write_enable: bool = False):
    if "week_id" not in st.session_state:
        st.session_state["week_id"] = ""

    # each page needs a unique widget key
    widget_key = f"week_id_{page_name}"

    # load current shared value into current page's widget
    st.session_state[widget_key] = st.session_state["week_id"]

    def save_week():
        st.session_state["week_id"] = st.session_state[widget_key]

    if write_enable:
        st.text_input(
            "Gameweek",
            key = widget_key,
            on_change = save_week,
        )

    return st.session_state["week_id"]

def season_input(page_name:str, write_enable: bool = False):
    if "season_id" not in st.session_state:
        st.session_state["season_id"] =""

    # each page needs a unique widget key
        widget_key = f"season_id_{page_name}"
    
        # load current shared value into current page's widget
        st.session_state[widget_key] = st.session_state["season_id"]
    
        def save_season():
            st.session_state["season_id"] = st.session_state[widget_key]

        if write_enable:
            st.text_input(
                "Season",
                key = widget_key,
                on_change = save_season,
            )
    
        return st.session_state["season_id"]