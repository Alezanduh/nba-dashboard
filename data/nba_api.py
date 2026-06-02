from utils.time_conversion import period_seconds
from utils.time_conversion import game_seconds
import pandas as pd

from nba_api.stats.endpoints import playbyplayv3
from nba_api.stats.endpoints import boxscoresummaryv3
from utils.game_info import create_team_info_df
from assets.team_info import team_info
from utils.pbp import pbp_features

def load_game(game_id):

    pbp = playbyplayv3.PlayByPlayV3(
        game_id=game_id,
        start_period=1,
        end_period=4
    )

    df = pbp.get_data_frames()[0]
    df = pbp_features(df)

    bs = (
        boxscoresummaryv3
        .BoxScoreSummaryV3(game_id=game_id)
        .get_data_frames()
    )

    game_summary_bs = bs[0] # The Game Summary table
    line_summary_bs = bs[4] # The Line Score table

    team_info_df = create_team_info_df(
        game_summary_bs, 
        df,
        team_info
    )

    return df, game_summary_bs, team_info_df, line_summary_bs