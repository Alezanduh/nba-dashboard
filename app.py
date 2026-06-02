import streamlit as st
import pandas as pd
import time

from analytics.lead import (
    find_largest_lead,
    find_lead_changes
)

from analytics.runs import (
    find_largest_run,
    largest_player_runs
)

from analytics.highs import ( 
    get_game_highs
)

from analytics.matchups import (
    load_team_matchups,
    prev_team_matchups,
    find_matchup_highs,
    get_matchup_highs,
    load_player_averages,
    get_player_stats_summary
)
from analytics.summary import line_summary

from plots.score_plots import plot_total_scores
from plots.shot_charts import create_shot_chart
from plots.momentum_plots import plot_momentum
from utils.time_conversion import get_game_date
from utils.get_nba_logos import get_logo_url

from utils.bs import (
    get_game_stats,
    clean_player_box_score
)

from data.nba_api import load_game

from nba_api.stats.static import teams  
from nba_api.stats.endpoints import leaguegamefinder 

# Pre-fetch static team list
nba_teams = teams.get_teams()
team_names = sorted([t['full_name'] for t in nba_teams])
team_name_to_id = {t['full_name']: t['id'] for t in nba_teams}

if "available_games" not in st.session_state:
    st.session_state.available_games = pd.DataFrame()

if "selected_game_id" not in st.session_state:
    st.session_state.selected_game_id = None

st.set_page_config(
    page_title="NBA Game Dashboard",
    layout="wide"
)


@st.cache_data(show_spinner=False, ttl=3600)
def get_game_data(game_id):
    df, bs, team_info, line_bs = load_game(game_id)

    # Prevent overloading NBA API
    time.sleep(1)

    bs_dict, team_bs_dict = get_game_stats(game_id, types=['all'])

    return df, bs, team_info, bs_dict, team_bs_dict, line_bs


st.title("NBA Game Analytics Dashboard")

github = "https://github.com/Alezanduh"

st.write(f"By Alexander Marsh")
st.link_button("GitHub", github)

# ------------------------------------------------------------------
# Main Page Search Interface
# ------------------------------------------------------------------

st.write("### Search Game")

# Create three columns for the search parameters
s_col1, s_col2, s_col3 = st.columns([2, 2, 2])

with s_col1:
    # Select box for primary team
    search_team = st.selectbox("Team", team_names)
    primary_id = team_name_to_id[search_team]

with s_col2:
    # Select box for conditional opponent
    # Add a "None" option (opponent is optional)
    opp_options = ["Any Opponent"] + team_names
    search_opp = st.selectbox("Opponent (Optional)", opp_options)
    opp_id = team_name_to_id[search_opp] if search_opp != "Any Opponent" else None

with s_col3:
    # Slider for Year selection
    selected_year = st.slider("Season Year", 2005, 2025, 2025)
    season_str = f"{selected_year}-{str(selected_year + 1)[2:]}"

# Fetch games based on search criteria
@st.cache_data(ttl=3600)
def search_nba_games(team_id, vs_team_id, season):
    '''
    Searches for all NBA games that match criteria.
    Returns all games from a season between a team and an opponent
    '''
    finder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        vs_team_id_nullable=vs_team_id,
        season_nullable=season,
        season_type_nullable='Regular Season'
    )
    games = finder.get_data_frames()[0]

    # if no games match criteria or issue with LeagueGameFinder
    if games.empty:

        return games
    
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE']).dt.date
    # Display label: DATE | TEAM (VS) OPPONENT (W/L)
    games['DISPLAY_LABEL'] = (
        games['GAME_DATE'].astype(str) + " | " + 
        games['MATCHUP'] + " (" + games['WL'] + ")"
    )
    return games[['GAME_ID', 'DISPLAY_LABEL']]

search_clicked = st.button(
    "Find Games",
    type="primary"
)

if search_clicked:

    with st.spinner("Searching for matchups..."):

        st.session_state.available_games = (
            search_nba_games(
                primary_id,
                opp_id,
                season_str
            )
        )
available_games = st.session_state.available_games

