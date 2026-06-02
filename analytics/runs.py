from utils.time_conversion import seconds_to_minutes
import pandas as pd

def largest_player_runs(pbp, team_info, threshold=8, team='same'):

    # Store active runs separately for each team
    active_runs = {}

    prev_pts_total = 0

    runs_list = []

    for _, row in pbp.iterrows():

        player = row['playerNameI']
        player_team = row['teamTricode']

        # Initialize tracking for this team if it does not exist
        if player_team not in active_runs:

            active_runs[player_team] = {
                'prev_player': None,
                'run_total': 0,
                'run_start_time': 0,
                'run_end_time': 0
            }

        team_run = active_runs[player_team]

        # Calculate points scored on this specific play
        # Use shotValue for FGs; for FTs, only calculate diff if pointsTotal is currently non-zero
        if row['shotResult'] == 'Made':

            points = row['shotValue']

        elif row['pointsTotal'] > 0:

            points = row['pointsTotal'] - prev_pts_total

        else:

            points = 0

        if points > 0:

            prev_player = team_run['prev_player']

            # team='all'
            # Run ends when ANY other player scores
            if team == 'all':

                player_changed = (prev_player != player)

            # team='same'
            # Run ends only when a TEAMMATE scores
            else:

                player_changed = (
                    prev_player is not None
                    and prev_player != player
                )

            # If the player changed, the previous run ends
            if player_changed:

                # Check if the finished run meets the threshold
                if (
                    prev_player is not None
                    and team_run['run_total'] >= threshold
                ):

                    runs_list.append({
                        'Player': prev_player,
                        'Team': player_team,
                        'Run Total': int(team_run['run_total']),
                        'Start Time': seconds_to_minutes(
                            team_run['run_start_time'],
                            None
                        ),
                        'End Time': seconds_to_minutes(
                            team_run['run_end_time'],
                            None
                        )
                    })

                # Start new tracking for the current player
                team_run['prev_player'] = player
                team_run['run_total'] = points
                team_run['run_start_time'] = row['gameTime']

            else:

                # First scorer for this team
                if prev_player is None:

                    team_run['prev_player'] = player
                    team_run['run_total'] = points
                    team_run['run_start_time'] = row['gameTime']

                # Same player is still scoring
                elif player == prev_player:

                    team_run['run_total'] += points

            # Update the time of the most recent bucket in this run
            team_run['run_end_time'] = row['gameTime']

            # Update prev_pts_total ONLY when a score happens to keep it as a valid reference
            prev_pts_total = row['pointsTotal']

    # Final check for active runs when the game ends
    for team_tricode, team_run in active_runs.items():

        if (
            team_run['prev_player'] is not None
            and team_run['run_total'] >= threshold
        ):

            runs_list.append({
                'Player': team_run['prev_player'],
                'Team': team_tricode,
                'Run Total': int(team_run['run_total']),
                'Start Time': seconds_to_minutes(
                    team_run['run_start_time'],
                    None
                ),
                'End Time': seconds_to_minutes(
                    team_run['run_end_time'],
                    None
                )
            })

    # Convert to DataFrame and drop any rows where Player might be None/NaN
    df_runs = pd.DataFrame(runs_list)

    if not df_runs.empty:

        df_runs = (
            df_runs
            .sort_values('Run Total', ascending=False)
            .reset_index(drop=True)
        )

    return df_runs


from utils.time_conversion import seconds_to_minutes


def extract_runs(pbp_df):
    """
    Extract all scoring runs from the play-by-play.

    Returns a df:
        Team
        Run
        Start Time
        End Time
        Period
    """

    runs = []

    # Current active run
    current_team = None
    current_run = 0
    run_start_time = 0
    run_period = 0

    h_prev, a_prev = 0, 0

    for _, row in pbp_df.iterrows():

        sh = row['scoreHome']
        sa = row['scoreAway']
        time = row['gameTime']
        period = row['period']

        # Home scores
        if sh > h_prev:

            points = sh - h_prev

            # New run begins
            if current_team != 'HOME':

                # Save previous run
                if current_team is not None:
                    runs.append({
                        'Team': current_team,
                        'Run': current_run,
                        'Start Time': run_start_time,
                        'End Time': time,
                        'Period': run_period
                    })

                current_team = 'HOME'
                current_run = points
                run_start_time = time
                run_period = period

            else:
                current_run += points

            h_prev = sh

        # Away scores
        elif sa > a_prev:

            points = sa - a_prev

            # New run begins
            if current_team != 'AWAY':

                # Save previous run
                if current_team is not None:
                    runs.append({
                        'Team': current_team,
                        'Run': current_run,
                        'Start Time': run_start_time,
                        'End Time': time,
                        'Period': run_period
                    })

                current_team = 'AWAY'
                current_run = points
                run_start_time = time
                run_period = period

            else:
                current_run += points

            a_prev = sa

    # Save final run
    if current_team is not None:

        runs.append({
            'Team': current_team,
            'Run': current_run,
            'Start Time': run_start_time,
            'End Time': pbp_df['gameTime'].iloc[-1],
            'Period': run_period
        })

    return pd.DataFrame(runs)


def find_largest_run(pbp_df, info_df, period=0):

    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    away_tri = info_df.loc[~info_df['isHome'], 'teamTricode'].iloc[0]

    runs_df = extract_runs(pbp_df)

    # Only consider runs fully contained within the requested quarter
    if period != 0:
        runs_df = runs_df[runs_df['Period'] == period]

    # Replace placeholders with actual team tricodes
    runs_df['Team'] = runs_df['Team'].replace({
        'HOME': home_tri,
        'AWAY': away_tri
    })

    home_runs = runs_df[runs_df['Team'] == home_tri]
    away_runs = runs_df[runs_df['Team'] == away_tri]


    def get_best_run(team_runs):
        # Base case: no runs occured 
        if team_runs.empty:
            return 0, (0, 0)

        # Find best run recorded
        best = team_runs.loc[team_runs['Run'].idxmax()]
        # Record run size and the duration it occured over
        return (
            int(best['Run']),
            (best['Start Time'], best['End Time'])
        )

    # Apply to both home and away teams
    home_max_run, home_times = get_best_run(home_runs)
    away_max_run, away_times = get_best_run(away_runs)

    fmt = lambda t: (
        f"{seconds_to_minutes(t[0], None)} - "
        f"{seconds_to_minutes(t[1], None)}"
    )

    return pd.DataFrame({
        'Team': [home_tri, away_tri],
        'Largest Run': [home_max_run, away_max_run],
        'Run Duration': [fmt(home_times), fmt(away_times)]
    }).set_index('Team')
