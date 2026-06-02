from matplotlib.ticker import FuncFormatter
from utils.time_conversion import seconds_to_minutes
from utils.time_conversion import get_game_date
from scipy.interpolate import make_interp_spline
from scipy.interpolate import PchipInterpolator
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_total_scores(pbp, info, bs, period=0, score_type='total', smooth=False): 

    quarter_ends = np.arange(720, 2881, 720)
    quarters = np.arange(0, 2881, 720)

    # Identify team info
    home_info = info.loc[info['isHome']].iloc[0]
    away_info = info.loc[~info['isHome']].iloc[0]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.xaxis.set_major_formatter(FuncFormatter(seconds_to_minutes))

    # Subset period info
    if period == 0: 
        ax.set_xticks(np.arange(0, (4 * 720 + 1), 240)) 

        # ax.set_title(f"{home_info['teamName']} vs {away_info['teamName']}\n{get_game_date(bs)}")


        for x in quarters:
            ax.axvline(x=x, color='gray', linestyle='--', linewidth=1, zorder=0)

        
        for i, x in enumerate(quarter_ends):
            ax.text(x - 360, ax.get_ylim()[1] - 28, f'Q{i+1}', ha='center', va='bottom')

    else:

        ax.set_xticks(np.arange((period - 1) * 720, (period * 720 + 1), 60)) 

        pbp = pbp[pbp['period'] == period]

        # x limits
        quarter_start = (period - 1) * 720
        quarter_end = period * 720

        ax.set_xlim(quarter_start, quarter_end) 

        # ax.set_title(f"{home_info['teamName']} vs {away_info['teamName']}\n{get_game_date(bs)}\n Quarter {period}")



        
    # Total score: cumulative sum of both home and away points 
    if (score_type == 'Total'):

        if smooth:

            # Clean data to remove duplicate time values
            home_clean = pbp.groupby('gameTime')['scoreHome'].max().reset_index()
            away_clean = pbp.groupby('gameTime')['scoreAway'].max().reset_index()

            # Create the Pchip objects 
            pchip_home = PchipInterpolator(home_clean['gameTime'], home_clean['scoreHome'])
            pchip_away = PchipInterpolator(away_clean['gameTime'], away_clean['scoreAway'])

            # 2880 is the standard 48-minute game in seconds
            x_smooth = np.linspace(0, pbp['gameTime'].max(), 1000)

            y_home_smooth = pchip_home(x_smooth)
            y_away_smooth = pchip_away(x_smooth)

            # Plot home
            ax.plot(
                x_smooth, y_home_smooth, 
                color=home_info['primaryColor'], 
                label=home_info['teamName'], 
                linewidth=2.5, 
                zorder=3
                )

            # Plot away
            ax.plot(
                x_smooth, y_away_smooth, 
                color=away_info['primaryColor'], 
                label=away_info['teamName'], 
                linewidth=2.5, 
                zorder=3
                )

        else: 

            ax.plot(pbp['gameTime'], pbp['scoreHome'], color=home_info['primaryColor'])
            ax.plot(pbp['gameTime'], pbp['scoreAway'], color=away_info['primaryColor'])
            
        ax.set_ylabel('Points Scored')

        ymin, ymax = ax.get_ylim()

        if period == 0: 

            # For full game: grid lines every 25 points
            start = 0
            end = 25 * np.ceil(ymax / 25)

            for y in np.arange(start, end + 25, 25):
                ax.axhline(
                    y=y,
                    color='gray',
                    linestyle='--',
                    linewidth=0.8,
                    alpha=0.4,
                    zorder=0
                )

        else: 
            
            # For each quarter: grid liens every 10 points
            start = 10 * np.floor(ymin / 10)
            end = 10 * np.ceil(ymax / 10)

            for y in np.arange(start, end + 10, 10):
                ax.axhline(
                    y=y,
                    color='gray',
                    linestyle='--',
                    linewidth=0.8,
                    alpha=0.4,
                    zorder=0
                )

    # Marginal score: the difference inscore between both teams
    elif (score_type == 'Marginal'):

        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1.5, zorder=1)

        if smooth:

            # Clean data to remove duplicate time values
            home_clean = pbp.groupby('gameTime')['homeMargin'].max().reset_index()
            away_clean = pbp.groupby('gameTime')['awayMargin'].max().reset_index()

            # Create the Pchip objects 
            pchip_home = PchipInterpolator(home_clean['gameTime'], home_clean['homeMargin'])
            pchip_away = PchipInterpolator(away_clean['gameTime'], away_clean['awayMargin'])

            # 2880 is the standard 48-minute game in seconds
            # Consider subsetted games can vary in length
            x_smooth = np.linspace(
                pbp['gameTime'].min(),
                pbp['gameTime'].max(),
                1000
            )

            y_home_smooth = pchip_home(x_smooth)
            y_away_smooth = pchip_away(x_smooth)

            # Plot home
            ax.plot(
                x_smooth, y_home_smooth, 
                color=home_info['primaryColor'], 
                label=home_info['teamName'], 
                linewidth=2.5, 
                zorder=3
                )

            # Plot away
            ax.plot(
                x_smooth, y_away_smooth, 
                color=away_info['primaryColor'], 
                label=away_info['teamName'], 
                linewidth=2.5, 
                zorder=3
                )

        else: 

            ax.plot(pbp['gameTime'], pbp['homeMargin'], color=home_info['primaryColor'], label=home_info['teamName'])
            ax.plot(pbp['gameTime'], pbp['awayMargin'], color=away_info['primaryColor'], label=away_info['teamName'])

        ax.set_ylabel('Points Margin')

        # Grid the graph
        ymin, ymax = ax.get_ylim()

        start = 5 * np.floor(ymin / 5)
        end = 5 * np.ceil(ymax / 5)

        for y in np.arange(start, end + 5, 5):
            if y != 0:  # keep the zero line distinct (i.e remains black)
                ax.axhline(
                    y=y,
                    color='gray',
                    linestyle='--',
                    linewidth=0.8,
                    alpha=0.4,
                    zorder=0
                )

        # Shade area between margins
        if smooth:
            ax.fill_between(
                x_smooth,
                y_home_smooth,
                y_away_smooth,
                color='gray',
                alpha=0.15,
                zorder=1
            )
        else:
            ax.fill_between(
                pbp['gameTime'],
                pbp['homeMargin'],
                pbp['awayMargin'],
                color='gray',
                alpha=0.15,
                zorder=1
            )

    
    
    ax.set_xlabel('Minutes')
    ax.legend()
    
    return fig


