from nba_api.stats.endpoints import (
    BoxScoreAdvancedV3, 
    BoxScoreTraditionalV3, 
    BoxScorePlayerTrackV3, 
    BoxScoreHustleV2, 
    BoxScoreFourFactorsV3
)
from assets.col_mapping import type_mapping
import pandas as pd

def get_game_stats(game_id, types=['traditional']):
    '''
    Fetches specific NBA boxscores based on a list of requested types.

    Queries the NBA API endpoints dynamically using a keyword mapping. It splits 
    the returned data into player-level and team-level stats dictionaries.

    Args:
        game_id (str): The unique 10-digit identifier for an NBA game.
        types (List[str], optional): The statistics categories to retrieve. 
            Supported keys are 'traditional', 'adv', 'track', 'hustle', 
            'fourfactors', or 'all'. Defaults to ['traditional'].

    Returns:
        Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]: A tuple containing 
            two dicts (player_results, team_results), where the keys match 
            the requested types and values are the corresponding pandas DataFrames
    '''
    # Mapping keywords to the endpoint classes
    mapping = {
        'traditional': BoxScoreTraditionalV3,
        'adv': BoxScoreAdvancedV3,
        'track': BoxScorePlayerTrackV3,
        'hustle': BoxScoreHustleV2,
        'fourfactors': BoxScoreFourFactorsV3
    }
    
    player_results = {}
    team_results = {}

    if 'all' in types:
        new_types = ['traditional', 'adv', 'track', 'hustle', 'fourfactors']
    else:
        new_types = types


    for t in new_types:
        if t in mapping:
            # Initialize the endpoint and get the first dataframe (Player Stats)
            endpoint = mapping[t](game_id=game_id)
            all_dfs = endpoint.get_data_frames()
            
            # Extract each individually
            # 0 -> Player 
            # 1 -> Team
            player_results[t] = all_dfs[0]
            team_results[t] = all_dfs[1]
        else:
            print(f"Warning: Type '{t}' is not recognized.")

    return player_results, team_results


def clean_player_box_score(bs_dict, team, types='traditional', expanded=True): 
    '''
    Filters, cleans, and renames an individual player box score DataFrame.

    Slices raw NBA API box score data by team and structural complexity. It can 
    either drop non-essential metadata (expanded=True) or isolate a core subset 
    of prominent stats (expanded=False) before translating columns to readable headers.

    Args:
        bs_dict (Dict[str, pd.DataFrame]): Dictionary containing raw box score 
            DataFrames mapped by their stat type keyword.
        team (str): The 3-letter team tricode filter (ex: 'DET'). 'both' 
        retains all players in the game.
        types (str, optional): The dictionary key corresponding to the stat block 
            to clean. Defaults to 'traditional'.
        expanded (bool, optional): If True, returns all columns except metadata. 
            If False, filters down strictly to baseline core metrics. Defaults to True.

    Returns:
        pd.DataFrame: A cleaned DataFrame indexed by the formatted player name.
    '''

    cols_deselected = ['gameId', 'teamId', 'teamCity', 'teamName', 'playerSlug', 'teamSlug', 'personId', 'firstName', 'familyName', 'comment', 'jerseyNum'] # non-essential player info
    player_info = ['nameI', 'teamTricode', 'position'] # essential player info

    # Map only essential columns (non-expanded)
    col_mapping = {
        'traditional': ['minutes', 'points', 'reboundsTotal', 'assists', 'steals', 'blocks', 'turnovers'],
        'adv': ['minutes', 'offensiveRating', 'defensiveRating', 'netRating', 'trueShootingPercentage', 'assistToTurnover', 'usagePercentage'],
        'track': ['minutes', 'distance', 'touches', 'passes', 'contestedFieldGoalPercentage', 'uncontestedFieldGoalsPercentage'],
        'hustle': ['minutes', 'contestedShots', 'deflections', 'chargesDrawn', 'screenAssists', 'looseBallsRecoveredTotal', 'boxOuts'],
        'fourfactors': ['minutes', 'effectiveFieldGoalPercentage', 'freeThrowAttemptRate', 'teamTurnoverPercentage', 'offensiveReboundPercentage']
    }   


    df = bs_dict.get(types)

    # Filter for team selected
    # One team is required to be selected 
    if team != 'both': 
        filt_df = df[df['teamTricode'] == team]
    else: 
        filt_df = df



    if expanded == True:
        # Return full column set
        final_df = filt_df.drop(columns=cols_deselected, errors='ignore')
    else: 
        # Obtain specific [relevant] columns 
        # Allows for dynamic implementation
        selected_cols = col_mapping.get(types, [])
        final_cols = player_info + selected_cols
        
        # Ensure only columns that actually exist in the df are requested
        valid_cols = [c for c in final_cols if c in filt_df.columns]
        final_df = filt_df[valid_cols]

    rename_map = type_mapping.get(types, {})

    final_df.rename(columns=rename_map, inplace=True)

    return final_df.set_index("PLAYER")
