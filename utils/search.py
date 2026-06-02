from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

def get_team_games(team_id, season='2025-26'):
    """Fetches all games for a team in a specific season."""
    finder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        season_nullable=season,
        season_type_nullable='Regular Season'
    )
    games = finder.get_data_frames()[0]
    
    # Create a clean label for the dropdown
    # Example: "2026-05-30: LAL vs. BOS (W)"
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE']).dt.date
    games['DISPLAY_LABEL'] = (
        games['GAME_DATE'].astype(str) + ": " + 
        games['MATCHUP'] + " (" + games['WL'] + ")"
    )
    
    return games[['GAME_ID', 'DISPLAY_LABEL', 'GAME_DATE']]