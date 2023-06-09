def calc_absolute_values(absolute_values, stats_game,player):
    absolute_values.setdefault(f'{player}_twopointers', []).append(stats_game[player].twopointers)
    absolute_values.setdefault(f'{player}_threepointers',[]).append(stats_game[player].threepointers)
    absolute_values.setdefault(f'{player}_misses_two',[]).append(stats_game[player].misses_two)
    absolute_values.setdefault(f'{player}_misses_three',[]).append(stats_game[player].misses_three)
    absolute_values.setdefault(f'{player}_opp_twopointers',[]).append(stats_game[player].opp_twopointers)
    absolute_values.setdefault(f'{player}_opp_threepointers',[]).append(stats_game[player].opp_threepointers)
    absolute_values.setdefault(f'{player}_opp_misses_two',[]).append(stats_game[player].opp_misses_two)
    absolute_values.setdefault(f'{player}_opp_misses_three',[]).append(stats_game[player].opp_misses_three)
    absolute_values.setdefault(f'{player}_turnovers',[]).append(stats_game[player].turnovers)
    absolute_values.setdefault(f'{player}_forced_turnovers',[]).append(stats_game[player].forced_turnovers)
    absolute_values.setdefault(f'{player}_freethrows',[]).append(stats_game[player].freethrows)
    absolute_values.setdefault(f'{player}_misses_freethrow',[]).append(stats_game[player].misses_freethrow)
    absolute_values.setdefault(f'{player}_offensive_rebounds',[]).append(stats_game[player].offensive_rebounds)
    absolute_values.setdefault(f'{player}_defensive_rebounds',[]).append(stats_game[player].defensive_rebounds)
    absolute_values.setdefault(f'{player}_opp_freethrows',[]).append(stats_game[player].opp_freethrows)
    absolute_values.setdefault(f'{player}_opp_misses_freethrow',[]).append(stats_game[player].opp_misses_freethrow)
    absolute_values.setdefault(f'{player}_opp_offensive_rebounds',[]).append(stats_game[player].opp_offensive_rebounds)
    absolute_values.setdefault(f'{player}_opp_defensive_rebounds',[]).append(stats_game[player].opp_defensive_rebounds)
    
    
def calc_absolute_values_inactive(absolute_values, stats_game,player):
    
    absolute_values.setdefault(f'{player}_twopointers', []).append(None)
    absolute_values.setdefault(f'{player}_threepointers',[]).append(None)
    absolute_values.setdefault(f'{player}_misses_two',[]).append(None)
    absolute_values.setdefault(f'{player}_misses_three',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_twopointers',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_threepointers',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_misses_two',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_misses_three',[]).append(None)
    absolute_values.setdefault(f'{player}_turnovers',[]).append(None)
    absolute_values.setdefault(f'{player}_forced_turnovers',[]).append(None)
    absolute_values.setdefault(f'{player}_freethrows',[]).append(None)
    absolute_values.setdefault(f'{player}_misses_freethrow',[]).append(None)
    absolute_values.setdefault(f'{player}_offensive_rebounds',[]).append(None)
    absolute_values.setdefault(f'{player}_defensive_rebounds',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_freethrows',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_misses_freethrow',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_offensive_rebounds',[]).append(None)
    absolute_values.setdefault(f'{player}_opp_defensive_rebounds',[]).append(None)