import itertools

def get_active_roster(game,roster):
    active_players = []
    active_columns = game.dropna(axis='columns',thresh=40)
    
    for player in roster:
        try: 
            if active_columns[f'{player}_twopointers'].values[0]!=None:

                active_players.append(player)
            
        except KeyError:
            continue
    return active_players


def get_combinations(active_roster):
    combinations = {}
    for i in range(len(active_roster)):
        
        tmp_combinations=[]
        tmp_roster = active_roster[:i] + active_roster[i+1:]
        
        for comb in itertools.combinations(tmp_roster, 4):
            player_1 = [active_roster[i]]
            list_combo = list(comb)
            # print(player_1+list_combo)
            tmp_combinations.append([active_roster[i]]+list(comb))
        
        combinations[active_roster[i]] = tmp_combinations
        
    return combinations

def deans_factors_season(season,combinations):
    deans_factors={}
    player1=[]
    player2=[]
    player3=[]
    player4=[]
    player5=[]
    lineups = []
    total_def_fg = []
    total_off_fg = []
    total_off_to = []
    total_def_to = []
    total_off_rb = []
    total_def_rb = []
    total_off_ft = []
    total_def_ft = []
    
    for player in combinations:
        
        # for each lineup for each respective player 
        for lineup in combinations[player]:
            
            # retrieve the absolute values necessary to compute all dean's factors
            abs_val = handle_absolute_values_season(season,lineup)
            
            # Helper variables to compute dean's factors
            fga = abs_val['twopointers'] + abs_val['threepointers'] + abs_val['misses_two'] + abs_val['misses_three']
            fga_opp = abs_val['opp_twopointers'] + abs_val['opp_threepointers'] + abs_val['opp_misses_two'] + abs_val['opp_misses_three']
            fta = abs_val['freethrows']+ abs_val['misses_freethrow']
            fta_opp = abs_val['opp_freethrows']+ abs_val['opp_misses_freethrow']
            
            # Deans Factors
            off_fg = (abs_val['twopointers']+1.5*abs_val['threepointers'])/fga
            def_fg = (abs_val['opp_twopointers']+1.5*abs_val['opp_threepointers'])/fga_opp
            off_to = abs_val['turnovers']/(fga+0.44*fta+abs_val['turnovers'])
            def_to = abs_val['forced_turnovers']/(fga_opp+0.44*fta_opp+abs_val['forced_turnovers'])
            off_rb = abs_val['offensive_rebounds']/(abs_val['offensive_rebounds']+abs_val['opp_defensive_rebounds'])
            def_rb = abs_val['defensive_rebounds']/(abs_val['defensive_rebounds']+abs_val['opp_offensive_rebounds'])
            off_ft = abs_val['freethrows']/fga
            def_ft =  abs_val['opp_freethrows']/fga_opp
            
            
            player1.append(lineup[0])
            player2.append(lineup[1])
            player3.append(lineup[2])
            player4.append(lineup[3])
            player5.append(lineup[4])
            lineups.append(lineup)
            
            total_def_fg.append(def_fg)
            total_off_fg.append(off_fg)
            total_off_to.append(off_to)
            total_def_to.append(def_to)
            total_off_rb.append(off_rb)
            total_def_rb.append(def_rb)
            total_off_ft.append(off_ft)
            total_def_ft.append(def_ft)
            
        deans_factors['player1'] =player1
        deans_factors['player2'] = player2
        deans_factors['player3'] = player3
        deans_factors['player4'] = player4
        deans_factors['player5'] = player5
        deans_factors['off_fg_perc'] = total_off_fg
        deans_factors['def_fg_perc'] = total_def_fg
        deans_factors['off_to_perc'] = total_off_to
        deans_factors['def_to_perc'] = total_def_to
        deans_factors['off_rb_perc'] = total_off_rb
        deans_factors['def_rb_perc'] = total_def_rb
        deans_factors['off_ft_factor'] = total_off_ft
        deans_factors['def_ft_factor'] = total_def_ft
        
    return deans_factors