# Final Selection Box
if not available_games.empty:
    selected_game_label = st.selectbox(
        "Select game:",
        available_games['DISPLAY_LABEL'].tolist()
    )

    load_game_clicked = st.button(
        "Load Selected Game",
        type="primary"
    )

    if load_game_clicked:
        # If Load Selected Game is clicked 
        # `selected_game_id` equals the id within `available_games`
        st.session_state.selected_game_id = (
            available_games.loc[
                available_games['DISPLAY_LABEL']
                == selected_game_label,
                'GAME_ID'
            ].iloc[0]
        )
else:
    st.warning(f"No games found for {search_team} in the {season_str} season.")
    st.stop()

st.divider()

# ------------------------------------------------------------------
# Sidebar Controls
# ------------------------------------------------------------------

# Use the searched_id as the default value for the text input (prevents it from loading prior)
game_id = st.session_state.selected_game_id

if game_id is None:

    st.info(
        "Search for games and click "
        "'Load Selected Game'."
    )

    st.stop()


try:
    with st.spinner("Loading game data..."):
        df, bs, team_info_df, bs_dict, team_bs_dict, line_bs = get_game_data(game_id)

        

except Exception as e:
    st.error(f"Failed to load game data: {e}")
    st.stop()

# Gather game info for plotting
home_tri = team_info_df.loc[team_info_df['isHome'], 'teamTricode'].iloc[0]
away_tri = team_info_df.loc[~team_info_df['isHome'], 'teamTricode'].iloc[0]
home_id = team_info_df.loc[team_info_df['isHome'], 'teamId'].iloc[0]
away_id = team_info_df.loc[~team_info_df['isHome'], 'teamId'].iloc[0]
home_loc = team_info_df.loc[team_info_df['isHome'], 'teamLocation'].iloc[0]
away_loc = team_info_df.loc[~team_info_df['isHome'], 'teamLocation'].iloc[0]
home_name = team_info_df.loc[team_info_df['isHome'], 'teamName'].iloc[0]
away_name = team_info_df.loc[~team_info_df['isHome'], 'teamName'].iloc[0]

game_dt = pd.to_datetime(bs['gameEt'].iloc[0])

# Game information 
# HOMETEAM vs. AWAYTEAM on DAY OF WEEK, MONTH, DAY ,YEAR
st.subheader(f"{home_tri} vs. {away_tri}  |  {get_game_date(bs)}")

# Add team logo images 
col1, col2, col3 = st.columns(3)

line_df, record_df = line_summary(line_bs)

away_record = record_df.loc[1, 'RECORD']
home_record = record_df.loc[0, 'RECORD']


with col1:
    st.image(get_logo_url(home_id), width=200)
    st.metric("Home Team", f"{home_loc} {home_name}")
    st.markdown(f"<p style='text-align:left; color:gray;'>({home_record})</p>", unsafe_allow_html=True)
with col2: 
    # Centered and Scaled "VS."
    # Use margin-top to "push" it down to align with the middle of the logos
    st.markdown("""
        <div style="text-align: center; margin-top: 80px; margin-left: -75px">
            <h2 style="font-size: 40px; font-weight: bold; color: #555;">VS</h2>
        </div>
    """, unsafe_allow_html=True)
