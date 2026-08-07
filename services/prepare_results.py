import json
from pathlib import Path


FIXTURE_SEPARATOR = " - "
SCORE_SEPARATOR = "-"


def _split_fixture(fixture: str) -> tuple[str, str]:
    home, away = [
        team.strip()
        for team in fixture.split(FIXTURE_SEPARATOR, maxsplit=1)
    ]
    return home, away


def _split_score(score: str) -> tuple[int, int]:
    home_score, away_score = [
        int(value.strip())
        for value in score.split(SCORE_SEPARATOR, maxsplit=1)
    ]
    return home_score, away_score


def _calculate_winner(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home"
    if home_score < away_score:
        return "away"
    return "draw"


def parse_results(results: dict) -> dict:
    fixtures = {}

    for fixture, score in results.items():
        home_team, away_team = _split_fixture(fixture)
        home_score, away_score = _split_score(score)

        fixtures[fixture] = {
            "fixture": fixture,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "winner": _calculate_winner(home_score, away_score),
        }

    #print(f"Found {len(fixtures)} fixtures from results")
    return fixtures


def save_week_results(
    results: dict,
    week_id: str,
    output_dir: str = "data/predictions",
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed_results = parse_results(results)
    week_data = {
        "week_id": week_id,
        "fixtures": list(results.keys()),
        "results": parsed_results,
        "total_results_saved": len(parsed_results),
        "comments": [],
    }

    output_path = output_dir / f"gameweek_{week_id}_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(week_data, file, indent=2, ensure_ascii=False)

    return output_path


def add_fixtures_to_json(fixtures: dict, filename: str) -> None:
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["results"] = fixtures

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    #print(f"Updated {filename} with {len(fixtures)} game results")
