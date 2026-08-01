import json
import pandas as pd

from src.utils import save_dataframe_to_csv

def parse_weekly_json(file_path: str) -> tuple:
    from utils import load_json
    """
    Parses the weekly JSON data and returns the results and comments.
    """
    # TODO: Add error handling for file not found or invalid JSON
    # TODO: Add validation for the structure of the JSON data
    # TODO: Add logging for the number of results and comments loaded
    # TODO: Add a check for empty results or comments and handle accordingly
    # TODO: unify data folders and path structure for easier access and management of weekly data
    data = load_json(file_path)
    filename = file_path.split("/")[-1]

    results = data["results"]
    comments = data["comments"]
    
    print(f"Loaded {len(results)} results from {filename}")
    print(f"Loaded {len(comments)} comments from {filename}")

    return results, comments

def predictions_to_dataframe(predictions: dict) -> pd.DataFrame:
    rows = []

    for comment in predictions:
        comment_data = {
            "comment_id": comment["comment_id"],
            "author": comment["author"],
            "published_at": comment["published_at"],
        }

        for fixture, pred in comment["predictions"].items():
            rows.append({
                **comment_data,
                **pred,
            })

    df_predictions = pd.DataFrame(rows)
    print(f"Loaded {len(df_predictions)} results into DataFrame")
    return df_predictions

def results_to_dataframe(results: dict) -> pd.DataFrame:
    result_keys = [
    "fixture",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "winner",
    ]

    df_results = pd.DataFrame([
        {key: result.get(key) for key in result_keys}
        for result in results.values()
    ])
    print(f"Loaded {len(df_results)} results into DataFrame")
    return df_results

def calculate_points(predictions_df: pd.DataFrame, results_df: pd.DataFrame):
    # list unique authors
    unique_authors = predictions_df['author'].unique()

    # empty dictionary to store points for each author

    author_points = {}



    for author in unique_authors:
        points = 0
        # compare matches for each author with the results dataframe, use fixture as the key of comparison and increase counter by 5 if winner is the same, and by 10 if home_score and away_score are also the same
        author_predictions = predictions_df[predictions_df['author'] == author]

        for index, row in author_predictions.iterrows():
            #print(f"Author: {author}, Fixture: {row['fixture']}, Predicted Winner: {row['winner']}, Predicted Home Score: {row['home_score']}, Predicted Away Score: {row['away_score']}")
            # compare with results dataframe
            # match fixtures in results and current row
            result_row = results_df[results_df['fixture'] == row['fixture']]
            if not result_row.empty:
                result_row = result_row.iloc[0]
                if row['winner'] == result_row['winner']:
                    points += 5
                    if row['home_score'] == result_row['home_score'] and row['away_score'] == result_row['away_score']:
                        points += 5

        # save points for each author in the dictionary
        author_points[author] = points
        print(f"Author: {author}, Points: {points}")

    # save author points to csv
    author_points_df = pd.DataFrame(list(author_points.items()), columns=['author', 'points'])

    #TODO: make the filename and path dynamic based on the week number, for now hardcoded to 2026_week_06_author_points.csv
    csv_path = "data/week_06/2026_week_06_author_points.csv"
    save_dataframe_to_csv(author_points_df, csv_path)


