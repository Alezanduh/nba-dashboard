import pandas as pd

def label_home_away(row, home_id, away_id):
    if row['teamId'] == home_id:
        return 'home'
    elif row['teamId'] == away_id:
        return 'away'
    else:
        return 'neutral' # For period starts/ends where teamId is 0

def add_team_info(pbp_df, team_info_df): 
    pbp_team_info_df = pbp_df.merge(
        team_info_df,
        on='teamTricode',
        how='inner'
    )
    return pbp_team_info_df

def create_team_info_df(summary_df: pd.DataFrame, pbp_df: pd.DataFrame, team_info_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new dataframe containing team information for the specified game.
    """
    # SAFEGUARD: Check for column existence to prevent KeyError: ''
    # Depending on the NBA API endpoint, these might be capitalized or camelCase
    try:
        home_col = 'homeTeamId' if 'homeTeamId' in summary_df.columns else 'HOME_TEAM_ID'
        away_col = 'awayTeamId' if 'awayTeamId' in summary_df.columns else 'VISITOR_TEAM_ID'
        
        home_team_id = summary_df[home_col].iloc[0]
        visitor_team_id = summary_df[away_col].iloc[0]
    except KeyError:
        # If we still can't find them, let's print columns to the terminal for debugging
        print(f"Available Columns: {summary_df.columns.tolist()}")
        raise KeyError("Could not find Home/Away Team IDs in the summary data.")

    pbp_df = pbp_df.copy()
    team_df = add_team_info(pbp_df, team_info_df)

    team_df['side'] = team_df.apply(
        label_home_away,
        axis=1,
        args=(home_team_id, visitor_team_id)
    )

    team_df['isHome'] = team_df['teamId'] == home_team_id

    # Filter out neutral teamId 0 and return relevant info
    return (
        team_df.loc[
            team_df['teamId'] != 0,
            ['teamTricode', 'teamName', 'teamLocation', 'teamId', 'side', 'isHome', 'primaryColor', 'secondaryColor']
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

def create_tricode_pivot(totals, info_df):
    # Get tricodes team_info_df
    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    away_tri = info_df.loc[~info_df['isHome'], 'teamTricode'].iloc[0]

    # Replace 'home' / 'away' with associated TriCode
    totals_renamed = totals.rename(columns={
        'scoreHome': home_tri,
        'scoreAway': away_tri
    })

    # Add TriCodes into df
    melted = totals_renamed.melt(
        id_vars=['period'], 
        value_vars=[home_tri, away_tri], 
        var_name='Team', 
        value_name='Points'
    )

    # Pivot df for readability
    pivot_df = melted.pivot_table(
        index='Team', 
        columns='period', 
        values='Points'
    )
    
    return pivot_df.astype(int)