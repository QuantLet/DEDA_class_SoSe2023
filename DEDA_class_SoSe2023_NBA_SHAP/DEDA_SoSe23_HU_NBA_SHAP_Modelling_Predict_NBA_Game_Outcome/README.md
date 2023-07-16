## [<img src="https://github.com/QuantLet/Styleguide-and-FAQ/blob/master/pictures/qloqo.png" alt="Visit QuantNet">](http://quantlet.de/) **SRMforDA_descriptive** [<img src="https://github.com/QuantLet/Styleguide-and-FAQ/blob/master/pictures/QN2.png" width="60" alt="Visit QuantNet 2.0">](http://quantlet.de/)

```yaml

Name of Quantlet: 'game_outcome_modelling'

Published in: 'DEDA class SoSe23'

Description: 'Modelling of three different models (log. Regression, decision tree, xgboostcl) to predict game outcome of 40.000 NBA games with 8 predictors, called Dean's factors. Additionally, the performance of the model is evaluated through cross validation and their respective ROC curves. Trained models are provided as .pkl files.'

Keywords: 'logistic regression, decision tree, xgboost classifier, model evaluation, AUC, ROC'

Author: 'Oliver Klatt Tustanowski, Jannic Horst, Tobias Klein'

Datafile: 'nba_games_team_level.csv derived from nba.sqlite database (source: https://www.kaggle.com/datasets/wyattowalsh/basketball)'

Output: '.pkl files containing trained models (log regression, decision tree cl, xgboost cl)'