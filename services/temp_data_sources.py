def get_teams()-> dict:
    # Returns a dictionary mapping team names to their possible variations.
    # very temporary solution, will be replaced with a more robust solution in the future
    dict_of_teams = {
        "Arsenal": ["Arsenal"],
        "Aston_Villa": ["Aston_Villa","Villa"],
        "Bournemouth": ["Bournemouth"],
        "Brentford": ["Brentford"],
        "Brighton": ["Brighton"],
        "Burnley": ["Burnley"],
        "Chelsea": ["Chelsea"],
        "Crystal_Palace": ["Crystal_Palace", "Palace"],
        "Everton": ["Everton"],
        "Fulham": ["Fulham"],
        "Leeds": ["Leeds_United", "Leeds"],
        "Liverpool": ["Liverpool", "Pool"],
        "Manchester_City": ["Manchester City", "Man City"],
        "Manchester_United": ["Manchester United", "MU", "Man United"],
        "Newcastle": ["Newcastle United", "Newcastle", "Newcastle Utd"],
        "Nottingham_Forest": ["Nottingham Forest","Nottingham", "Forest"],
        "Sunderland": ["Sunderland"],
        "Tottenham": ["Tottenham Hotspurs","Tottenham", "Spurs"],
        "West_Ham": ["West Ham"],
        "Wolves": ["Wolverhampton Wanderers", "Wolves", "Wolverhampton"],
    }
    return dict_of_teams

def get_weekly_matches(gameweek:str = "25") -> list:
    # Returns a list of matches for the current week.
    # very temporary solution, will be replaced with a more robust solution in the future
    match gameweek:
        case "25":
            weekly_matches = [
                "Leeds - Nottingham_Forest",
                "Manchester_United - Tottenham",
                "Bournemouth - Aston_Villa",
                "Arsenal - Sunderland",
                "Burnley - West_Ham",
                "Fulham - Everton",
                "Wolves - Chelsea",
                "Newcastle - Brentford",
                "Brighton - Crystal_Palace",
                "Liverpool - Manchester_City"
            ]
        case "26":
            weekly_matches = [
                    "Chelsea - Leeds",
                    "Everton - Bournemouth",
                    "Tottenham - Newcastle",
                    "West_Ham - Manchester_United",
                    "Aston_Villa - Brighton",
                    "Crystal_Palace - Burnley",
                    "Manchester_City - Fulham",
                    "Nottingham_Forest - Wolves",
                    "Sunderland - Liverpool",
                    "Brentford - Arsenal",
            ]

    return weekly_matches

def get_weekly_results(gameweek:str = "25") -> dict:
    match gameweek:
        case "25":
            results = {
                "Leeds - Nottingham_Forest": "3-1",
                "Manchester_United - Tottenham": "2-0",
                "Bournemouth - Aston_Villa":"1-1",
                "Arsenal - Sunderland":"3-0",
                "Burnley - West_Ham":"0-2",
                "Fulham - Everton":"1-2",
                "Wolves - Chelsea":"1-3",
                "Newcastle - Brentford":"2-3",
                "Brighton - Crystal_Palace":"0-1",
                "Liverpool - Manchester_City":"1-2"
                }
        case "26":
            results = {
                "Chelsea - Leeds":"2-2",
                "Everton - Bournemouth":"1-2",
                "Tottenham - Newcastle":"1-2",
                "West_Ham - Manchester_United":"1-1",
                "Aston_Villa - Brighton":"1-0",
                "Crystal_Palace - Burnley":"2-3",
                "Manchester_City - Fulham":"3-0",
                "Nottingham_Forest - Wolves":"0-0",
                "Sunderland - Liverpool":"0-1",
                "Brentford - Arsenal":"1-1",
            }
    return results