def handle_absolute_values_season(game,lineup):
    twopointers = 0
    threepointers = 0
    misses_two = 0
    misses_three = 0
    opp_twopointers = 0
    opp_threepointers = 0
    opp_misses_two = 0
    opp_misses_three = 0
    turnovers = 0
    forced_turnovers = 0
    freethrows = 0
    misses_freethrow = 0
    offensive_rebounds = 0
    defensive_rebounds = 0
    opp_freethrows = 0
    opp_misses_freethrow = 0
    opp_offensive_rebounds = 0
    opp_defensive_rebounds = 0

    absolute_values = {}
    for player in lineup:
        twopointers+= game[f'{player}_twopointers'].mean()
        threepointers+= game[f'{player}_threepointers'].mean()
        misses_two+= game[f'{player}_misses_two'].mean()
        misses_three+= game[f'{player}_misses_three'].mean()
        opp_twopointers+= game[f'{player}_opp_twopointers'].mean()
        opp_threepointers+= game[f'{player}_opp_threepointers'].mean()
        opp_misses_two+= game[f'{player}_opp_misses_two'].mean()
        opp_misses_three+= game[f'{player}_opp_misses_three'].mean()
        turnovers+= game[f'{player}_turnovers'].mean()
        forced_turnovers+= game[f'{player}_forced_turnovers'].mean()
        misses_freethrow+= game[f'{player}_misses_freethrow'].mean()
        offensive_rebounds+= game[f'{player}_offensive_rebounds'].mean()
        defensive_rebounds+= game[f'{player}_defensive_rebounds'].mean()
        freethrows += game[f'{player}_freethrows'].mean()
        misses_freethrow += game[f'{player}_misses_freethrow'].mean()
        opp_freethrows+= game[f'{player}_opp_freethrows'].mean()
        opp_misses_freethrow+= game[f'{player}_opp_misses_freethrow'].mean()
        opp_offensive_rebounds+= game[f'{player}_opp_offensive_rebounds'].mean()
        opp_defensive_rebounds+= game[f'{player}_opp_defensive_rebounds'].mean()
    
    absolute_values['lineup'] = lineup
    absolute_values['twopointers'] = twopointers
    absolute_values['threepointers'] = threepointers
    absolute_values['misses_two'] = misses_two
    absolute_values['misses_three'] = misses_three
    absolute_values['opp_twopointers'] = opp_twopointers
    absolute_values['opp_threepointers'] = opp_threepointers
    absolute_values['opp_misses_two'] = opp_misses_two
    absolute_values['opp_misses_three'] = opp_misses_three
    absolute_values['turnovers'] = turnovers
    absolute_values['forced_turnovers'] = forced_turnovers
    absolute_values['freethrows'] = freethrows
    absolute_values['misses_freethrow'] = misses_freethrow
    absolute_values['offensive_rebounds'] = offensive_rebounds
    absolute_values['defensive_rebounds'] = defensive_rebounds
    absolute_values['opp_freethrows'] = opp_freethrows
    absolute_values['opp_misses_freethrow'] = opp_misses_freethrow
    absolute_values['opp_offensive_rebounds'] = opp_offensive_rebounds
    absolute_values['opp_defensive_rebounds'] = opp_defensive_rebounds
        
    return absolute_values

# IRRELEVANT FOR THE APPLICATION

# def deans_factors(game,combinations):
    
#     deans_factors={}
#     player1=[]
#     player2=[]
#     player3=[]
#     player4=[]
#     player5=[]
#     game_id = []
#     lineups = []
#     total_def_fg = []
#     total_off_fg = []
#     total_off_to = []
#     total_def_to = []
#     total_off_rb = []
#     total_def_rb = []
#     total_off_ft = []
#     total_def_ft = []
    
#     for focus in combinations:
        
#         for lineup in combinations[focus]:
#             abs_val = handle_absolute_values(game,lineup)
            
            
#             fga = abs_val['twopointers'] + abs_val['threepointers'] + abs_val['misses_two'] + abs_val['misses_three']
#             fga_opp = abs_val['opp_twopointers'] + abs_val['opp_threepointers'] + abs_val['opp_misses_two'] + abs_val['opp_misses_three']
#             fta = abs_val['freethrows']+ abs_val['misses_freethrow']
#             fta_opp = abs_val['opp_freethrows']+ abs_val['opp_misses_freethrow']
            
#             # Deans Factors
            
#             off_fg = (abs_val['twopointers']+1.5*abs_val['threepointers'])/fga
#             def_fg = (abs_val['opp_twopointers']+1.5*abs_val['opp_threepointers'])/fga_opp
#             off_to = abs_val['turnovers']/(fga+0.44*fta+abs_val['turnovers'])
#             def_to = abs_val['forced_turnovers']/(fga_opp+0.44*fta_opp+abs_val['forced_turnovers'])
#             off_rb = abs_val['offensive_rebounds']/(abs_val['offensive_rebounds']+abs_val['opp_defensive_rebounds'])
#             def_rb = abs_val['defensive_rebounds']/(abs_val['defensive_rebounds']+abs_val['opp_offensive_rebounds'])
#             off_ft = abs_val['freethrows']/fga
#             def_ft =  abs_val['opp_freethrows']/fga_opp
            
