from utils.shot_chart import draw_court
import matplotlib.pyplot as plt

def create_shot_chart(pbp_df, info_df, period=0, shot_result=''):
    '''
    Creates an NBA-dimensioned shot chart

    Plots tracked x,y shot location from the NBA given each possession. Detailing makes and misses using 
    separate colourings.

    Args:
        pbp_df (pd.DataFrame): Play-by-play information for each possession. Contains shot information and shot-type.
        info_df (pd.DataFrame): Contains team based information for visual plotting and distinguishing home / away teams.
        period (int, optional): Integer value 0-4 detailing what selection of the game is used for the shot chart
            Defaults to 0 (full game)
        shot_result (string, optional): (WIP) Details which shot status are shown ('make', 'miss')
            Defaults to '' 

    Returns:
        plt.Figure: Figure showing a court-mapping and shot information
    
    '''

    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    away_tri = info_df.loc[~info_df['isHome'], 'teamTricode'].iloc[0]

    if period != 0:
        filt_df = pbp_df[pbp_df['period'] == period]
    else:
        filt_df = pbp_df

    made = filt_df['shotResult'] == 'Made'

    x_made = filt_df.loc[made, 'xLegacy']
    y_made = filt_df.loc[made, 'yLegacy']

    x_missed = filt_df.loc[~made, 'xLegacy']
    y_missed = filt_df.loc[~made, 'yLegacy']

    fig, ax = plt.subplots(figsize=(12, 11))

    draw_court(ax=ax, outer_lines=True)

    if shot_result in ('', 'Made'):
        ax.scatter(
            x_made,
            y_made,
            s=60,
            color='dodgerblue',
            edgecolors='dodgerblue',
            alpha=0.8,
            zorder=5
        )

    if shot_result in ('', 'Missed'):
        ax.scatter(
            x_missed,
            y_missed,
            s=60,
            color='darkred',
            edgecolors='darkred',
            alpha=0.8,
            zorder=5
        )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Title is diplayed in UI

    '''
    if period == 0:
        ax.set_title(f"{home_tri} vs. {away_tri} Shot Chart")
    else:
        ax.set_title(
            f"{home_tri} vs. {away_tri} Shot Chart\nQuarter {period}"
        )
    '''

    return fig