with col3: 
    st.image(get_logo_url(away_id), width=200)
    st.metric("Away Team", f"{away_loc} {away_name}")
    st.markdown(f"<p style='text-align:left; color:gray;'>({away_record})</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Sidebar Controls
# ------------------------------------------------------------------

st.sidebar.header("Filters")

period = st.sidebar.selectbox(
    "Period",
    [0, 1, 2, 3, 4],
    format_func=lambda x: (
        "Full Game" if x == 0 else f"Quarter {x}"
    )
)

score_type = st.sidebar.selectbox(
    "Score View",
    ["Total", "Marginal"]
)

team_leaders = st.sidebar.selectbox(
    "Leaderboard Filter",
    ["Both", home_tri, away_tri],
    index=0
)

smooth = st.sidebar.checkbox(
    "Smooth Curves",
    value=True
)



# ------------------------------------------------------------------
# Analytics
# ------------------------------------------------------------------

lead_df = find_largest_lead(
    df,
    team_info_df,
    period
)

run_df = find_largest_run(
    df,
    team_info_df,
    period
)

changes_count, changes_df = find_lead_changes(
    df,
    team_info_df,
    period
)

trad_bs = bs_dict.get('traditional')

highs_df = get_game_highs(
    trad_bs, 
    selected_stats=['all'], 
    team='both' if team_leaders == "Both" else team_leaders
)


# ------------------------------------------------------------------
# KPI Metrics
# ------------------------------------------------------------------

st.subheader("Game Overview")

m1, m2, m3 = st.columns(3)

with m1:

    if not lead_df.empty:

        max_lead_val = lead_df["Largest Lead"].max()
        leading_team = lead_df["Largest Lead"].idxmax()

        st.metric(
            "Largest Lead",
            f"{int(max_lead_val)} pts",
            delta=leading_team,
            delta_color="off"
        )

    else:
        st.metric("Largest Lead", "N/A")

with m2:

    if not run_df.empty:

        max_run_val = run_df["Largest Run"].max()
        run_team = run_df["Largest Run"].idxmax()

        st.metric(
            "Largest Run",
            f"{int(max_run_val)}-0",
            delta=run_team,
            delta_color="off"
        )

    else:
        st.metric("Largest Run", "N/A")

with m3:

    st.metric(
        "Lead Changes",
        int(changes_count)
    )


# ------------------------------------------------------------------
# Game Overview
# ------------------------------------------------------------------

if line_df is not None:
    st.write(f"### Game Summary")
    st.dataframe(line_df, use_container_width=True, hide_index=True)
else:
    st.error(f"Could not load data.")

# ------------------------------------------------------------------
# Game Highs
# ------------------------------------------------------------------


st.write("### Game Leaders")
if isinstance(highs_df, pd.DataFrame) and not highs_df.empty:
    # Create a row of columns for the top stats
    h_cols = st.columns(len(highs_df))
    
    for i, (stat_name, row) in enumerate(highs_df.iterrows()):
        with h_cols[i]:
            #Place Player Name (Top) above Metric & Value (Bottom)
            st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; border-left: 3px solid #555;">
                    <p style="margin: 0; font-size: 0.8rem; color: gray; text-transform: uppercase;">{stat_name}</p>
                    <p style="margin: 0; font-size: 1.1rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['Player']}</p>
                    <p style="margin: 0; font-size: 1.5rem; color: #2ecc71;">{int(row['Value'])} <span style="font-size: 0.8rem; color: #888;">{row['Team']}</span></p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Leader data unavailable for current selection.")

st.divider()

# ------------------------------------------------------------------
# Box-Score Summary
# ------------------------------------------------------------------

box_score_map = {
    "Traditional": "traditional",
    "Advanced": "adv",
    "Tracking": "track",
    "Four Factors": "fourfactors",
    "Hustle": "hustle"
}

# Create the selectbox using the display names 
selected_label = st.selectbox(
    "Box Score Type", 
    options=list(box_score_map.keys())
)

col1, col2 = st.columns([3, 1], vertical_alignment="bottom")

with col1:
    teams = [home_tri, away_tri]
    team_selected = st.segmented_control(
        "Team", 
        teams, 
        selection_mode="single",
        default=home_tri
    )

with col2:
    # Placing it in a column with vertical_alignment="bottom" ensures the checkbox aligns with the control, not the control's label.
    expanded = st.checkbox(
        "Expanded View",
        value=False
    )
# Get selected key
type_key = box_score_map[selected_label]

filt_bs = clean_player_box_score(bs_dict, team_selected, type_key, expanded=expanded)

if filt_bs is not None:
    st.write(f"### {selected_label} Statistics")
    st.dataframe(filt_bs, use_container_width=True)
else:
    st.error(f"Could not load {selected_label} data.")

# ------------------------------------------------------------------
# Previous Results
# ------------------------------------------------------------------

st.divider() 

@st.cache_data(show_spinner="Fetching matchup history...", ttl=600)
def get_cached_matchups(game_date, team_id, opp_id, last=5):
    return load_team_matchups(game_date, team_id, opp_id, last)

@st.cache_data(ttl=600)
def get_cached_player_matchups(matchup_df):
    return load_player_averages(matchup_df)


with st.expander("Matchup Details"):
    last_n = 5
    st.write(f"### Last {last_n} Matchups")

    # --- 1. Fetch Team Matchups ---
     # Fetch team-level results (Score, W/L)
     
    home_matchup_raw = get_cached_matchups(
        game_dt,
        home_id,
        away_id,
        last=last_n
    )

    away_matchup_raw = get_cached_matchups(
        game_dt,
        away_id,
        home_id,
        last=last_n
    )

    # Formatted matchup tables for display
    home_matchups = prev_team_matchups(home_matchup_raw)
    away_matchups = prev_team_matchups(away_matchup_raw)


    if not home_matchups.empty and not away_matchups.empty:
        # ADD: Functionality to filter for only W/L and score stats
        # Matchups are not reflexive (W/L), location (@, vs.) and stats are indicative of a singular team

        # Home team matchup statistics
        st.write(f"#### {home_tri} Matchup Statistics")
        st.dataframe(home_matchups, hide_index=True, use_container_width=True)

        # Home team matchup statistics
        st.write(f"#### {away_tri} Matchup Statistics")
        st.dataframe(away_matchups, hide_index=True, use_container_width=True)

    else:
        st.info("No previous team encounters found.")

    st.divider()

    '''
    # game_ids are shared between home_matchups and away_matchups (only need to input one)
    logs = get_cached_player_matchups(
        home_matchup_raw
    )

    player_avg_df = get_player_stats_summary(logs)

    if not player_avg_df.empty:
        st.write("### Matchup Stat Leaders (Averages)")
        
        # Mapping IDs to Tricodes for the UI
        team_map = {home_id: home_tri, away_id: away_tri}
        highs_df = get_matchup_highs(player_avg_df, team_map)
        
        # Display the Highs
        h_cols = st.columns(len(highs_df))
        for i, (stat_name, row) in enumerate(highs_df.iterrows()):
            with h_cols[i]:
                # Use red for high turnovers, green for everything else
                color = "#ff4b4b" if stat_name == 'TOV' else "#2ecc71"
                
                st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; border-left: 3px solid #555;">
                        <p style="margin: 0; font-size: 0.75rem; color: gray; text-transform: uppercase;">{stat_name}</p>
                        <p style="margin: 0; font-size: 1rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['Player']}</p>
                        <p style="margin: 0; font-size: 1.4rem; color: {color};">{row['Value']} <span style="font-size: 0.75rem; color: #888;">{row['Team']}</span></p>
                    </div>
                """, unsafe_allow_html=True)
                
        st.write("") # Padding
        with st.expander("View Full Player Averages"):
            st.dataframe(player_avg_df.drop(columns=['TEAM_ID']), hide_index=True)
    else:
        st.warning("Player matchup history unavailable for these teams.")
    
    '''

# LeagueDashPlayerStats OR PlayerDashboardByLastNGames
# Do something similar to box-score (get specific type of stats - playerstats, def, etc)
# Last 5 matchups with team (or allow slider)

# TeamGameLogs
# Results of Last N games against team
# Potentially get more game info based upon returned ids (may be costly)


# ------------------------------------------------------------------
# Analytics Tables
# ------------------------------------------------------------------

st.divider()

with st.expander("View Lead & Run Details"):

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Largest Leads")

        if not lead_df.empty:
            st.dataframe(
                lead_df,
                width='stretch'
            )
        else:
            st.info("No lead data available.")

    with col2:

        st.write("### Lead Change Timeline")

        if not changes_df.empty:
            st.dataframe(
                changes_df,
                width='stretch'
            )
        else:
            st.info("No lead changes recorded.")


# ------------------------------------------------------------------
# Main Tabs
# ------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Score Flow",
        "Shot Chart",
        "Player Runs",
        "Game Momentum"
    ]
)

