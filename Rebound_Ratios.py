# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:56:31 2016

@author: Javesh
"""

#STEP 1: GET REBOUND DATA FOR EACH TEAM SINCE THE 2004-2005 SEASON
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd


url_template = "http://espn.go.com/nba/statistics/team/_/stat/rebounds-per-game/sort/avgOffensiveRebounds/year/{yearno}"

team_reb_df = pd.DataFrame()
df2 = pd.DataFrame()

for yearno in range (2005, 2016):
    url = url_template.format(yearno = yearno)
    html = urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    headers = [tr.getText() for tr in soup.findAll('tr')[1]]
    for i in range(2,5):
        headers[i] = headers[i] + "_REB_%"
    for i in range(5, 7):
        headers[i] = "OFF_" + headers[i]
    for i in range(7, 9):
        headers[i] = "DEF_" + headers[i]
    for i in range (9, 12):
        headers[i] = "TOT_" + headers[i]
    
    rows = soup.findAll('tr')[2:]
    team_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    df1 = pd.DataFrame(team_data, columns = headers)
    df1.insert(0, 'Year', yearno)
    
    df2 = df2.append(df1, ignore_index = True)

#remove unwanted rows

df2 = df2[df2.TEAM != "REBOUND PCT"]
df2 = df2[df2.TEAM != "TEAM"]
team_reb_df = team_reb_df.append(df2, ignore_index = True)
team_reb_df = team_reb_df.convert_objects(convert_numeric=True)
    
    
#STEP 2: GET PLAYER REBOUND DATA SINCE THE 2004-2005 SEASON
url_template_2 = "http://espn.go.com/nba/statistics/player/_/stat/rebounds/sort/avgRebounds/year/{yearno}/qualified/false/count/{count}"
count = [00, 41, 81, 121, 161, 201, 241, 281, 321, 361, 401, 441]

player_reb_df = pd.DataFrame()
df4 = pd.DataFrame()


for yearno in range (2005, 2016):
    for counts in count:
        
        url2 = url_template_2.format(yearno = yearno, count = counts)
        html2 = urlopen(url2)
        soup2 = BeautifulSoup(html2, "lxml")
        player_headers = [tr.getText() for tr in soup2.findAll('tr')[0]]
        player_rows = soup2.findAll('tr')[1:]
        player_data = [[td.getText() for td in player_rows[i].findAll('td')] for i in range(len(player_rows))]
        df3 = pd.DataFrame(player_data, columns = player_headers)
        df3.insert(0, 'Year', yearno)
        df4 = df4.append(df3, ignore_index = True)

#remove unwanted rows
df4 = df4[df4.TEAM != "TEAM"]
player_reb_df = player_reb_df.append(df4, ignore_index = True)
#I want to get rid of player Bobby Jones because at one point he is on 5 teams, and also his rebound stats are low
player_reb_df = player_reb_df[player_reb_df.PLAYER != "Bobby Jones, SF"]
player_reb_df = player_reb_df.reset_index()
player_reb_df = player_reb_df.join(pd.DataFrame(player_reb_df.TEAM.str.split('/').tolist(), columns = ['TEAM1', 'TEAM2', 'TEAM3']))
#change outdated teams to new names
player_dict = {'SEA':'OKC', 'NJ':'BKN'}
player_reb_df = player_reb_df.replace({"TEAM1":player_dict})
player_reb_df = player_reb_df.replace({"TEAM2":player_dict})
player_reb_df = player_reb_df.replace({"TEAM3":player_dict})
#create a new dataframes and change TEAM1 to TEAM2
yes_TEAM2 = player_reb_df[player_reb_df['TEAM2'].notnull()]
for i in range (0, len(yes_TEAM2)):
    yes_TEAM2.PLAYER.iloc[i] += "_T2"
yes_TEAM2.TEAM1 = yes_TEAM2.TEAM2

#append the above dataframe to the main player dataframe
#this will create 2 separate entires for players that were on 2 teams
#Now, I can sort through my data using TEAM1
player_reb_df2 = pd.DataFrame()
player_reb_df2 = player_reb_df
player_reb_df2 = player_reb_df2.append(yes_TEAM2)
sort_ORPG = player_reb_df2.sort(['Year', 'ORPG'], ascending = [True, False])
sort_DRPG = player_reb_df2.sort(['Year', 'DRPG'], ascending = [True, False])
sort_TRPG = player_reb_df2.sort(['Year', 'RPG'], ascending = [True, False])
sort_ORPG = sort_ORPG.reset_index()
sort_DRPG = sort_DRPG.reset_index()
sort_TRPG = sort_TRPG.reset_index()

#only keep data for the top 2 rebounders per team
best_player_ORPG = pd.DataFrame()
best_player_DRPG = pd.DataFrame()
best_player_TRPG = pd.DataFrame()
#sorted_dfs is a list with the dataframes that sort through player_reb_df2 by ORPG, DRPG, and TRPG
sorted_dfs = [sort_ORPG, sort_DRPG, sort_TRPG]
#best_dfs will hold the best player from each team in ORPGs, DRPGs, and TRPGs
best_dfs = [best_player_ORPG, best_player_DRPG, best_player_TRPG]

for yearno2 in range (2005, 2016):       
    new_df_ORPG = sort_ORPG[sort_ORPG.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    best_player_ORPG = best_player_ORPG.append(new_df_ORPG)
    new_df_DRPG = sort_DRPG[sort_DRPG.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    best_player_DRPG = best_player_DRPG.append(new_df_DRPG)
    new_df_TRPG = sort_TRPG[sort_TRPG.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    best_player_TRPG = best_player_TRPG.append(new_df_TRPG)

#df_remove will be the DataFrame that holds the values of best_dfs that are not in best_dfs (top player from each team)
ORPG_remove = pd.DataFrame()
DRPG_remove = pd.DataFrame()
TRPG_remove = pd.DataFrame()
removed = [ORPG_remove, DRPG_remove, TRPG_remove]

ORPG_remove = sort_ORPG[sort_ORPG.index.map(lambda x: x not in best_player_ORPG.index)]
DRPG_remove = sort_DRPG[sort_DRPG.index.map(lambda x: x not in best_player_DRPG.index)]
TRPG_remove = sort_TRPG[sort_TRPG.index.map(lambda x: x not in best_player_TRPG.index)]


#now I can extract the second best player from each team by repeating the above code one more time
sec_player_ORPG = pd.DataFrame()
sec_player_DRPG = pd.DataFrame()
sec_player_TRPG = pd.DataFrame()
for yearno2 in range (2005, 2016):
    new_df_ORPG_2 = ORPG_remove[ORPG_remove.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    sec_player_ORPG = sec_player_ORPG.append(new_df_ORPG_2)
    new_df_DRPG_2 = DRPG_remove[DRPG_remove.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    sec_player_DRPG = sec_player_DRPG.append(new_df_DRPG_2)
    new_df_TRPG_2 = TRPG_remove[TRPG_remove.Year == yearno2].drop_duplicates(subset = ['TEAM1'])
    sec_player_TRPG = sec_player_TRPG.append(new_df_TRPG_2)

del best_player_ORPG['index']
del best_player_DRPG['index']
del best_player_TRPG['index']
del sec_player_ORPG['index']
del sec_player_ORPG['level_0']
del sec_player_DRPG['index']
del sec_player_DRPG['level_0']
del sec_player_TRPG['index']
del sec_player_TRPG['level_0']

sec_player_ORPG = sec_player_ORPG.reset_index()
sec_player_DRPG = sec_player_DRPG.reset_index()
sec_player_TRPG = sec_player_TRPG.reset_index()

#combine dataframes to have first and second best rebounders in each

frames_ORPG = [best_player_ORPG, sec_player_ORPG]
frames_DRPG = [best_player_DRPG, sec_player_DRPG]
frames_TRPG = [best_player_TRPG, sec_player_TRPG]

top_two_ORPG = best_player_ORPG.merge(sec_player_ORPG, on = ['Year', 'TEAM1'], how = 'outer')
top_two_DRPG = best_player_DRPG.merge(sec_player_DRPG, on = ['Year', 'TEAM1'], how = 'outer')
top_two_TRPG = best_player_TRPG.merge(sec_player_TRPG, on = ['Year', 'TEAM1'], how = 'outer')

top_two_ORPG = top_two_ORPG.sort('ORPG_x', ascending = False)
top_two_DRPG = top_two_DRPG.sort('DRPG_x', ascending = False)
top_two_TRPG = top_two_TRPG.sort('RPG_x', ascending = False)

del top_two_ORPG['level_0']
del top_two_DRPG['level_0']
del top_two_TRPG['level_0']

top_two_ORPG = top_two_ORPG.reset_index()
top_two_DRPG = top_two_DRPG.reset_index()
top_two_TRPG = top_two_TRPG.reset_index()

#STEP 3: MERGE THE PLAYER AND TEAM DATA
#create dictionary to map team abbreviations in top_two dfs with team_df

team_dict = {'Washington':'WSH', 'Cleveland': 'CLE', 'Atlanta':"ATL", 'Charlotte':'CHA', 'Golden State': 'GS', 'Detroit': "DET", 'Utah': 'UTAH', 'Oklahoma City':'OKC', 'Orlando': 'ORL', 'LA Lakers':'LAL', 'Sacramento': 'SAC', 'New Orleans':'NO', 'Chicago':'CHI', 'Dallas': 'DAL', 'San Antonio': 'SA', 'Milwaukee':'MIL', 'LA Clippers': 'LAC', 'Portland':'POR', 'Denver':'DEN', 'Phoenix':'PHX', 'New York': 'NY', 'Minnesota':'MIN', 'Boston':'BOS', 'Philadelphia':'PHI', 'Miami':'MIA', 'Memphis':'MEM', 'Houston':'HOU', 'Indiana':'IND', 'Brooklyn':'BKN', 'Toronto':'TOR'}
team_reb_df = team_reb_df.replace({"TEAM": team_dict})
team_reb_df = team_reb_df.rename(columns = {'TEAM':'TEAM1'})

#outer merge on Year and TEAM1
best_ORPG = best_player_ORPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')
best_DRPG = best_player_DRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')
best_TRPG = best_player_TRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')

sec_ORPG = sec_player_ORPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')
sec_DRPG = sec_player_DRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')
sec_TRPG = sec_player_TRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how='outer')

both_ORPG = top_two_ORPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how = 'outer')
both_DRPG = top_two_DRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how = 'outer')
both_TRPG = top_two_TRPG.merge(team_reb_df, on = ['Year', 'TEAM1'], how = 'outer')

#STEP 4: MAKE CALCULATIONS
#change data types to numeric so that we can make calculations
best_ORPG = best_ORPG.convert_objects(convert_numeric = True)
best_DRPG = best_DRPG.convert_objects(convert_numeric = True)
best_TRPG = best_TRPG.convert_objects(convert_numeric = True)

sec_ORPG = sec_ORPG.convert_objects(convert_numeric = True)
sec_DRPG = sec_DRPG.convert_objects(convert_numeric = True)
sec_TRPG = sec_TRPG.convert_objects(convert_numeric = True)

both_ORPG = both_ORPG.convert_objects(convert_numeric = True)
both_DRPG = both_DRPG.convert_objects(convert_numeric = True)
both_TRPG = both_TRPG.convert_objects(convert_numeric = True)

best_ORPG['Ratio'] = best_ORPG['ORPG']/best_ORPG['OFF_OWN']
best_DRPG['Ratio'] = best_DRPG['DRPG']/best_DRPG['DEF_OWN']
best_TRPG['Ratio'] = best_TRPG['RPG']/best_TRPG['TOT_OWN']

sec_ORPG['Ratio'] = sec_ORPG['ORPG']/sec_ORPG['OFF_OWN']
sec_DRPG['Ratio'] = sec_DRPG['DRPG']/sec_DRPG['DEF_OWN']
sec_TRPG['Ratio'] = sec_TRPG['RPG']/sec_TRPG['TOT_OWN']

both_ORPG['Ratio'] = (both_ORPG['ORPG_x'] + both_ORPG['ORPG_y'])/both_ORPG['OFF_OWN']
both_DRPG['Ratio'] = (both_DRPG['DRPG_x'] + both_DRPG['DRPG_y'])/both_DRPG['DEF_OWN']
both_TRPG['Ratio'] = (both_TRPG['RPG_x'] + both_TRPG['RPG_y'])/both_TRPG['TOT_OWN']

best_ORPG = best_ORPG.sort(['Year', 'TEAM1'])
best_DRPG = best_DRPG.sort(['Year', 'TEAM1'])
best_TRPG = best_TRPG.sort(['Year', 'TEAM1'])

sec_ORPG = sec_ORPG.sort(['Year', 'TEAM1'])
sec_DRPG = sec_DRPG.sort(['Year', 'TEAM1'])
sec_TRPG = sec_TRPG.sort(['Year', 'TEAM1'])

both_ORPG = both_ORPG.sort(['Year', 'TEAM1'])
both_DRPG = both_DRPG.sort(['Year', 'TEAM1'])
both_TRPG = both_TRPG.sort(['Year', 'TEAM1'])

#STEP 5: MAKE NEW DATAFRAMES WITH CALCULATIONS
#league_ratios will hold the league average ratios from 2005-2015
league_ratios = pd.DataFrame()
Year = [2005]
for a in range (2006, 2016):
    Year.append(a)
league_ratios['Year'] = Year

TeamORPG = []
TeamDRPG = []
TeamTRPG = []

BestORPG = []
BestDRPG = []
BestTRPG = []

SecORPG = []
SecDRPG = []
SecTRPG = []

BothORPG = []
BothDRPG = []
BothTRPG = []

for a in range (2005, 2016):
    TeamORPG.append(team_reb_df.loc[team_reb_df['Year'] == a]['OFF_OWN'].mean())
    TeamDRPG.append(team_reb_df.loc[team_reb_df['Year'] == a]['DEF_OWN'].mean())
    TeamTRPG.append(team_reb_df.loc[team_reb_df['Year'] == a]['TOT_OWN'].mean())
    
    BestORPG.append(best_ORPG.loc[best_ORPG['Year'] == a]['Ratio'].mean())
    BestDRPG.append(best_DRPG.loc[best_DRPG['Year'] == a]['Ratio'].mean())
    BestTRPG.append(best_TRPG.loc[best_TRPG['Year'] == a]['Ratio'].mean())
    
    SecORPG.append(sec_ORPG.loc[sec_ORPG['Year'] == a]['Ratio'].mean())
    SecDRPG.append(sec_DRPG.loc[sec_DRPG['Year'] == a]['Ratio'].mean())
    SecTRPG.append(sec_TRPG.loc[sec_TRPG['Year'] == a]['Ratio'].mean())
    
    BothORPG.append(both_ORPG.loc[both_ORPG['Year'] == a]['Ratio'].mean())
    BothDRPG.append(both_DRPG.loc[both_DRPG['Year'] == a]['Ratio'].mean())
    BothTRPG.append(both_TRPG.loc[both_TRPG['Year'] == a]['Ratio'].mean())

league_ratios['BestORPG'] = BestORPG
league_ratios['BestDRPG'] = BestDRPG
league_ratios['BestTRPG'] = BestTRPG

league_ratios['SecORPG'] = SecORPG
league_ratios['SecDRPG'] = SecDRPG
league_ratios['SecTRPG'] = SecTRPG

league_ratios['BothORPG'] = BothORPG
league_ratios['BothDRPG'] = BothDRPG
league_ratios['BothTRPG'] = BothTRPG

teams=[]
for value in team_dict.values():
    teams.append(value)

teams = sorted(teams)

from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('NBA_Rebound_Ratios_Charts.pdf')
import matplotlib.pyplot as plt

#STEP 6: MAKE AND SAVE GRAPHS 
#graphs of ORPG, DRPG, and TRPG, league-wide averages
plt.plot(Year, TeamORPG, label = 'ORPG')
plt.plot(Year, TeamDRPG, label = 'DRPG')
plt.plot(Year, TeamTRPG, label = 'TRPG')
plt.title('League-Wide Average Rebounds')
plt.legend(bbox_to_anchor=(1,0.80))
plt.figure
plt.savefig(pp, format = 'pdf')
plt.show()
#graphs of ORPG, DRPG, and TRPG ratios, league-wide averages

plt.plot(Year, BestORPG, label = 'ORPG')
plt.plot(Year, BestDRPG, label = 'DRPG')
plt.plot(Year, BestTRPG, label = 'TRPG')
plt.title('Best Player Rebounds / Team Rebounds')
plt.legend(bbox_to_anchor=(1,0.80))
fig = plt.figure
plt.savefig(pp, format = 'pdf')
plt.show()


plt.plot(Year, SecORPG, label = 'ORPG')
plt.plot(Year, SecDRPG, label = 'DRPG')
plt.plot(Year, SecTRPG, label = 'TRPG')
plt.title('2nd Best Player Rebounds / Team Rebounds')
plt.legend(bbox_to_anchor=(1,0.80))
fig2 = plt.figure
plt.savefig(pp, format='pdf')
plt.show()



plt.plot(Year, BothORPG, label = 'ORPG')
plt.plot(Year, BothDRPG, label = 'DRPG')
plt.plot(Year, BothTRPG, label = 'TRPG')
plt.title('Top 2 Best Players Rebounds / Team Rebounds')
plt.legend(bbox_to_anchor=(1,0.80))
fig3 = plt.figure
plt.savefig(pp, format='pdf')
plt.show()

best_ORPG = best_ORPG.sort(['Year', 'TEAM1'])
best_DRPG = best_DRPG.sort(['Year', 'TEAM1'])
best_TRPG = best_TRPG.sort(['Year', 'TEAM1'])

sec_ORPG = sec_ORPG.sort(['Year', 'TEAM1'])
sec_DRPG = sec_DRPG.sort(['Year', 'TEAM1'])
sec_TRPG = sec_TRPG.sort(['Year', 'TEAM1'])

both_ORPG = both_ORPG.sort(['Year', 'TEAM1'])
both_DRPG = both_DRPG.sort(['Year', 'TEAM1'])
both_TRPG = both_TRPG.sort(['Year', 'TEAM1'])

#graphs by team
for team in teams:
    plt.plot(Year, best_ORPG[best_ORPG["TEAM1"]==team]['Ratio'], label = 'ORPG')
    plt.plot(Year, best_DRPG[best_DRPG["TEAM1"]==team]['Ratio'], label = 'DRPG')
    plt.plot(Year, best_TRPG[best_TRPG["TEAM1"]==team]['Ratio'], label = 'TRPG')
    plt.title(team + ' Best Player Rebounds / Team Rebounds')
    plt.legend(bbox_to_anchor = (1, 1.5))
    plt.figure
    plt.savefig(pp, format='pdf')
    plt.show()


for team in teams:
    plt.plot(Year, sec_ORPG[sec_ORPG["TEAM1"]==team]['Ratio'], label = 'ORPG')
    plt.plot(Year, sec_DRPG[sec_DRPG["TEAM1"]==team]['Ratio'], label = 'DRPG')
    plt.plot(Year, sec_TRPG[sec_TRPG["TEAM1"]==team]['Ratio'], label = 'TRPG')
    plt.title(team + ' 2nd Best Player Rebounds / Team Rebounds')
    plt.legend(bbox_to_anchor = (1, 1.5))
    plt.figure
    plt.savefig(pp, format='pdf')
    plt.show()

for team in teams:
    plt.plot(Year, both_ORPG[both_ORPG["TEAM1"]==team]['Ratio'], label = 'ORPG')
    plt.plot(Year, both_DRPG[both_DRPG["TEAM1"]==team]['Ratio'], label = 'DRPG')
    plt.plot(Year, both_TRPG[both_TRPG["TEAM1"]==team]['Ratio'], label = 'TRPG')
    plt.title(team + ' Top 2 Best Players Rebounds / Team Rebounds')
    plt.legend(bbox_to_anchor = (1, 1.5))
    plt.figure    
    plt.savefig(pp, format='pdf')
    plt.show()


    
pp.close()
    