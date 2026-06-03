## NBA Analytics Dashboard

The NBA attempts to coalesce all analytical elements of a game in one place using data from nba.com. 

This NBA dashboard creates an analytical based summary of any selected NBA game. Given any NBA game-id with suitable tracking information (2005+),
it details both visual and numerical trends, patterns and insights within the current match-up while additionally drawing upon historical 
information. The dashboard has functionality that allows real-time interaction based upon parameters to formulate and model the information 
allowing for individualistic insights.

### Getting Started

The application is able to be run locally by installing Streamlit within your environment. 

```
# Within terminal
pip install streamlit
streamlit run app.py
```

To tinker with additional functionality or for further exploration, I recommend reviewing the NBA API (https://github.com/swar/nba_api/tree/master) page. All data included is courtesy of NBA.com and obtained through the NBA API page.

You can install the API with the following code
```
pip install nba_api
```
And using their endpoints can collect player, team, or league information. An example courtesy of NBA API
```
from nba_api.stats.endpoints import playercareerstats

# Nikola Jokić career stats
career = playercareerstats.PlayerCareerStats(player_id='203999')

# pandas data frames (optional: pip install pandas)
career.season_totals_regular_season.get_data_frame()

# json
career.get_json()

# dictionary
career.get_dict()
```

## Overview

**The dashboard provides the following high-level functionality**

**Real-Time Data Processing:** Dynamically pulls live play-by-play data using the nba_api.

**Advanced Modeling of Game Trends:** Uses both total and marginal scoring and time-decayed algorithms to map game swings.

**Granular Filters:** Allows users to subset data by specific game quarters or view cumulative team scores.

### Usage Summary


#### Search Game

Search for games by filtering a team of interest, an opponent (optional) and an NBA season - the resulting list will show the date of all
games that match the search criteria. Selecting one will automatically create a detailed review of the game.

<img width="1104" height="310" alt="image" src="https://github.com/user-attachments/assets/017c838a-cc62-46f6-8273-35c7e5d15893" />

#### Game Overview

<img width="1097" height="699" alt="image" src="https://github.com/user-attachments/assets/abefc29f-7137-4656-9924-d7f8fdb47129" />

**Plotting**: 
* Game score plots with distinction between total and marginal (difference between home and away)
* Momentum plots detailing which team is advantageously positioned at any moment 
* Shot charts using play-by-play tracking data to visualize the (x, y) location of every shot and the status (`make`, `miss`)

**Player Insights**:
* Game highs in basic summary statistics with additional filtering by team
* (WIP) Previous *n* matchup(s) player averages between teams
* Player individual within-team or within-game run summary determined by user decided cutoff `threshold`
* Traditional, advanced, tracking, four-factors and hustle box-score summaries provided for each player

**Game Summary**
* Team information and record on date of selected game
* Quarter-by-quarter scoring summary
* Previous *n* matchup(s) win-loss and stat summary between teams
* Game overview that includes largest lead by a team, largest run by a team and number of lead changes

### Project Information

#### Python 
Python is used to handle the entire backend analytical pipeline of the application. 
* **Data Retrieval & Cleaning:** Communicates with the NBA API endpoints to fetch raw play-by-play (PBP) and advanced box score data, filtering it dynamically by game ID and team tricode.
* **Algorithmic Modeling:** Runs custom mathematical processors (such as time-decayed exponential weight calculations normalized via hyperbolic tangent functions) to compute live game momentum.
* **Visualization:** Generates complex, publication-grade visual assets (e.g., scoring trends and custom-shaded margin differentials) using `Matplotlib` and `SciPy` interpolators.

#### Streamlit 
Streamlit serves as the reactive presentation layer for the dashboard.
* **Top-Down Execution:** Streamlit treats the Python codebase as a continuous script. Every time a user interacts with a UI widget (such as selecting a quarter or toggling a smoothing filter), Streamlit triggers an instant top-down rerun of the logic.
* **Reactive Data Flow:** Input variables selected in the browser are bound directly to Python functions. When the user changes a parameter, Streamlit passes the value to the Python engine, captures the newly generated Pandas DataFrames or Matplotlib figures, and dynamically updates the rendered web page in real time.

### NBA.com
NBA.com's (https://www.nba.com/termsofuse) Terms of Use regarding the use of the NBA’s digital platforms.
