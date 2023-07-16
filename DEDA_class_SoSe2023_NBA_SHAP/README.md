# NBA Player Importance (DEDA class SoSe2023)
Determining NBA player importance using game outcome prediction and generalised Shapley values. 

This project is influenced by the methodology described in the paper titled ["Measuring players’ importance in team sports using a generalized version of the Shapley value" (2022)](https://rdcu.be/dcCMR). The paper focuses on evaluating the importance of each player in basketball by determining their average marginal contribution to the utility of a subset of players using the [NBA Database](https://www.kaggle.com/datasets/wyattowalsh/basketball) on Kaggle.

# Data

This dataset is updated regulary and includes:

- 30 teams
- 4800+ players
- 60,000+ games (every game since the inaugural 1946-47 - NBA season)
- Box Scores for over 95% of all games
- Play-by-Play game data with 13M+ rows of Play-by-Play data in all!
- The source code for the creation of this database is accessible here.

# Approach

 1. Train a classifier to predict game outcomes
 2. Make predictions on a lineup level (get win probabilities)
 3. Calculate generalized Shap-values for each player

# Results

[todo]

# Repository Structure
```
Project/
├── DEDA_SoSe23_HU_NBA_SHAP_Calculate_Shapley_Values_from_NBA_Games/    <- SHAP Calculation
├── DEDA_SoSe23_HU_NBA_SHAP_Data_Sourcing_NBA_Games/                    <- ETL
├── DEDA_SoSe23_HU_NBA_SHAP_Graphical_Evaluation_SHAP_NBA/              <- SHAP evaluation graphs
└── DEDA_SoSe23_HU_NBA_SHAP_Modelling_Predict_NBA_Game_Outcome/         <- Game Outcome Classifier Modeling
```
# Citation

[Metulini, R., Gnecco, G. "Measuring players’ importance in basketball using the generalized Shapley value" Ann Oper Res, 2022](https://doi.org/10.1007/s10479-022-04653-z)

[Walsh, W. "NBA Database" Kaggle.com, 2023](https://www.kaggle.com/datasets/wyattowalsh/basketball)


