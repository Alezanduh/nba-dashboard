from utils.time_conversion import seconds_to_minutes
import pandas as pd

def find_lead_changes(pbp_df, info_df, period=0):

    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    away_tri = info_df.loc[~info_df['isHome'], 'teamTricode'].iloc[0]

    # Current active runs
    lead_changes = 0
    leader = 0 # indicates team leading (0 = neither, 1 = home, 2 = away)
    lead_time = [] # list of game time at lead change
    lead_score = [] # list of score at lead change

    df = pbp_df[pbp_df['period'] == period] if period != 0 else pbp_df

    for _, row in df.iterrows():
        sh, sa, time = row['scoreHome'], row['scoreAway'], row['gameTime']

        # Determine current leader
        if sh > sa: 
            curr_leader = 1
        elif sa > sh: 
            curr_leader = 2
        else: 
            curr_leader = 0
            

        
        # If lead changes
        if (curr_leader != leader) & (curr_leader != 0) & (leader != 0):
            
            leader = curr_leader
            lead_changes += 1
            lead_time.append(time)
            lead_score.append((sh, sa))

        # If the game becomes untied, update leader
        elif (leader == 0) & (curr_leader != 0):
            leader = curr_leader

        # If the game becomes tied, set leader to 0 so the next score counts as a change
        elif curr_leader == 0:
            leader = 0

    lead_formatted_times = [seconds_to_minutes(t, None) for t in lead_time]
    score_home = [sh[0] for sh in lead_score]
    score_away = [sa[1] for sa in lead_score]

    return lead_changes, pd.DataFrame({
        'Time' : lead_formatted_times,
        f'{home_tri} Score' : score_home,
        f'{away_tri} Score' : score_away
    }).set_index('Time')


def find_largest_lead(pbp_df, info_df, period=0):

    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    away_tri = info_df.loc[~info_df['isHome'], 'teamTricode'].iloc[0]

    home_largest_lead, away_largest_lead = 0, 0
    home_lead_time, away_lead_time = 0, 0

    if period != 0:
        mask = pbp_df['period'] == period
        df = pbp_df[mask]

    else: 
        df = pbp_df

    for _, row in df.iterrows():
        # Home lead
        if row['scoreHome'] > row['scoreAway']:
            home_lead = row['scoreHome'] - row['scoreAway']

            if home_lead > home_largest_lead:
                home_largest_lead = home_lead
                home_lead_time = row['gameTime']

        # Away lead
        elif row['scoreHome'] < row['scoreAway']:
            away_lead = row['scoreAway'] - row['scoreHome']

            if away_lead > away_largest_lead:
                away_largest_lead = away_lead
                away_lead_time = row['gameTime']

    home_timestamp = seconds_to_minutes(home_lead_time)
    away_timestamp = seconds_to_minutes(away_lead_time)

    return pd.DataFrame({
        'Team': [home_tri, away_tri],
        'Largest Lead': [int(home_largest_lead), int(away_largest_lead)],
        'Time of Lead': [home_timestamp, away_timestamp]
    }).set_index('Team')