# ------------------------------------------------------------------
# Score Flow
# ------------------------------------------------------------------

with tab1:
    if period != 0: 
        st.subheader(f"{home_tri} vs. {away_tri} Game Flow for Quarter {period}")
    else:
        st.subheader(f"{home_tri} vs. {away_tri} Game Flow")
    
    score_fig = plot_total_scores(
        df,
        team_info_df,
        bs,
        period=period,
        score_type=score_type,
        smooth=smooth
    )

    if score_fig is not None:
        st.pyplot(
            score_fig,
            width='stretch'
        )


# ------------------------------------------------------------------
# Shot Chart
# ------------------------------------------------------------------

with tab2:
    # Dynamic header - add quarter info if specified
    header_text = f"{home_tri} vs. {away_tri} Shot Chart"
    if period != 0:
        header_text += f" - Quarter {period}"
    
    st.markdown(f"### {header_text}")

    st.markdown("""
        <div style="display: flex; gap: 20px; margin-bottom: 20px; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 12px; height: 12px; background-color: #1f77b4; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem; font-weight: 500; color: #ccc;">Made Shot</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 12px; height: 12px; background-color: #e74c3c; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem; font-weight: 500; color: #ccc;">Missed Shot</span>
            </div>
            <div style="margin-left: auto; border-left: 1px solid #444; padding-left: 20px;">
                <span style="font-size: 0.8rem; color: #888; text-transform: uppercase;">Tracking: {0} shots</span>
            </div>
        </div>
    """.format(len(df[df['actionType'].str.contains('Shot|Layup|Dunk', case=False, na=False)]) if 'actionType' in df.columns else "N/A"), unsafe_allow_html=True)

    # Creare a figure based upon
    shot_fig = create_shot_chart(
        df,
        team_info_df,
        period=period
    )

    if shot_fig is not None:
        # Using a container to center the plot slightly
        with st.container():
            st.pyplot(shot_fig, use_container_width=True)
    else:
        st.info("No shot data available for the selected period.")


