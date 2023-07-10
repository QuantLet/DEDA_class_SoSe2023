class Player:
    players_dict = {}
    def __init__(self, name):
        self.name = name
        self.twopointers = 0
        self.threepointers = 0
        self.misses_two = 0
        self.misses_three = 0
        self.opp_twopointers = 0
        self.opp_threepointers = 0
        self.opp_misses_two = 0
        self.opp_misses_three = 0
        self.offensive_rebounds = 0
        self.defensive_rebounds = 0
        self.opp_offensive_rebounds = 0
        self.opp_defensive_rebounds = 0
        self.turnovers = 0
        self.misses_freethrow = 0
        self.freethrows = 0
        self.opp_misses_freethrow = 0
        self.opp_freethrows = 0
        self.forced_turnovers = 0
        Player.players_dict[name] = self
        
    def twopointer(self):
        self.twopointers +=1
        
    def threepointer(self):
        self.threepointers +=1
        
    def miss_two(self):
        self.misses_two+=1
        
    def miss_three(self):
        self.misses_three+=1
        
    def opp_twopointer(self):
        self.opp_twopointers+=1
        
    def opp_threepointer(self):
        self.opp_threepointers +=1
        
    def opp_miss_two(self):
        self.opp_misses_two+=1
        
    def opp_miss_three(self):
        self.opp_misses_three+=1
        
    def offensive_rebounding(self,amount):
        self.offensive_rebounds = amount
        
    def defensive_rebounding(self,amount):
        self.defensive_rebounds = amount
        
    def opp_offensive_rebounding(self):
        self.opp_offensive_rebounds +=1
        
    def opp_defensive_rebounding(self):
        self.opp_defensive_rebounds +=1
    
    def turnover(self):
        self.turnovers+=1
        
    def freethrow(self):
        self.freethrows+=1
    
    def miss_freethrow(self):
        self.misses_freethrow+=1
        
    def opp_freethrow(self):
        self.opp_freethrows+=1
    
    def opp_miss_freethrow(self):
        self.opp_misses_freethrow+=1
        
    def forced_turnover(self):
        self.forced_turnovers+=1
        
    def reset(self):
        Player.players_dict = {}

