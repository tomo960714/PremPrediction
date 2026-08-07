import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

try:
    from .utils import save_dataframe_to_csv
except ImportError:
    from utils import save_dataframe_to_csv


RESULT_COLUMNS = [
    "fixture",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "winner",
]


@dataclass(frozen=True)
class ScoringRules:
    winner_points: int = 5
    exact_score_points: int = 10


DEFAULT_SCORING_RULES = ScoringRules()

def load_predictions_json(file_path: str) -> list[dict]:
    """
    Loads a JSON file containing weekly predictions data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = Path(file_path).name

    predictions = data["comments"]
    #print(f"Loaded {len(predictions)} predictions from {filename}")

    return predictions


def load_results_json(file_path: str) -> dict:
    """
    Loads a JSON file containing weekly results data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = Path(file_path).name

    results = data["results"]
    #print(f"Loaded {len(results)} results from {filename}")

    return results


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
    #print(f"Loaded {len(df_predictions)} results into DataFrame")
    return df_predictions


def results_to_dataframe(results: dict) -> pd.DataFrame:
    df_results = pd.DataFrame([
        {key: result.get(key) for key in RESULT_COLUMNS}
        for result in results.values()
    ])
    #print(f"Loaded {len(df_results)} results into DataFrame")
    return df_results


def _is_correct_winner(prediction: pd.Series, result: pd.Series) -> bool:
    return prediction["winner"] == result["winner"]


def _is_exact_score(prediction: pd.Series, result: pd.Series) -> bool:
    return (
        prediction["home_score"] == result["home_score"]
        and prediction["away_score"] == result["away_score"]
    )


def calculate_prediction_points(
    prediction: pd.Series,
    result: pd.Series,
    scoring_rules: ScoringRules = DEFAULT_SCORING_RULES,
) -> int:
    if not _is_correct_winner(prediction, result):
        return 0

    if _is_exact_score(prediction, result):
        return scoring_rules.exact_score_points

    return scoring_rules.winner_points


def score_predictions(
    predictions_df: pd.DataFrame,
    results_df: pd.DataFrame,
    scoring_rules: ScoringRules = DEFAULT_SCORING_RULES,
) -> pd.DataFrame:
    results_by_fixture = results_df.set_index("fixture")
    rows = []

    for _, prediction in predictions_df.iterrows():
        fixture = prediction["fixture"]

        if fixture not in results_by_fixture.index:
            points = 0
        else:
            points = calculate_prediction_points(
                prediction,
                results_by_fixture.loc[fixture],
                scoring_rules,
            )

        rows.append({
            **prediction.to_dict(),
            "points": points,
        })

    scored_predictions_df = pd.DataFrame(rows)
    #print(f"Scored {len(scored_predictions_df)} predictions")
    return scored_predictions_df


def summarize_author_points(scored_predictions_df: pd.DataFrame) -> pd.DataFrame:
    author_points_df = (
        scored_predictions_df
        .groupby("author", as_index=False)["points"]
        .sum()
        .sort_values(["points", "author"], ascending=[False, True])
        .reset_index(drop=True)
    )

    #print(f"Calculated points for {len(author_points_df)} authors")
    return author_points_df


def calculate_points(
    predictions_df: pd.DataFrame,
    results_df: pd.DataFrame,
    scoring_rules: ScoringRules = DEFAULT_SCORING_RULES,
    csv_path: str | None = None,
) -> pd.DataFrame:
    scored_predictions_df = score_predictions(
        predictions_df,
        results_df,
        scoring_rules,
    )
    author_points_df = summarize_author_points(scored_predictions_df)

    if csv_path is not None:
        save_dataframe_to_csv(author_points_df, csv_path)

    return author_points_df