#             game_id.append(game['game_id'])
#             player1.append(lineup[0])
#             player2.append(lineup[1])
#             player3.append(lineup[2])
#             player4.append(lineup[3])
#             player5.append(lineup[4])
#             lineups.append(lineup)
#             #here were all def_fg[0]
#             total_def_fg.append(def_fg)
#             total_off_fg.append(off_fg)
#             total_off_to.append(off_to)
#             total_def_to.append(def_to)
#             total_off_rb.append(off_rb)
#             total_def_rb.append(def_rb)
#             total_off_ft.append(off_ft)
#             total_def_ft.append(def_ft)
            
#         deans_factors['game_id'] = game_id
#         deans_factors['player1'] =player1
#         deans_factors['player2'] = player2
#         deans_factors['player3'] = player3
#         deans_factors['player4'] = player4
#         deans_factors['player5'] = player5
#         deans_factors['off_fg_perc'] = total_off_fg
#         deans_factors['def_fg_perc'] = total_def_fg
#         deans_factors['off_to_perc'] = total_off_to
#         deans_factors['def_to_perc'] = total_def_to
#         deans_factors['off_rb_perc'] = total_off_rb
#         deans_factors['def_rb_perc'] = total_def_rb
#         deans_factors['off_ft_factor'] = total_off_ft
#         deans_factors['def_ft_factor'] = total_def_ft
        
#     return deans_factors
    

# IRRELEVANT FOR APPLICATION

# def handle_absolute_values(game,lineup):
#     twopointers = 0
#     threepointers = 0
#     misses_two = 0
#     misses_three = 0
#     opp_twopointers = 0
#     opp_threepointers = 0
#     opp_misses_two = 0
#     opp_misses_three = 0
#     turnovers = 0
#     forced_turnovers = 0
#     freethrows = 0
#     misses_freethrow = 0
#     offensive_rebounds = 0
#     defensive_rebounds = 0
#     opp_freethrows = 0
#     opp_misses_freethrow = 0
#     opp_offensive_rebounds = 0
#     opp_defensive_rebounds = 0

#     absolute_values = {}
#     for player in lineup:
#         twopointers+= game[f'{player}_twopointers']
#         threepointers+= game[f'{player}_threepointers']
#         misses_two+= game[f'{player}_misses_two']
#         misses_three+= game[f'{player}_misses_three']
#         opp_twopointers+= game[f'{player}_opp_twopointers']
#         opp_threepointers+= game[f'{player}_opp_threepointers']
#         opp_misses_two+= game[f'{player}_opp_misses_two']
#         opp_misses_three+= game[f'{player}_opp_misses_three']
#         turnovers+= game[f'{player}_turnovers']
#         forced_turnovers+= game[f'{player}_forced_turnovers']
#         misses_freethrow+= game[f'{player}_misses_freethrow']
#         offensive_rebounds+= game[f'{player}_offensive_rebounds']
#         defensive_rebounds+= game[f'{player}_defensive_rebounds']
#         opp_freethrows+= game[f'{player}_opp_freethrows']
#         opp_misses_freethrow+= game[f'{player}_opp_misses_freethrow']
#         opp_offensive_rebounds+= game[f'{player}_opp_offensive_rebounds']
#         opp_defensive_rebounds+= game[f'{player}_opp_defensive_rebounds']
    
#     absolute_values['lineup'] = lineup
#     absolute_values['twopointers'] = twopointers
#     absolute_values['threepointers'] = threepointers
#     absolute_values['misses_two'] = misses_two
#     absolute_values['misses_three'] = misses_three
#     absolute_values['opp_twopointers'] = opp_twopointers
#     absolute_values['opp_threepointers'] = opp_threepointers
#     absolute_values['opp_misses_two'] = opp_misses_two
#     absolute_values['opp_misses_three'] = opp_misses_three
#     absolute_values['turnovers'] = turnovers
#     absolute_values['forced_turnovers'] = forced_turnovers
#     absolute_values['freethrows'] = freethrows
#     absolute_values['misses_freethrow'] = misses_freethrow
#     absolute_values['offensive_rebounds'] = offensive_rebounds
#     absolute_values['defensive_rebounds'] = defensive_rebounds
#     absolute_values['opp_freethrows'] = opp_freethrows
#     absolute_values['opp_misses_freethrow'] = opp_misses_freethrow
#     absolute_values['opp_offensive_rebounds'] = opp_offensive_rebounds
#     absolute_values['opp_defensive_rebounds'] = opp_defensive_rebounds
        
#     return absolute_values


