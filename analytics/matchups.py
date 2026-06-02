from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv3, boxscoretraditionalv2
from assets.col_mapping import stats_summary_mapping


import random
import pandas as pd
from nba_api.stats.endpoints import playergamelogs


def load_team_matchups(game_date, team_id, opp_id, last_n=5):
    # Find last_n games between teams of interest
    finder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        vs_team_id_nullable=opp_id,
        date_to_nullable=game_date
    )
    df = finder.get_data_frames()[0]

    return df.head(last_n)

def prev_team_matchups(matchups): 

    deselected_cols = ['SEASON_ID', 'TEAM_ID', 'TEAM_NAME', 'GAME_ID', 'MIN', 'PLUS_MINUS'] # non-essential columns

    filt_df = matchups.drop(columns=deselected_cols, errors='ignore').copy()

    filt_df.rename(columns=stats_summary_mapping, inplace=True)

    return filt_df 

def load_player_averages(matchup_df):
    """
    Fetches player logs from the last_n (len(matchup_df)) team matchups against an opponent
    prior to game_date.
    """

    # Browser Header
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://stats.nba.com/',
        'Connection': 'keep-alive',
    }

    try:

        if matchup_df.empty:
            return pd.DataFrame()

        game_ids = matchup_df['GAME_ID'].unique().tolist()

        print(f"Found {len(game_ids)} matchup games")

        logs_list = []

        # Fetch player logs for the team
        for game_id in game_ids:

            try:

                bs = boxscoretraditionalv2.BoxScoreTraditionalV2(
                    game_id=game_id,
                    headers=headers,
                    timeout=30
                )

                game_logs = bs.get_data_frames()[0]

                if not game_logs.empty:

                    game_logs = game_logs.copy()
                    game_logs['GAME_ID'] = game_id

                    logs_list.append(game_logs)

            except Exception as e:

                print(f"Error loading game {game_id}: {e}")

                continue

        if not logs_list:
            return pd.DataFrame()

        all_logs = pd.concat(
            logs_list,
            ignore_index=True
        )

        if all_logs.empty:
            return pd.DataFrame()

        print(
            f"Returning {len(all_logs)} player logs "
            f"from {len(game_ids)} matchup games"
        )

        return all_logs

    except Exception as e:

        print(f"Error loading logs: {e}")

        return pd.DataFrame()

        
def get_player_stats_summary(players_df):
    # Loaded function fails to fetch player matchup info
    if players_df.empty:
        return pd.DataFrame()

    # essential cols
    cols = [
        'PLAYER_NAME', 'TEAM_ID', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 
        'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 
        'AST', 'TOV', 'STL', 'BLK', 'PTS', 'PLUS_MINUS'
    ]
    
    filt_df = players_df[cols].copy()
    
    mapping = {
        'FG_PCT': 'FG%',
        'FG3M': '3PM',
        'FG3A': '3PA',
        'FG3_PCT': '3P%',
        'FT_PCT': 'FT%',
        'PLUS_MINUS': '+/-'
    }

    filt_df.rename(columns=stats_summary_mapping, inplace=True)

    avg_stats = filt_df.groupby(['PLAYER_NAME', 'TEAM_ID']).mean(numeric_only=True).reset_index()

    # Round for clean average
    return avg_stats.round(1)

def find_matchup_highs(prev_stats):
    """
    Identifies the player with the highest average for each major stat category.
    Assumes 'PLAYER_NAME' is a column and the index is aligned.
    """

    if prev_stats.empty:
        return {}

    stats_cols = [
        'FGM', 'FGA', 'FG%', '3PM', '3PA', 
        '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 
        'AST', 'TOV', 'STL', 'BLK', 'PTS', '+/-'
    ]

    # Ensure we only check columns that actually exist in the dataframe
    available_cols = [c for c in stats_cols if c in prev_stats.columns]
    
    leaders = {}

    for col in available_cols:
        if col == 'TOV': # lower turnovers is optimal
            idx = prev_stats[col].idmin() 
        else:
            idx = prev_stats[col].idxmax()

        
        
        # 2. Retrieve the player name and the value at that index
        player = prev_stats.loc[idx, 'PLAYER_NAME']
        value = prev_stats.loc[idx, col]
        
        leaders[col] = {
            'Player': player,
            'Value': round(value, 1)
        }

    return leaders

def get_matchup_highs(avg_df, team_mapping):
    """
    avg_df: The averaged player stats
    team_mapping: a dict or dataframe to get Tricode from TeamId
    """
    stats_to_track = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']
    highs = []

    for stat in stats_to_track:
        if stat in avg_df.columns:
            # For TOV, you might want min, but usually leaders show the 'highest' 
            # volume player to watch out for. We'll stick with max for consistency.
            idx = avg_df[stat].idxmax()
            row = avg_df.loc[idx]
            
            highs.append({
                'Stat': stat,
                'Player': row['PLAYER_NAME'],
                'Value': row[stat],
                'Team': team_mapping.get(row['TEAM_ID'], "") # Ensure TEAM_ID is in your avg_df
            })
            
    return pd.DataFrame(highs).set_index('Stat')

        