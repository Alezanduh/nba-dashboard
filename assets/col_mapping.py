'''
Box-Score Column Mapping 

Traditional
Advanced
Tracking
Hustle
Four Factors

'''

traditional_mapping = {
    'nameI': 'PLAYER',
    'position': 'POS',
    'teamTricode': 'TEAM',
    'jerseyNum': 'NUMBER',
    'minutes': 'MIN',
    'fieldGoalsMade': 'FGM',
    'fieldGoalsAttempted': 'FGA',
    'fieldGoalsPercentage': 'FG%',
    'threePointersMade': '3PM',
    'threePointersAttempted': '3PA',
    'threePointersPercentage': '3P%',
    'freeThrowsMade': 'FTM',
    'freeThrowsAttempted': 'FTA',
    'freeThrowsPercentage': 'FT%',
    'reboundsOffensive': 'OREB',
    'reboundsDefensive': 'DREB',
    'reboundsTotal': 'REB',
    'assists': 'AST',
    'steals': 'STL',
    'blocks': 'BLK',
    'turnovers': 'TO',
    'foulsPersonal': 'PF',
    'points': 'PTS',
    'plusMinusPoints': '+/-'
}

advanced_mapping = {
    'nameI': 'PLAYER',
    'position': 'POS',
    'teamTricode': 'TEAM',
    'jerseyNum': 'NUMBER',
    'minutes': 'MIN',
    'offensiveRating': 'OFFRTG',
    'defensiveRating': 'DEFRTG',
    'netRating': 'NETRTG',
    'usagePercentage': 'USG%',
    'pace': 'PACE',
    'PIE': 'PIE',
    'assistPercentage': 'AST%',
    'assistToTurnover': 'AST/TO',
    'assistRatio': 'AST_RATIO',
    'offensiveReboundPercentage': 'OREB%',
    'defensiveReboundPercentage': 'DREB%',
    'reboundPercentage': 'REB%',
    'turnoverRatio': 'TO_RATIO',
    'effectiveFieldGoalPercentage': 'eFG%',
    'trueShootingPercentage': 'TS%',
    'possessions': 'POSS',
    'estimatedOffensiveRating': 'EST OFFRTG',
    'estimatedDefensiveRating': 'EST DEFRTG',
    'estimatedNetRating': 'EST NETRTG',
    'estimatedUsagePercentage': 'EST USG%',
    'estimatedPace': 'EST PACE',
    'pacePer40': 'PACE PER 40'
}

four_factors_mapping = {
    'nameI': 'PLAYER',
    'position': 'POS',
    'teamTricode': 'TEAM',
    'jerseyNum': 'NUMBER',
    'minutes': 'MIN',
    'effectiveFieldGoalPercentage': 'eFG%',
    'freeThrowAttemptRate': 'FTA RATE',
    'teamTurnoverPercentage': 'TOV%',
    'offensiveReboundPercentage': 'OREB%',
    'oppEffectiveFieldGoalPercentage': 'OPP eFG%',
    'oppFreeThrowAttemptRate': 'OPP FTA RATE',
    'oppTeamTurnoverPercentage': 'OPP TOV%',
    'oppOffensiveReboundPercentage': 'OPP OREB%'
}

hustle_mapping = {
    'nameI': 'PLAYER',
    'teamTricode': 'TEAM',
    'jerseyNum': 'NUMBER',
    'position': 'POS',
    'minutes': 'MIN',
    'contestedShots': 'CONTESTED',
    'contestedShots2pt': 'CONTESTED 2PT',
    'contestedShots3pt': 'CONTESTED 3PT',
    'deflections': 'DEFLECTIONS',
    'chargesDrawn': 'CHARGES DRAWN',
    'screenAssists': 'SCREEN AST',
    'screenAssistPoints': 'SCREEN AST PTS',
    'looseBallsRecoveredOffensive': 'LOOSE BALL REC OFF',
    'looseBallsRecoveredDefensive': 'LOOSE BALL REC DEF',
    'looseBallsRecoveredTotal': 'LOOSE BALLS REC',
    'offensiveBoxOuts': 'OFF BOXOUTS',
    'defensiveBoxOuts': 'DEF BOXOUTS',
    'boxOutPlayerTeamRebounds': 'BOXOUT TEAM REB',
    'boxOutPlayerRebounds': 'BOXOUT PLAYER REB',
    'boxOuts': 'BOX OUTS'
}

tracking_mapping = {
    'nameI': 'PLAYER',
    'position': 'POS',
    'teamTricode': 'TEAM',
    'jerseyNum': 'NUMBER',
    'minutes': 'MIN',
    'speed': 'SPD',
    'distance': 'DIST',
    'reboundChancesOffensive': 'OREB CHANCE',
    'reboundChancesDefensive': 'DREB CHANCE',
    'reboundChancesTotal': 'REB CHANCE',
    'touches': 'TCH',
    'secondaryAssists': 'SEC AST',
    'freeThrowAssists': 'FT AST',
    'passes': 'PASS',
    'assists': 'AST',
    'contestedFieldGoalsMade': 'CFGM',
    'contestedFieldGoalsAttempted': 'CFGA',
    'contestedFieldGoalPercentage': 'CFG%',
    'uncontestedFieldGoalsMade': 'UFGM',
    'uncontestedFieldGoalsAttempted': 'UFGA',
    'uncontestedFieldGoalsPercentage': 'UFG%',
    'fieldGoalPercentage': 'FG%',
    'defendedAtRimFieldGoalsMade': 'DFGM RIM',
    'defendedAtRimFieldGoalsAttempted': 'DFGA RIM',
    'defendedAtRimFieldGoalPercentage': 'DFG% RIM'
}

type_mapping = {
    'traditional': traditional_mapping,
    'adv': advanced_mapping,
    'track': tracking_mapping,
    'hustle': hustle_mapping,
    'fourfactors': four_factors_mapping
}

'''
Line Summary Mapping
'''

line_mapping = {
    'teamTricode': 'TEAM',
    'teamWins': 'WINS',
    'teamLosses': 'LOSSES',
    'period1Score': '1ST',
    'period2Score': '2ND',
    'period3Score': '3RD',
    'period4Score': '4TH',
    'score': 'FINAL'
}

'''
Box-Score Stats Mapping

Usage: 
matchups.py - get_player_stats_summary(), prev_team_matchups()
'''

stats_summary_mapping = {
        'FG_PCT': 'FG%',
        'FG3M': '3PM',
        'FG3A': '3PA',
        'FG3_PCT': '3P%',
        'FT_PCT': 'FT%',
        'PLUS_MINUS': '+/-'
    }