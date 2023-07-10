#Own Imports
import abs_values
import lineups
import handle_absolute_values

# External libraries
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import warnings
import sqlite3
warnings.filterwarnings('ignore')

# team = 'LAL'
# season = '22018'
# players_season = '18_19'

def source_data(team,season,players_season):
    conn = sqlite3.connect('nba.sqlite')
    c = conn.cursor()

    team = team
    
    # Making SQlite call to receive necessary pbp data
    c.execute('''SELECT pbp.eventmsgtype, pbp.game_id ,pbp.player1_name, pbp.player2_name, pbp.player3_name, pbp.homedescription, pbp.neutraldescription, pbp.visitordescription,pbp.eventnum, g.team_abbreviation_home, g.team_abbreviation_away, g.season_id ,gi.game_date 
    From play_by_play AS pbp
    JOIN game_info gi ON pbp.game_id = gi.game_id 
    JOIN game g ON pbp.game_id = g.game_id
    WHERE g.team_abbreviation_home='LAL' OR g.team_abbreviation_away='LAL'
    ORDER BY gi.game_date DESC
    LIMIT 1000000''')

    team_pbp = c.fetchall()
    
    # inserting pbp data into DataFrame
    team_pbp = pd.DataFrame(data=team_pbp)
    team_pbp = team_pbp.rename(columns={0:'game_event_type',1:'game_id',2:'player_1',3:'player_2',4:'player_3',5:'home_desc',6:'neutral_desc',
                                          7:'away_desc',8:'game_event_id',9:'home_team',10:'away_team',11:'season_id',12:'date'})
    
    #Getting season data for specific season
    season = team_pbp[team_pbp['season_id']==season]
    
    # Getting season ids for the specific season
    game_ids = season['game_id'].unique()
    
    # Getting active roster of that season
    lakers_roster = pd.read_csv('lakers_rosters.csv',sep=';')
    lakers_roster = lakers_roster[lakers_roster['Season']==players_season]['Player']
    
    game_lineups_home = []
    game_lineups_away = []
    
    # Getting all the various lineups for each game of that season (on play by play basis)
    for game in game_ids:
        game_data = season[season['game_id']==game]
        current_lineups = lineups.play_by_play_lineup(game_data)
        
        game_lineups_home.append(current_lineups['lineup_home'])

        game_lineups_away.append(current_lineups['lineup_away'])
        

    # Adding home and away current lineups to our data 
    flattened_home = [item for sublist in game_lineups_home for item in sublist]
    flattened_away = [item for sublist in game_lineups_away for item in sublist]

    season['home_lineup']=flattened_home
    season['away_lineup'] = flattened_away
    
    c.execute('SELECT wl_home,game_id from game g')

    win_loss = c.fetchall()

    # Getting win/loss data for the games of that season
    dict_win_loss = {}
    for game in win_loss:
        dict_win_loss[game[1]] = game[0]
        
    # Actually retrieving the necessary statistics for every respective player 
    absolute_values = {}

    for game in game_ids:

        data_game = season[season['game_id']==game]
        
        opponents_rebounds_off = {}
        opponents_rebounds_def = {}
        
        stats_game = abs_values.player_data_calc(data_game,lakers_roster,'LAL')

        active_players = list(stats_game.keys())
        
        # getting active and inactive roster for paticular game
        
        active_lakers_players = list(set(active_players) & set(lakers_roster))

        inactive_players = list(set(lakers_roster)-set(active_lakers_players))
        
        for player in active_lakers_players:
            
            if player not in stats_game.keys():
                Player(player)

            handle_absolute_values.calc_absolute_values(absolute_values, stats_game,player)
        
        for player in inactive_players:
            
            # absolute values
            handle_absolute_values.calc_absolute_values_inactive(absolute_values, stats_game,player)
        
        # getting win loss column!

        if data_game['home_team'].head(1).values[0] == 'LAL':
            if dict_win_loss[game]=='W':
                absolute_values.setdefault('win',[]).append(1)
            else:
                absolute_values.setdefault('win',[]).append(0)
                
        if data_game['home_team'].head(1).values[0] != 'LAL':
            if dict_win_loss[game]=='L':
                absolute_values.setdefault('win',[]).append(0)
            else:
                absolute_values.setdefault('win',[]).append(1)
                
        absolute_values.setdefault('game_id',[]).append(game)
        player_name = list(stats_game.keys())[0]
        
        # Reset of stats for new game
        stats_game[player_name].reset()
    
    # Saving data to dataframe
    df_lal_season = pd.DataFrame(absolute_values)
    
    # Exporting data to csv file
    df_lal_season.to_csv(f'lakers_season_{players_season}_absolute.csv')
    
    
    
source_data('LAL','22018','18_19')  