# ------------------------------------------------------------------
# Player Runs
# ------------------------------------------------------------------

with tab3:
    st.subheader(f"{home_tri} vs. {away_tri} Player Runs")

    run_mode = st.radio(
        "Run Type",
        [
            "Team-only runs",
            "Game-wide runs"
        ],
        horizontal=True
    )

    team_filter = (
        "same"
        if run_mode == "Team-only runs"
        else "all"
    )

    threshold = st.slider(
        "Run Threshold (Points)",
        min_value=4,
        max_value=25,
        value=8,
        help=(
            "Minimum points scored by a player "
            "without interruption."
        )
    )

    player_runs_df = largest_player_runs(
        df,
        team_info_df,
        threshold,
        team=team_filter
    )

    if not player_runs_df.empty:
        st.dataframe(
            player_runs_df,
            width='stretch'
        )
    else:
        st.info(
            f"No individual player runs of "
            f"{threshold}+ points occurred."
        )

# ------------------------------------------------------------------
# Game Momentum
# ------------------------------------------------------------------

with tab4: 

    st.subheader(f"{home_tri} vs. {away_tri} Game Momentum")

    threshold = st.slider(
        "Time Threshold (Seconds)",
        min_value=60,
        max_value=600,
        value=180,
        help=(
            "Threshold: "
            "How long previous scores "
            "Are considered in "
            "momentum calculation."
        )
    )

    decay = st.slider(
        "Rate of Decay",
        min_value=0.00001,
        max_value=1.0,
        value=0.01,
        help=(
            "Decay constant: "
            "Larger decay constant "
            "will decrease value of "
            "older points exponentially."
        )
    )

    scaling = st.slider(
        "Scaling Factor",
        min_value=0.00001,
        max_value=0.01,
        value=0.001,
        help=(
            "Scaling constant: "
            "Scales smoothness "
            "of momentum regularization."
        )
    )

    momentum_fig = plot_momentum(
        df,
        team_info_df,
        period=period,
        scaling=scaling,
        decay=decay,
        threshold=threshold,
        smooth=smooth
    )

    if momentum_fig is not None:
        st.pyplot(
            momentum_fig,
            width='stretch'
        )