from nba_api.stats.endpoints import WinProbabilityPBP

def get_wp_df(game_id):

    # FIX: Issues with WinProbabilityPBP endpoint

    wp = WinProbabilityPBP(game_id=game_id)

    dfs= wp.get_data_frames()
    
    # Index 0 contains the play-by-play win probability data
    win_prob_df = dfs[0]
    
    return win_prob_df

def plot_wp(game_id):

    wp_df = get_wp_df(game_id)

    


