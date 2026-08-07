import json
import re
from pathlib import Path

import requests


YOUTUBE_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
FIXTURE_SEPARATOR = " - "
SCORE_PATTERN = re.compile(r"\b\d{1,2}\b")


def _split_fixture(fixture: str) -> tuple[str, str]:
    home, away = [
        team.strip()
        for team in fixture.split(FIXTURE_SEPARATOR, maxsplit=1)
    ]
    return home, away


def _calculate_winner(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home"
    if home_score < away_score:
        return "away"
    return "draw"


def _empty_prediction(fixture: str, home_team: str, away_team: str) -> dict:
    return {
        "fixture": fixture,
        "found": False,
        "prediction": None,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": None,
        "away_score": None,
        "winner": None,
    }


def _format_prediction(result: dict) -> dict:
    return {
        "fixture": result["fixture"],
        "found": True,
        "prediction": f"{result['home_score']}-{result['away_score']}",
        "home_team": result["home_team"],
        "away_team": result["away_team"],
        "home_score": result["home_score"],
        "away_score": result["away_score"],
        "winner": result["winner"],
    }


def get_all_comments(video_id: str, api_key: str) -> list:
    """Fetch all top-level comments for a YouTube video."""
    comments = []
    page_token = None

    while True:
        params = {
            "key": api_key,
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "order": "time",
            "textFormat": "plainText",
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(YOUTUBE_COMMENTS_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        for thread in data.get("items", []):
            comment = thread["snippet"]["topLevelComment"]
            snippet = comment["snippet"]

            comments.append({
                "id": comment["id"],
                "author": snippet.get("authorDisplayName"),
                "text": snippet.get("textDisplay"),
                "likes": snippet.get("likeCount", 0),
                "published_at": snippet.get("publishedAt"),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return comments


def parse_weekly_games(weekly_games: list) -> dict:
    fixtures = {}

    for fixture in weekly_games:
        home, away = _split_fixture(fixture)
        fixtures[frozenset([home, away])] = {
            "fixture": fixture,
            "home_team": home,
            "away_team": away,
        }

    return fixtures


def find_team_mentions_in_text(text: str, teams: dict) -> list:
    results = []

    for team, aliases in teams.items():
        for alias in aliases:
            alias_text = alias.replace("_", " ")
            pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(alias_text)
                + r"(?![A-Za-z0-9])"
            )

            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                results.append({
                    "team": team,
                    "alias": alias,
                    "matched_text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                })

    return sorted(results, key=lambda mention: mention["start"])


def find_numbers_in_line(line: str) -> list:
    return [
        {
            "value": int(match.group()),
            "start": match.start(),
            "end": match.end(),
        }
        for match in SCORE_PATTERN.finditer(line)
    ]


def _deduplicate_team_mentions(mentions: list) -> list:
    seen = set()
    team_mentions = []

    for mention in mentions:
        if mention["team"] in seen:
            continue

        seen.add(mention["team"])
        team_mentions.append(mention)

    return team_mentions


def _next_number_after_mention(numbers: list, mention: dict) -> dict | None:
    return next(
        (number for number in numbers if number["start"] >= mention["end"]),
        None,
    )


def _scores_by_team(team_mentions: list, numbers: list) -> dict | None:
    scores = {}

    for mention in team_mentions:
        score = _next_number_after_mention(numbers, mention)
        if score is None:
            return None

        scores[mention["team"]] = score["value"]

    return scores


def find_fixture_scores(comment: dict, teams: dict, weekly_games: list) -> list:
    text = comment.get("text", "") if isinstance(comment, dict) else str(comment)
    fixtures = parse_weekly_games(weekly_games)
    results = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        team_mentions = _deduplicate_team_mentions(
            find_team_mentions_in_text(line, teams)
        )

        if len(team_mentions) != 2:
            continue

        first, second = team_mentions
        pair = frozenset([first["team"], second["team"]])

        if pair not in fixtures:
            continue

        numbers = find_numbers_in_line(line)
        if len(numbers) < 2:
            continue

        scores = _scores_by_team(team_mentions, numbers)
        if scores is None:
            continue

        fixture = fixtures[pair]
        home_score = scores[fixture["home_team"]]
        away_score = scores[fixture["away_team"]]

        results.append({
            "fixture": fixture["fixture"],
            "home_team": fixture["home_team"],
            "away_team": fixture["away_team"],
            "home_score": home_score,
            "away_score": away_score,
            "winner": _calculate_winner(home_score, away_score),
            "line_number": line_number,
            "matched_text": line.strip(),
        })

    return results


def format_comment_predictions(
    comment: dict,
    raw_scores: list,
    weekly_games: list,
) -> dict:
    fixtures = parse_weekly_games(weekly_games)
    found_by_fixture = {score["fixture"]: score for score in raw_scores}
    predictions = {}
    missing_games = []

    for fixture in weekly_games:
        result = found_by_fixture.get(fixture)
        fixture_info = fixtures[frozenset(_split_fixture(fixture))]

        if result is None:
            missing_games.append(fixture)
            predictions[fixture] = _empty_prediction(
                fixture,
                fixture_info["home_team"],
                fixture_info["away_team"],
            )
            continue

        predictions[fixture] = _format_prediction(result)

    return {
        "comment_id": comment["id"],
        "author": comment["author"],
        "published_at": comment.get("published_at"),
        "total_games_expected": len(weekly_games),
        "total_games_found": len(weekly_games) - len(missing_games),
        "all_games_found": len(missing_games) == 0,
        "missing_games": missing_games,
        "predictions": predictions,
    }


def save_week_predictions(
    comments: list,
    dict_of_teams: dict,
    weekly_games: list,
    week_id: str,
    output_dir: str = "data/predictions",
    min_games_found: int = 3,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_comments = []

    for comment in comments:
        raw_scores = find_fixture_scores(comment, dict_of_teams, weekly_games)
        formatted_comment = format_comment_predictions(
            comment,
            raw_scores,
            weekly_games,
        )

        if formatted_comment["total_games_found"] >= min_games_found:
            saved_comments.append(formatted_comment)

    week_data = {
        "week_id": week_id,
        "fixtures": weekly_games,
        "total_comments_saved": len(saved_comments),
        "comments": saved_comments,
    }

    output_path = output_dir / f"gameweek_{week_id}_predictions.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(week_data, file, indent=2, ensure_ascii=False)

    return output_path
