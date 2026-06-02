def quarter_totals(pbp):
    # Group by period and take the last row of each group - captures missing end times
    q_totals = pbp.groupby('period').tail(1)
    
    return q_totals[['period', 'scoreHome', 'scoreAway', 'teamTricode']].reset_index(drop=True)