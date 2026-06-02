import re
import math
import pandas as pd

# TIME FORMAT: PT, MINUTES REMAINING, SECONDS REMAINING
# PT12M00.00S

def nba_clock_to_seconds(clock_str):
    """
    Converts play-by-play time format into seconds elapsed from beginning of regulation

    Args:
        clock_str (str): String containing time information

    Returns:
        time (int): time since first play (beginning of regulation)
    """

    match = re.match(r'PT(\d+)M([\d.]+)S', clock_str)
    minutes = int(match.group(1))
    seconds = float(match.group(2))
    return minutes * 60 + seconds

def period_seconds(clock_str, period_length=720):
    remaining = nba_clock_to_seconds(clock_str)
    return period_length - remaining

def game_seconds(period, clock_str):
    remaining = nba_clock_to_seconds(clock_str)

    # first four quarters
    if period <= 4:
        return (period - 1) * 720 + (720 - remaining)
    else:
        # overtime periods are 5 minutes
        return 4 * 720 + (period - 5) * 300 + (300 - remaining)

def seconds_to_minutes(seconds_elapsed, pos=None):

    minutes = int(seconds_elapsed // 60)
    seconds = int(seconds_elapsed % 60)

    return f'{minutes}:{seconds:02d}'

def get_game_date(bs_df):

    game_dt = pd.to_datetime(bs_df['gameEt'].iloc[0])
    
    # Extract data time components
    year = game_dt.year
    month = game_dt.strftime('%B') 
    day = game_dt.day
    day_of_week = game_dt.strftime('%A') 

    if day % 10 == 1: 
        return f"{day_of_week}, {month} {day}st, {year}"
    elif day % 10 == 2: 
        return f"{day_of_week}, {month} {day}nd, {year}"
    elif day % 10 == 3: 
        return f"{day_of_week}, {month} {day}rd, {year}"
    else: 
        return f"{day_of_week}, {month} {day}th, {year}"