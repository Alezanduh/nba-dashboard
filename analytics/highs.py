import pandas as pd

def get_game_highs(bs_df, selected_stats=['all'], types=['traditional'], team='both'):
    '''
    
    '''
    # Fetch the data (Fixed variable name conflict) 
    # FIX: Allow more functionality - convert lines into a function
    traditional_bs = bs_df

    if traditional_bs is None:
        return "Traditional Box Score not found in results."
    
    if team == 'both':
        filt_bs = traditional_bs
    else:
        filt_bs = traditional_bs[traditional_bs['teamTricode'] == team]

    stat_map = {
        'points': 'Points',
        'reboundsTotal': 'Rebounds',
        'assists': 'Assists',
        'steals': 'Steals',
        'blocks': 'Blocks',
        'turnovers': 'Turnovers'
    }

    # All selects all columns
    if 'all' in selected_stats:
        target_cols = list(stat_map.keys())
    # Choose selected coluns
    else: 
        target_cols = selected_stats

    game_highs = {}

    for c in target_cols:
        # Unsupported column names
        if c not in filt_bs.columns:
            continue
            
        idx = filt_bs[c].idxmax()

        first = filt_bs.loc[idx, 'firstName']
        last = filt_bs.loc[idx, 'familyName']
        team = filt_bs.loc[idx, 'teamTricode']
        total = filt_bs.loc[idx, c]
        
        display_name = stat_map.get(c, c.capitalize())
        game_highs[display_name] = {
            "Player": f"{first} {last}", 
            "Value": total, 
            "Team" : team
            }

    return pd.DataFrame(game_highs).T