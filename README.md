# Rebound_Ratios
There's been a lot of talk recently about how NBA teams are starting to abandon efforts at getting offensive rebounds in order to play
transition defense. I wanted to explore this through numbers. Specifically, I wanted to find out if teams are having less players
try to grab rebounds (offensive, defensive, and total) now than they did since 2005. So, I thought I should examine this by seeing how the
ratio of a team's top rebounder's (for each of the 3 rebounding categories) rebounds per game to total team rebounds per game has changed
from the past. I also wanted to see this ratio for the second best rebounder from each team, and also for the sum of rebounds per game
for the best and second best rebounder on each team. Specifically, I looked from the 2004-2005 season up until the 2014-2015 season
(it was easiest to work with this subset of data as there was no change in the number of teams within this period).

The code I have written first scrapes the data from ESPN and puts it into a pandas dataframe. 

Then, it cleans the data. It is important to note that the data included multiple teams for players that were traded within a season. 
In order to deal with this data without having to write separate scraping code to figure out the players rebounds per game whilst on each
team, I instead just created multiple entries for players that were on multiple teams (one entry for each team they were on, with all the 
other data remaining the same). In this way, the analysis is somewhat distored; however, very rarely were the top players on multiple 
teams within the season. Also, most players that were traded around had similar rebounding numbers whilst on each of their teams.

Lastly, the script creates 93 charts and saves them in a pdf entitled "NBA_Rebound_Ratios_Charts". The first 3 charts include league-wide
average ratios, while the other 90 show the ratios for each team since the 2004-2005 season.

Special thanks to Savvas Tjortjoglou, whose website I used to learn how to scrape NBA data: http://savvastjortjoglou.com/. Parts of my code
may look similar to his for this reason.



