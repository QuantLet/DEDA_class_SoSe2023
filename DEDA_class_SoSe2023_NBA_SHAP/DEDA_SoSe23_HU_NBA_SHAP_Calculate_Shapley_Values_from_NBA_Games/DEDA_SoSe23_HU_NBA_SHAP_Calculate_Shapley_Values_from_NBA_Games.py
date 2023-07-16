import pandas as pd 
import itertools
import deans_factors
import warnings
import pickle
warnings.filterwarnings('ignore')

def calculate_probas(deans_factors,model):  
    probas = []
    for i, row in deans_factors.iterrows():
        probas.append(model.predict_proba([row[5:]])[0][1])
    return probas

def calculate_shapley(deans_factors,active_players):
    shapley_values={}
    for player in active_players:
        
        # Player playing at any of the 5 positions
        respective_player = deans_factors[(deans_factors['player1']==player) | (deans_factors['player2']==player) |       (deans_factors['player3']==player) | (deans_factors['player4']==player) | (deans_factors['player5']==player) ]
        
        #Calculating |Li|
        combinations = len(respective_player.index)
        
        # calculating n
        number_players = len(active_players)
        
        shapley = 1/(combinations*number_players)*(respective_player['probas'].sum())
        
        shapley_values[player] = shapley
        
    return shapley_values

def to_shap(season,model):
    # Get active roster for the season --> Threshold of max 40 games missed!
    tmp_active = deans_factors.get_active_roster(season,roster)
    
    # Get all possible lineup combinations with active roster
    tmp_combinations = deans_factors.get_combinations(tmp_active)
    
    # calculate deans factors for each combination for the whole season 
    game_deans = pd.DataFrame(deans_factors.deans_factors_season(season,tmp_combinations))
    
    # Fill null values with 0 in order for the models to work
    filled_game_deans = game_deans.fillna(0)
    
    # return the probabililites of winning game according to each coalition
    probas = calculate_probas(filled_game_deans,model)
    
    filled_game_deans['probas'] = probas
    
    shapley_values = calculate_shapley(filled_game_deans,tmp_active)
    
    return shapley_values

def calculate_probas_xgb(deans_factors,model):
    probas = []
    for i, row in deans_factors.iterrows():
        probas.append(model.predict_proba([row[5:]])[0][1])
    return probas

def to_shap_xgb(season,model):
    tmp_active = deans_factors.get_active_roster(season,roster)
    
    tmp_combinations = deans_factors.get_combinations(tmp_active)
    
    game_deans = pd.DataFrame(deans_factors.deans_factors_season(season,tmp_combinations))
    
    filled_game_deans = game_deans.fillna(0)
    
    filled_game_deans = filled_game_deans.rename(renaming,axis='columns')
    
    filled_game_deans_tmp = filled_game_deans.drop(['player1','player2','player3','player4','player5'], axis=1)
    
    probas = model.predict_proba(filled_game_deans_tmp)[:,1]
    
    filled_game_deans['probas'] = probas
    
    shapley_values = calculate_shapley(filled_game_deans,tmp_active)
    
    return shapley_values


# load season data for players 
season = pd.read_csv('lakers_season_18_19_absolute.csv')

# Get active roster for respective season 
roster = pd.read_csv('lakers_rosters.csv',sep=';')
roster = roster[roster['Season']=='18_19']['Player']

# Column name matching (Necessary for xgboost model)
renaming = {'off_fg_perc': 'off_eff_fg_perc', 'def_fg_perc': 'def_eff_fg_perc','off_to_perc':'off_tov_perc','def_to_perc':'def_tov_perc','off_rb_perc':'off_reb_perc','def_rb_perc':'def_reb_perc','off_ft_factor':'off_free_throw_factor','def_ft_factor':'def_free_throw_factor'}

# importing different models
model_log_reg = pickle.load(open('logreg_game_outcome_v2.pkl', 'rb'))
model_dec_tree = pickle.load(open('dtree_game_outcome_v1.pkl', 'rb'))
model_xgbcl = pickle.load(open('xgbcl_game_outcome_v1.pkl', 'rb'))

# Calculate SHAP values for all three models
log_reg_shap_values = to_shap(season,model_log_reg)
xgb_shap_values = to_shap_xgb(season,model_xgbcl)
shap_values_dec_tree = to_shap(season,model_dec_tree)

# Parsing results into dataframe 
log_reg_shap_values = pd.DataFrame(log_reg_shap_values,index=[0])
xgb_shap_values = pd.DataFrame(xgb_shap_values,index=[0])
dec_tree_shap_values = pd.DataFrame(shap_values_dec_tree,index=[0])

# Exporting data to csv for all three models
log_reg_shap_values.to_csv('log_reg_shap_lakers_18_19.csv')
dec_tree_shap_values.to_csv('dec_tree_shap_lakers_18_19.csv')
xgb_shap_values.to_csv('xgbcl_shap_lakers_18_19.csv')
