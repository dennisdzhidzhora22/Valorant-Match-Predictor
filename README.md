## Overview:
This project predicts the probability of a team winning the game given a map selection, team compositions for both teams, and the current round score.

## Dependencies:
To run this project, you will need to have [Anaconda](https://www.anaconda.com/download/) installed on your system. This project uses a dedicated Conda environment to manage dependencies and ensure reproducibility.

## Instructions to generate the model and make predictions with it:
Extract valorant.sqlite into the 'data' folder from valorantdata.zip.<br>
Execute every cell in Main.ipynb in order. The last cell will save the model as a file.<br>
Then, run Valorant_Win_Prediction_UI.py, making sure that the model's .pkl file is in the same directory as Valorant_Win_Prediction_UI.py.

## Dataset Source:
https://www.kaggle.com/datasets/visualize25/valorant-pro-matches-full-data/data