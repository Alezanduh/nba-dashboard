from utils.time_conversion import game_seconds, seconds_to_minutes
from utils.plot_helpers import get_smooth_xy, apply_custom_grid
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as path_effects

def calc_delta(pbp_df, info_df):
    '''
    Calculates the point difference between plays relative to the home team.

    Determines whether the home team or away team scored on a given play 
    and applies a positive or negative multiplier to the point difference.

    Args:
        pbp_df (pd.DataFrame): The play-by-play data containing `teamTricode`
            and `pointsTotal` columns.
        info_df (pd.DataFrame): Team information containing 'isHome' and 
            `teamTricode` to isolate the home team - supports plotting.

    Returns:
        pd.Series: A series representing the point delta for each play from 
            the home team's perspective.
    '''
    home_tri = info_df.loc[info_df['isHome'], 'teamTricode'].iloc[0]
    
    pbp_df['multiplier'] = np.where(pbp_df['teamTricode'] == home_tri, 1, -1)
    pbp_df['ptsDelta'] = (pbp_df['pointsTotal'] - pbp_df['pointsTotal'].shift(1)).fillna(0)
    return pbp_df['ptsDelta'] * pbp_df['multiplier']

def calc_momentum(pbp_df, info_df, threshold=300, decay=0.01, scaling=0.001):
    '''
    Computes a time-decayed momentum score.

    Uses an exponential decay formula over a rolling time window to weight 
    recent scoring plays more heavily, scaling the output via a hyperbolic 
    tangent function to cap values gently.

    Args:
        pbp_df (pd.DataFrame): The play-by-play data containing `period`, 
            `clock`, and scoring attributes.
        info_df (pd.DataFrame): Team metadata used to establish scoring context.
        threshold (int, optional): The width of the rolling time window in 
            seconds. Defaults to 300.
        decay (float, optional): The exponential decay rate applied to older 
            plays. Defaults to 0.01.
        scaling (float, optional): Scaling factor applied to the sum of 
            weights before tanh normalization (typically most powerful factor). 
            Defaults to 0.001.

    Returns:
        pd.Series: A rolling 3-period centered moving average representing 
            the game momentum at any given moement.
    '''

    # Compute columns needed
    pbp_df['gameTime'] = pbp_df.apply(lambda r: game_seconds(r['period'], r['clock']), axis=1)
    pbp_df['scoreDelta'] = calc_delta(pbp_df, info_df)

    momentum = []
    for _, row in pbp_df.iterrows():

        # Threshold defines width of window (in seconds)
        start = max(0, row['gameTime'] - threshold) # curr_time - threshold
        end = row['gameTime'] # curr_time

        # Filter window and apply exponential decay
        temp = pbp_df[(pbp_df['gameTime'] >= start) & (pbp_df['gameTime'] <= end)]
        time_diffs = row['gameTime'] - temp['gameTime']
        weights = temp['scoreDelta'] * np.exp(-decay * time_diffs)

        # Scale using tanh for a natural cap
        momentum.append(np.tanh(weights.sum() * scaling) * 25)

    series = pd.Series(momentum, index=pbp_df.index)
    return series.rolling(window=3, center=True).mean().fillna(0)

def plot_momentum(pbp_df, info_df, period=0, smooth=True, threshold=300, decay=0.01, scaling=0.001): 
    """
    Plots the momentum swings between both teams throughout an NBA game.

    Generates a continuous line plot representing momentum over time (of NBA game). Areas 
    under the curve are shaded using team-specific colors to visually emphasize 
    which team holds positive momentum.

    Args:
        pbp_df (pd.DataFrame): The raw play-by-play match data.
        info_df (pd.DataFrame): Team styling metadata including `primaryColor`.
        period (int, optional): The specific game quarter to plot. If 0, plots 
            the entire game duration. Defaults to 0.
        smooth (bool, optional): If True, applies Pchip interpolation to smooth 
            the momentum curve line. Defaults to True.
        threshold (int, optional): Rolling momentum window duration. Defaults to 300.
        decay (float, optional): Exponential decay rate parameter. Defaults to 0.01.
        scaling (float, optional): Momentum curve dampening scale parameter. 
            Defaults to 0.001.

    Returns:
        plt.Figure: The generated matplotlib figure containing the styled 
            momentum visualization.
    """
    
    pbp_df['momentum'] = calc_momentum(pbp_df, info_df, scaling=scaling, decay=decay, threshold=threshold)
    
    # Identify team info
    home_info = info_df.loc[info_df['isHome']].iloc[0]
    away_info = info_df.loc[~info_df['isHome']].iloc[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.xaxis.set_major_formatter(FuncFormatter(seconds_to_minutes))

    # Time axis formatting
    if period == 0: 
        # Tick every quarter
        ax.set_xticks(np.arange(0, (4 * 720 + 1), 240)) 
        for x in np.arange(0, 2881, 720):
            # Add vertical line after each quarter
            ax.axvline(x=x, color='gray', linestyle='--', linewidth=1, zorder=0)
        for i, x in enumerate(np.arange(720, 2881, 720)):
            # In middle of quarter (x - 360) add quarter identifier
            ax.text(x - 360, ax.get_ylim()[1] - 28, f'Q{i+1}', ha='center', va='bottom')
        plot_df = pbp_df.copy()
    else:
        # Add ticks every minute (60 seconds)
        ax.set_xticks(np.arange((period - 1) * 720, (period * 720 + 1), 60)) 
        plot_df = pbp_df[pbp_df['period'] == period].copy()
        ax.set_xlim((period - 1) * 720, period * 720) 

    # If smooth checkbox is active
    # Use pchip to smooth
    x, y = plot_df['gameTime'], plot_df['momentum']

    if smooth:

        x, y = get_smooth_xy(x, y)

    # Draw the main line with a white glow effect for visibility
    stroke = [path_effects.withStroke(linewidth=4, foreground='white')]
    ax.plot(x, y, color="black", linewidth=1.5, zorder=4, alpha=0.7, path_effects=stroke)
    
    # Fill based on which team has the momentum (gray in-between)
    ax.fill_between(x, y, 0, where=(y >= 0), color=home_info['primaryColor'], alpha=0.4, interpolate=True, zorder=2)
    ax.fill_between(x, y, 0, where=(y < 0), color=away_info['primaryColor'], alpha=0.4, interpolate=True, zorder=2)
    
    # Add labels
    ax.set_ylabel('Momentum Score')
    ax.set_xlabel('Minutes')
    ax.axhline(0, color='black', linewidth=1.2, zorder=3) # Baseline
    apply_custom_grid(ax, 5, is_marginal=True)
    
    return fig