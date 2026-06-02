import pandas as pd
from assets.col_mapping import line_mapping

def line_summary(line_score_df):
    deselected_cols = ['gameId', 'teamId', 'teamSlug', 'team', 'teamCity', 'teamName']
    filt_df = line_score_df.drop(columns=deselected_cols, errors='ignore')

    filt_df.rename(columns=line_mapping, inplace=True)

    record_df = filt_df[['TEAM', 'WINS', 'LOSSES']].copy()
    record_df['RECORD'] = record_df['WINS'].astype(str) + "-" + record_df['LOSSES'].astype(str)

    line_df = filt_df.drop(columns=['WINS', 'LOSSES'])


    return line_df, record_df