# Handling of all player data --> Input is game data as a DataFrame
def player_data_calc(data,roster,team):
    opponents_rebounds_off = {}
    opponents_rebounds_def = {}
            
    digits = ['0','1','2','3','4','5','6','7','8','9']
    
    for i, row in data.iterrows():
        
        home_team = data['home_team'].head(1).values[0]
        
        # Create new player if not already listed
        if row['player_1'] not in Player.players_dict and row['player_1'] !=None:
            Player(row['player_1'])
        
        
        # Indicating a shot was attempted
        if row['game_event_type']==1 or row['game_event_type']==2 and row['player_1']!=None:
            
            # Made shots own team
            if home_team ==team and row[7]==None:
                current_lineup = row['home_lineup']
                handle_shots(row,current_lineup)

            if home_team !=team and row[5]==None:
                current_lineup = row['away_lineup']
                handle_shots(row,current_lineup)

            # Made shots opponent
            # Action by away team --> home team is our team --> action by opponent
            if home_team ==team and row[5]==None:
                current_lineup = row['home_lineup']
                handle_shots_opponent(row,current_lineup)

            # Action by home team --> Home team is not our team --> Action by opponent
            if home_team !=team and row[7]==None:
                current_lineup = row['away_lineup']
                handle_shots_opponent(row,current_lineup)
            
        # Handle Freethrows
        if row['game_event_type']==3 and row['player_1']!=None:
            
            if home_team ==team and row[7]==None or home_team ==team and row[5]==None:
                current_lineup = row['home_lineup']
            else:  
                current_lineup = row['away_lineup']

            handle_freethrows(row,home_team,team,current_lineup)
     
        # Turnovers own team 
        
        if row['game_event_type']==5 and row['player_1']!= None:
            
            Player.players_dict[row['player_1']].turnover()
            
        # Forced Turnovers (--> other team)
        handle_forced_turnovers(row,team,home_team)  
    
    # Opponents rebounds:
        if row['game_event_type']==4 and row['player_1']!= None: 
            
            if home_team ==team and row[7]==None or home_team ==team and row[5]==None:
                current_lineup = row['home_lineup']
                
            else:  
                current_lineup = row['away_lineup']
           
            if home_team ==team and row[5]==None:
                # Opponent is away
                opponent_home=False
                
                handle_opp_rebounds_away(row,opponent_home,current_lineup,opponents_rebounds_off,opponents_rebounds_def)
                
            if home_team !=team and row[7]==None:
                #Opponent is home
                opponent_home=True

                handle_opp_rebounds_home(row,opponent_home,current_lineup,opponents_rebounds_off,opponents_rebounds_def)
    
    # Own Rebounds
    for player in roster:
        
        try:
            if data[data['game_event_type']==4][data['player_1']==f'{player}'].shape[0]>0:
                
                substring = data[data['game_event_type']==4][data['player_1']==f'{player}'].tail(1)['home_desc'].values[0]

                if substring == None:
                    substring = data[data['game_event_type']==4][data['player_1']==f'{player}'].tail(1)['away_desc'].values[0]


                if substring != None:

                    # Offensive Rebounds
                    if substring.split("Off:",1)[1][1] in digits:
                        offensive_rebounds = int(substring.split("Off:",1)[1][:2])

                    else:
                        offensive_rebounds = int(substring.split("Off:",1)[1][0])

                    Player.players_dict[player].offensive_rebounding(offensive_rebounds)

                    # Defensive Rebounds
                    if substring.split("Def:",1)[1][1] in digits:
                        defensive_rebounds = int(substring.split("Def:",1)[1][:2]) 

                    else:
                        defensive_rebounds = int(substring.split("Def:",1)[1][0])

                    Player.players_dict[player].defensive_rebounding(defensive_rebounds)

        except KeyError:
            continue
        
    return Player.players_dict


def handle_shots(row,current_lineup):
    if row['game_event_type']==1 and row['player_1']!=None:
        descriptions = list(row[5:8])

        if any('3PT' in t for t in descriptions if t !=None):
            Player.players_dict[row['player_1']].threepointer()

        else:
            Player.players_dict[row['player_1']].twopointer()

    # Misses
    if row['game_event_type']==2 and row['player_1']!= None:
        descriptions = list(row[5:8])

        if any('3PT' in t for t in descriptions if t !=None):
            Player.players_dict[row['player_1']].miss_three()

        else:
            Player.players_dict[row['player_1']].miss_two()
                    
def handle_shots_opponent(row,current_lineup):
    if row['game_event_type']==1 and row['player_1']!=None:
        descriptions = list(row[5:8])

        if any('3PT' in t for t in descriptions if t !=None):

            
            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)
                Player.players_dict[player].opp_threepointer()

        else:

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)
                Player.players_dict[player].opp_twopointer()

    # Misses
    if row['game_event_type']==2 and row['player_1']!= None:
        descriptions = list(row[5:8])

        if any('3PT' in t for t in descriptions if t !=None):
            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)
                Player.players_dict[player].opp_miss_three()

        else:
            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)
                Player.players_dict[player].opp_miss_two()  
                
                
def handle_freethrows(row,home_team,team,current_lineup):
    if row['game_event_type']==3 and row['player_1']!= None:
        descriptions = list(row[5:8])

        if home_team ==team and row[7]==None or home_team!=team and row[5]==None:

    #Misses
            if any('MISS' in t for t in descriptions if t !=None):
                Player.players_dict[row['player_1']].miss_freethrow()
        #Makes 
            else:
                Player.players_dict[row['player_1']].freethrow()    
                
        #opponents
        

        if home_team ==team and row[5]==None or home_team!=team and row[7]==None:
            

            if any('MISS' in t for t in descriptions if t !=None):

                for player in current_lineup:
                    if player not in Player.players_dict:
                        Player(player)

                    Player.players_dict[player].opp_miss_freethrow()
        #Makes 
            else:
                for player in current_lineup:
                    if player not in Player.players_dict:
                        Player(player)
                        
                    Player.players_dict[player].opp_freethrow()   
                    
