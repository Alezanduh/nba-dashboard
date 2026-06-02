from nba_api.stats.endpoints import playbyplayv2
from utils.time_conversion import period_seconds
from utils.time_conversion import game_seconds
import pandas as pd
import time

def pbp_features(df): 
  df['gameTime'] = df.apply(
      lambda row: game_seconds(row['period'], row['clock']),
      axis=1
  )

  df = df.sort_values('gameTime')

  # Populate each time value with an associated score

  # Home team
  df['scoreHome'] = (
      pd.to_numeric(df['scoreHome'], errors='coerce')
        .ffill()
        .fillna(0)
  )

  # Away team
  df['scoreAway'] = (
      pd.to_numeric(df['scoreAway'], errors='coerce')
        .ffill()
        .fillna(0)
  )

  df['homeMargin'] = df['scoreHome'] - df['scoreAway']
  df['awayMargin'] = df['scoreAway'] - df['scoreHome']

  df['periodTime'] = df['clock'].apply(period_seconds) 

  return df


def get_pbp_data(game_id):
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'Connection': 'keep-alive',
    }

    try:
        pbp = playbyplayv2.PlayByPlayV2(
            game_id=game_id, 
            headers=headers, 
            timeout=30
        )
        
        df = pbp.get_data_frames()[0]

    except Exception as e:
        print(f"Connection Error: {e}")
        # If it fails, wait and try again - the NBA API often throttles
        time.sleep(2)

    return df