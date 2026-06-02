# Team Information DataFrame
import pandas as pd

team_info = pd.DataFrame({
    "teamTricode" : [
        "ATL","BOS","BKN","CHA","CHI","CLE","DAL","DEN","DET","GSW",
        "HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK",
        "OKC","ORL","PHI","PHX","POR","SAC","SAS","TOR","UTA","WAS"
    ],
    "teamName" : [
        "Hawks","Celtics","Nets","Hornets","Bulls","Cavaliers","Mavericks",
        "Nuggets","Pistons","Warriors","Rockets","Pacers","Clippers",
        "Lakers","Grizzlies","Heat","Bucks","Timberwolves","Pelicans",
        "Knicks","Thunder","Magic","76ers","Suns","Trail Blazers","Kings",
        "Spurs","Raptors","Jazz","Wizards"
    ],
    "teamLocation" : [
        "Atlanta","Boston","Brooklyn","Charlotte","Chicago","Cleveland",
        "Dallas","Denver","Detroit","Golden State","Houston","Indiana",
        "Los Angeles","Los Angeles","Memphis","Miami","Milwaukee",
        "Minnesota","New Orleans","New York","Oklahoma City","Orlando",
        "Philadelphia","Phoenix","Portland","Sacramento","San Antonio",
        "Toronto","Utah","Washington"
    ],
    "primaryColor" : [
        "#E03A3E","#007A33","#000000","#1D1160","#CE1141","#860038",
        "#00538C","#0E2240","#C8102E","#1D428A","#CE1141","#FDBB30",
        "#C8102E","#552583","#5D76A9","#98002E","#00471B","#0C2340",
        "#0C2340","#006BB6","#007AC1","#0077C0","#006BB6","#1D1160",
        "#E03A3E","#5A2D81","#C4CED4","#CE1141","#002B5C","#002B5C"
    ],
    "secondaryColor" : [
        "#FDB927","#BA9653","#FFFFFF","#00788C","#000000","#FDBB30",
        "#B8C4CA","#FEC524","#1D42BA","#FFC72C","#000000","#002D62",
        "#1D428A","#FDB927","#12173F","#F9A01B","#EEE1C6","#78BE20",
        "#C8102E","#F58426","#EF3B24","#C4CED4","#ED174C","#E56020",
        "#000000","#63727A","#000000","#000000","#00471B","#E31837"
    ]
})