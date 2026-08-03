from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


DEFAULT_DATA_DIR = Path("archive/data/predictions")


st.set_page_config(
    page_title="PremPrediction",
    page_icon="⚽",
    layout="wide",
)


@st.cache_data
def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data
def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def discover_weeks(data_dir: Path) -> list[str]:
    if not data_dir.exists():
        return []

    return sorted(
        path.stem
        for path in data_dir.glob("*.json")
        if not path.stem.endswith(("_results", "_predictions", "_author_points"))
    )


def week_paths(data_dir: Path, week_id: str) -> dict[str, Path]:
    return {
        "weekly_json": data_dir / f"{week_id}.json",
        "results": data_dir / f"{week_id}_results.csv",
        "predictions": data_dir / f"{week_id}_predictions.csv",
        "author_points": data_dir / f"{week_id}_author_points.csv",
    }


def normalize_team_name(value: object) -> str:
    return str(value).replace("_", " ")


def add_prediction_points(predictions: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    result_cols = results[
        ["fixture", "home_score", "away_score", "winner"]
    ].rename(
        columns={
            "home_score": "actual_home_score",
            "away_score": "actual_away_score",
            "winner": "actual_winner",
        }
    )

    scored = predictions.merge(result_cols, on="fixture", how="left")
    scored["outcome_points"] = (scored["winner"] == scored["actual_winner"]).astype(int) * 5
    scored["score_points"] = (
        (scored["home_score"] == scored["actual_home_score"])
        & (scored["away_score"] == scored["actual_away_score"])
    ).astype(int) * 5
    scored["points"] = scored["outcome_points"] + scored["score_points"]

    return scored


def format_score(home_score: object, away_score: object) -> str:
    if pd.isna(home_score) or pd.isna(away_score):
        return "-"

    return f"{int(home_score)}-{int(away_score)}"


def show_missing_files(paths: dict[str, Path]) -> bool:
    missing = [label for label, path in paths.items() if not path.exists()]
    if not missing:
        return False

    st.error("Missing files: " + ", ".join(missing))
    for label in missing:
        st.caption(f"{label}: {paths[label]}")
    return True


with st.sidebar:
    st.title("PremPrediction")
    data_dir_text = st.text_input("Prediction data folder", value=str(DEFAULT_DATA_DIR))
    data_dir = Path(data_dir_text)

    weeks = discover_weeks(data_dir)
    if weeks:
        default_week_index = len(weeks) - 1
        week_id = st.selectbox("Week", weeks, index=default_week_index)
    else:
        week_id = st.text_input("Week id", value="2026_week_06")

    st.divider()
    st.caption("Expected files")
    for label, path in week_paths(data_dir, week_id).items():
        st.code(f"{label}: {path}", language=None)


st.title("PremPrediction")

paths = week_paths(data_dir, week_id)
if show_missing_files(paths):
    st.stop()

weekly_data = read_json(str(paths["weekly_json"]))
results = read_csv(str(paths["results"]))
predictions = read_csv(str(paths["predictions"]))
leaderboard = read_csv(str(paths["author_points"]))
scored_predictions = add_prediction_points(predictions, results)

leaderboard = leaderboard.sort_values("points", ascending=False).reset_index(drop=True)
leaderboard.insert(0, "rank", leaderboard.index + 1)

total_comments = weekly_data.get("total_comments_saved", predictions["comment_id"].nunique())
complete_entries = int(predictions["found"].fillna(False).sum()) if "found" in predictions else 0

metric_cols = st.columns(4)
metric_cols[0].metric("Week", week_id)
metric_cols[1].metric("Fixtures", len(results))
metric_cols[2].metric("Comments", total_comments)
metric_cols[3].metric("Parsed predictions", complete_entries)

tab_leaderboard, tab_fixtures, tab_predictions, tab_data = st.tabs(
    ["Leaderboard", "Fixtures", "Predictions", "Data"]
)

with tab_leaderboard:
    st.subheader("Leaderboard")
    st.dataframe(
        leaderboard,
        use_container_width=True,
        hide_index=True,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", format="%d"),
            "author": "Author",
            "points": st.column_config.NumberColumn("Points", format="%d"),
        },
    )

with tab_fixtures:
    st.subheader("Fixture Results")
    fixture_rows = results.copy()
    fixture_rows["home_team"] = fixture_rows["home_team"].map(normalize_team_name)
    fixture_rows["away_team"] = fixture_rows["away_team"].map(normalize_team_name)
    fixture_rows["score"] = fixture_rows.apply(
        lambda row: format_score(row["home_score"], row["away_score"]),
        axis=1,
    )

    for row in fixture_rows.itertuples(index=False):
        home, score, away = st.columns([3, 1, 3])
        home.markdown(f"**{row.home_team}**")
        score.markdown(f"### {row.score}")
        away.markdown(f"**{row.away_team}**")
        st.divider()

with tab_predictions:
    st.subheader("Prediction Explorer")

    authors = ["All"] + sorted(scored_predictions["author"].dropna().unique().tolist())
    fixtures = ["All"] + sorted(scored_predictions["fixture"].dropna().unique().tolist())

    filter_cols = st.columns(3)
    selected_author = filter_cols[0].selectbox("Author", authors)
    selected_fixture = filter_cols[1].selectbox("Fixture", fixtures)
    only_scoring = filter_cols[2].toggle("Only scoring predictions")

    visible_predictions = scored_predictions.copy()
    if selected_author != "All":
        visible_predictions = visible_predictions[
            visible_predictions["author"] == selected_author
        ]
    if selected_fixture != "All":
        visible_predictions = visible_predictions[
            visible_predictions["fixture"] == selected_fixture
        ]
    if only_scoring:
        visible_predictions = visible_predictions[visible_predictions["points"] > 0]

    table = visible_predictions[
        [
            "author",
            "fixture",
            "prediction",
            "winner",
            "actual_winner",
            "points",
            "published_at",
        ]
    ].rename(
        columns={
            "author": "Author",
            "fixture": "Fixture",
            "prediction": "Prediction",
            "winner": "Predicted outcome",
            "actual_winner": "Actual outcome",
            "points": "Points",
            "published_at": "Published at",
        }
    )

    st.dataframe(table, use_container_width=True, hide_index=True)

with tab_data:
    st.subheader("Weekly JSON")
    st.json(weekly_data, expanded=False)
