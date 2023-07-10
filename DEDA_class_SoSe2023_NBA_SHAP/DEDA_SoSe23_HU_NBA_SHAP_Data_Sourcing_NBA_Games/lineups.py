import pandas as pd
def play_by_play_lineup(game_example):
    lineup_home = []
    lineup_away = []

    current_lineup_home = []
    current_lineup_away = []

    # Getting starting 5
    
    for index, row in game_example.iterrows():


        if row[0]==8 or row[0]==1 or row[0]==2:
            # Starting lineup of home team
            if len(lineup_home)<5 and row[5]!=None and row[2] not in lineup_home:

                lineup_home.append(f'{row[2]}')

            # Starting lineup of away team 
            if len(lineup_away)<5 and row[5]==None and row[2] not in lineup_away:

                lineup_away.append(f'{row[2]}')
                
        

        # break if both lineups full
        if len(lineup_home)==5 and len(lineup_away)==5:
            break

    for index, row in game_example.iterrows():

        if row[0]==8 and row[5]!=None and row[2]!=None and row[3]!=None:

            lineup_home_tmp = list(map(lambda x: x.replace(row[2], row[3]), lineup_home))

            if len(lineup_home_tmp) == len(set(lineup_home_tmp)):
                lineup_home = lineup_home_tmp

            
        if row[0]==8 and row[5]==None and row[2]!=None and row[3]!=None:

            lineup_away_tmp = list(map(lambda x: x.replace(row[2], row[3]), lineup_away))
            
            
            if len(lineup_away_tmp) == len(set(lineup_away_tmp)):
                lineup_away = lineup_away_tmp

        current_lineup_home.append(lineup_home[:])
        current_lineup_away.append(lineup_away[:])
        
    lineups = pd.DataFrame(data=[current_lineup_home,current_lineup_away])
    lineups = lineups.T
    lineups = lineups.rename(columns={0:'lineup_home',1:'lineup_away'})
    return lineups