def handle_forced_turnovers(row,team,home_team):
    if home_team==team and row[5]==None:

        # Check for away team rebounds
        if row['game_event_type']==5 and row['away_desc']!=None and row['home_desc']==None:

            for player in row['home_lineup']:

                if player not in Player.players_dict:
                    Player(player)
                Player.players_dict[player].forced_turnover() 

    if home_team!=team and row[7]==None:
        if row['game_event_type']==5 and row['home_desc']!=None and row['away_desc']==None:

            for player in row['away_lineup']:

                if player not in Player.players_dict:
                    Player(player)

                Player.players_dict[player].forced_turnover() 
            
def handle_opp_rebounds_home(row,opponent_home,current_lineup,opponents_rebounds_off,opponents_rebounds_def):
    try:
        
        # else: Just change away_desc to home_desc every time!!!!
        # if opponent_home:

        offensive_rebounds = int(row['home_desc'].split("Off:",1)[1][0])

        defensive_rebounds = int(row['home_desc'].split("Def:",1)[1][0])
        
        
        if opponents_rebounds_off[row['player_1']]< offensive_rebounds:
            opponents_rebounds_off[row['player_1']]+=1

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)


                Player.players_dict[player].opp_offensive_rebounding()
                
        
        if opponents_rebounds_def[row['player_1']] < defensive_rebounds:
            opponents_rebounds_def[row['player_1']]+=1
            

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)

                Player.players_dict[player].opp_defensive_rebounding()
    
    except KeyError:
            
        opponents_rebounds_off[row['player_1']] = int(row['home_desc'].split("Off:",1)[1][0])
        opponents_rebounds_def[row['player_1']] = int(row['home_desc'].split("Def:",1)[1][0])
        
        offensive_rebounds = int(row['home_desc'].split("Off:",1)[1][0])

        defensive_rebounds = int(row['home_desc'].split("Def:",1)[1][0])
        
        
        if offensive_rebounds>0:

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)


                Player.players_dict[player].opp_offensive_rebounding()
                
        
        if defensive_rebounds>0:

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)

                Player.players_dict[player].opp_defensive_rebounding()


def handle_opp_rebounds_away(row,opponent_home,current_lineup,opponents_rebounds_off,opponents_rebounds_def):
    try:
        # else: Just change away_desc to home_desc every time!!!!
        # if opponent_home:

        offensive_rebounds = int(row['away_desc'].split("Off:",1)[1][0])

        defensive_rebounds = int(row['away_desc'].split("Def:",1)[1][0])
        
        
        if opponents_rebounds_off[row['player_1']]< offensive_rebounds:
            opponents_rebounds_off[row['player_1']]+=1

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)


                Player.players_dict[player].opp_offensive_rebounding()
                
        
        if opponents_rebounds_def[row['player_1']] < defensive_rebounds:
            opponents_rebounds_def[row['player_1']]+=1
            

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)

                Player.players_dict[player].opp_defensive_rebounding()
    
    except KeyError:
            
        opponents_rebounds_off[row['player_1']] = int(row['away_desc'].split("Off:",1)[1][0])
        opponents_rebounds_def[row['player_1']] = int(row['away_desc'].split("Def:",1)[1][0])
        
        offensive_rebounds = int(row['away_desc'].split("Off:",1)[1][0])

        defensive_rebounds = int(row['away_desc'].split("Def:",1)[1][0])
        
        
        if offensive_rebounds>0:

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)


                Player.players_dict[player].opp_offensive_rebounding()
                
        
        if defensive_rebounds>0:

            for player in current_lineup:
                if player not in Player.players_dict:
                    Player(player)

                Player.players_dict[player].opp_defensive_rebounding()