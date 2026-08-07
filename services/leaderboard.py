import pandas as pd

from services.utils import save_dataframe_to_csv

# sum points for each user and sort by total points
def add_new_week_to_leaderboard(leaderboard_df: pd.DataFrame, new_week_df: pd.DataFrame) -> pd.DataFrame:
    # check if old leaderboard is empty
    if leaderboard_df.empty:
        # if empty, return new week dataframe sorted by points
        return new_week_df.sort_values(by='points', ascending=False).reset_index(drop=True)
    # match authors in the new week with the leaderboard
    leaderboard_df = pd.merge(leaderboard_df, new_week_df, on='author', how='outer', suffixes=('_old', '_new'))
    # fill NaN values with 0 for points
    
    leaderboard_df['total_points'] = leaderboard_df['points_old'].fillna(0)
    leaderboard_df['points'] = leaderboard_df['points_new'].fillna(0)
    # sum points for each user
    leaderboard_df['total_points'] = leaderboard_df['total_points'] + leaderboard_df['points']
    #print(leaderboard_df.head(1))
    # drop old and new points columns
    leaderboard_df = leaderboard_df.drop(columns=['points_old','points_new','points'])
    # sort by total points in descending order
    leaderboard_df = leaderboard_df.sort_values(by='total_points', ascending=False).reset_index(drop=True)
    return leaderboard_df

def save_leaderboard_csv(leaderboard_df: pd.DataFrame, season: str):
    # save the leaderboard DataFrame to a CSV file
    file_path = f'data/raw/{season}/summed_leaderboard.csv'
    save_dataframe_to_csv(leaderboard_df, file_path)

def save_weekly_leaderboard(leaderboard_df: pd.DataFrame, season: str, week_id: str):
    # save the weekly leaderboard DataFrame to a CSV file
    file_path = f'data/raw/{season}/gameweek_{week_id}_leaderboard.csv'
    save_dataframe_to_csv(leaderboard_df, file_path)
    

def open_leaderboard_csv(season: str) -> pd.DataFrame:
    # open the leaderboard CSV file and return a DataFrame
    file_path = f'data/raw/{season}/summed_leaderboard.csv'
    try:
        leaderboard_df = pd.read_csv(file_path)
        return leaderboard_df
    except FileNotFoundError:
        # if the file does not exist, return an empty DataFrame
        return pd.DataFrame(columns=['author', 'total_points'])

def get_user_rank(leaderboard_df: pd.DataFrame, author: str) -> int:
    # get the rank of a specific user based on total points
    leaderboard_df = leaderboard_df.sort_values(by='total_points', ascending=False).reset_index(drop=True)
    if author in leaderboard_df['author'].values:
        return leaderboard_df[leaderboard_df['author'] == author].index[0] + 1  # ranks are 1-indexed
    else:
        return -1  # return -1 if the user is not found in the leaderboard