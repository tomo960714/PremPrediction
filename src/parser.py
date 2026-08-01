from pathlib import Path
import re
import json

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

    return sorted(results, key=lambda x: x["start"])

def parse_weekly_games(weekly_games: list) -> dict:
    fixtures = {}

    for game in weekly_games:
        home, away = [x.strip() for x in game.split(" - ")]
        fixtures[frozenset([home, away])] = {
            "fixture": game,
            "home_team": home,
            "away_team": away,
        }

    return fixtures

def find_numbers_in_line(line: str) -> list:
    matches = []

    for match in re.finditer(r"\b\d{1,2}\b", line):
        matches.append({
            "value": int(match.group()),
            "start": match.start(),
            "end": match.end(),
        })

    return matches

def find_fixture_scores(comment: dict, teams: dict, weekly_games: list) -> list:
    text = comment["text"] if isinstance(comment, dict) else comment
    fixtures = parse_weekly_games(weekly_games)

    results = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        mentions = find_team_mentions_in_text(line, teams)

        # Deduplicate teams in same line
        seen = set()
        team_mentions = []

        for mention in mentions:
            if mention["team"] not in seen:
                seen.add(mention["team"])
                team_mentions.append(mention)

        if len(team_mentions) != 2:
            continue

        first, second = team_mentions
        pair = frozenset([first["team"], second["team"]])

        if pair not in fixtures:
            continue

        numbers = find_numbers_in_line(line)

        if len(numbers) < 2:
            continue

        fixture = fixtures[pair]

        # Assign scores based on nearest number after each team mention
        first_score = next(
            (n for n in numbers if n["start"] >= first["end"]),
            None
        )
        second_score = next(
            (n for n in numbers if n["start"] >= second["end"]),
            None
        )

        if first_score is None or second_score is None:
            continue

        scores_by_team = {
            first["team"]: first_score["value"],
            second["team"]: second_score["value"],
        }

        # find the winner based on the scores
        if scores_by_team[first["team"]] > scores_by_team[second["team"]]:
            winner = "home"
        elif scores_by_team[first["team"]] < scores_by_team[second["team"]]:
            winner = "away"
        else:
            winner = "draw"

        results.append({
            "fixture": fixture["fixture"],
            "home_team": fixture["home_team"],
            "away_team": fixture["away_team"],
            "home_score": scores_by_team[fixture["home_team"]],
            "away_score": scores_by_team[fixture["away_team"]],
            "winner": winner,
            "line_number": line_number,
            "matched_text": line.strip(),
        })

    return results

def format_comment_predictions(comment: dict, raw_scores: list, weekly_games: list) -> dict:
    expected_fixtures = set(weekly_games)
    fixtures = parse_weekly_games(weekly_games)

    found_by_fixture = {
        score["fixture"]: score
        for score in raw_scores
    }

    predictions = {}
    missing_games = []

    for fixture in weekly_games:
        result = found_by_fixture.get(fixture)
        fixture_info = fixtures[frozenset(fixture.split(" - "))]

        if result is None:
            missing_games.append(fixture)
            predictions[fixture] = {
                "fixture": fixture,
                "found": False,
                "prediction": None,
                "home_team": fixture_info["home_team"],
                "away_team": fixture_info["away_team"],
                "home_score": None,
                "away_score": None,
                "winner": None,
            }
            continue

        predictions[fixture] = {
            "fixture": fixture,
            "found": True,
            "prediction": f"{result['home_score']}-{result['away_score']}",
            "home_team": result["home_team"],
            "away_team": result["away_team"],
            "home_score": result["home_score"],
            "away_score": result["away_score"],
            "winner": result["winner"],
        }

    return {
        "comment_id": comment["id"],
        "author": comment["author"],
        "published_at": comment.get("published_at"),
        "total_games_expected": len(expected_fixtures),
        "total_games_found": len(expected_fixtures) - len(missing_games),
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
        readable_comment = format_comment_predictions(
            comment,
            raw_scores,
            weekly_games
        )

        if readable_comment["total_games_found"] >= min_games_found:
            saved_comments.append(readable_comment)

    week_data = {
        "week_id": week_id,
        "fixtures": weekly_games,
        "total_comments_saved": len(saved_comments),
        "comments": saved_comments,
    }

    output_path = output_dir / f"{week_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(week_data, f, indent=2, ensure_ascii=False)

    return output_path


# Weekly games 
def parse_results (results: dict) -> dict:
    fixtures = {}
    for game in results:
        home, away = [x.strip() for x in game.split(" - ")]
        home_score, away_score = [int(x) for x in results[game].split("-")]
        if home_score > away_score:
            winner = "home"
        elif home_score < away_score:
            winner = "away"
        else:
            winner = "draw"

        fixtures[game] = {
            "fixture": game,
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
            "winner": winner,

        }

    print(f"Parsed {len(fixtures)} fixtures from results")
    return fixtures

def add_fixtures_to_json(fixtures, filename):
    # add fixtures to existing json:
    with open(filename, 'r') as f:
        data = json.load(f)
    data["results"] = fixtures
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Updated {filename} with {len(fixtures)} game results")
