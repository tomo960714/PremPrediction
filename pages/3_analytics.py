import streamlit as st

from services.leaderboard import add_new_week_to_leaderboard, open_leaderboard_csv, save_leaderboard_csv
from services.prepare_results import save_week_results
from services.scoring import calculate_points, load_predictions_json, load_results_json, predictions_to_dataframe, results_to_dataframe
from services.temp_data_sources import get_weekly_results
from services.utils import load_dataframe_from_csv,load_season_id,load_week_id
from services.components import week_input, season_input
st.title("Analytics Page")

 

# make results.json

def save_results_json(week_id: str, season: str):
    # get the weekly result data

    #print(f"Saving results JSON for week {week_id} of season {season}")
    results = get_weekly_results(week_id)
    ourput_dir = save_week_results(
        results=results,
        week_id=week_id,
        output_dir=f"data/raw/{season}",
    )
    return ourput_dir


def score():

    default_path =f"data/raw/{season_id}/gameweek_{week_id}"
    results = load_results_json(default_path + f"_results.json")
    predictions = load_predictions_json(default_path + f"_predictions.json")
    predictions_df = predictions_to_dataframe(predictions)
    results_df = results_to_dataframe(results)
    leaderboard_df = calculate_points(predictions_df, results_df,csv_path=default_path + f"_leaderboard.csv")
    return leaderboard_df

def save_weekly_leaderboard(leaderboard_df):
    save_leaderboard_csv(leaderboard_df, season_id)
    st.write(f"Weekly leaderboard saved for week {week_id} of season {season_id}")

#TODO: load week and season from sidebar
week_id = load_week_id()
season_id = load_season_id()

if st.button("Save Results JSON"):
    save_results_json(week_id, season_id)
    st.write(f"Results JSON saved for week {week_id} of season {season_id}")



if st.button("Score Predictions"):
    st.write(f"Scoring predictions for week {week_id} of season {season_id}")
    leaderboard_df = score()
    st.write(" Weekly Leaderboard:")
    st.dataframe(leaderboard_df)


if st.button("Add to Leaderboard"):
    st.write(f"Adding week {week_id} results to the leaderboard for season {season_id}")
    # open the weekly leaderboard CSV
    weekly_leaderboard = load_dataframe_from_csv(f"data/raw/{season_id}/gameweek_{week_id}_leaderboard.csv")

    # Load the existing leaderboard
    existing_leaderboard_df = open_leaderboard_csv(season_id)
    # Add the new week to the leaderboard
    updated_leaderboard_df = add_new_week_to_leaderboard(existing_leaderboard_df, weekly_leaderboard)
    # Save the updated leaderboard
    save_weekly_leaderboard(updated_leaderboard_df)
    save_leaderboard_csv(updated_leaderboard_df, season_id)