# Createdt			2022-03-18
# Updated			2022-04-02
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal				All Rights Reserved

# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")

def ModelSupportVectorMachineRegressor(X_Train_Final, X_Test_Final, Y_Train_Final, Y_Test_Final):
	# X Data is TA-Features, Y Data is Label (Returns of Asset)
	
	regressor = SVR(kernel="rbf", epsilon=0.005)
	
	#Fit the Model
	regressor.fit(X_Train_Final, Y_Train_Final)
	
	#Predictions for the whole Dataset
	X = np.concatenate((X_Train_Final, X_Test_Final), axis=0)
	
	df = pd.DataFrame()
	df["prediction"] = regressor.predict(X)
	
	return df

def ModelDecisionTreeRegressor(X_Train_Final, X_Test_Final, Y_Train_Final, Y_Test_Final):
	# X Data is TA-Features, Y Data is Label (Returns of Asset)
	
	regressor = DecisionTreeRegressor(max_depth=6)
	
	#Fit the Model
	regressor.fit(X_Train_Final, Y_Train_Final)
	
	#Predictions for the whole Dataset
	X = np.concatenate((X_Train_Final, X_Test_Final), axis=0)
	
	df = pd.DataFrame()
	df["prediction"] = regressor.predict(X)
	
	return df
	
def ModelRandomForestRegressor(X_Train_Final, X_Test_Final, Y_Train_Final, Y_Test_Final):
	# X Data is TA-Features, Y Data is Label (Returns of Asset)
	
	regressor = RandomForestRegressor(n_estimators = 20, max_depth = 10, max_features = "sqrt", random_state = 1)
	
	#Fit the Model
	regressor.fit(X_Train_Final, Y_Train_Final)
	
	#Predictions for the whole Dataset
	X = np.concatenate((X_Train_Final, X_Test_Final), axis=0)
	
	df = pd.DataFrame()
	df["prediction"] = regressor.predict(X)
	
	return df