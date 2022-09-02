# Created		2022-03-20
# Updated		2022-09-02
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal			Read only Policy
# Imports
import numpy as np
import pandas as pd
import datetime as dt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def ExtractStringDate(date):
	return str(date)[0:10]

def LoadData(name, folder, timeFrame = "Daily"):
	df = pd.read_csv(f"../Data/{folder}/{name}_{timeFrame}.csv", delimiter="\t", index_col="<DATE>", parse_dates=True)
	
	if timeFrame == "Daily":
		df = df.iloc[:,:-2]
		df.columns = ["open", "high", "low", "close", "volume"]
		df.index.name = "timeStamp"
	elif timeFrame == "Hourly":
		df = df.iloc[:,:-2]
		df.columns = ["time", "open", "high", "low", "close", "volume"]
		date = pd.Series(df.index, index=df.index)
		date = date.apply(ExtractStringDate)
		timeStamp = date + "T" + df["time"]
		timeStamp = timeStamp.apply(np.datetime64)
		df.index = timeStamp
		df.index.name = "timeStamp"
		df = df.drop(columns=["time"])
	
	return df

def PreprocessData(df, features, splitPercentage = 0.8):
	
	#FillNa(0) is a workaround to have same Length Data
	#Add ReturnClose (Market Return) to DataFrame
	df["Return Close"] = df["close"].pct_change(1).fillna(0)
	#ReturnHigh is Positiv or Zero
	df["Return High"] = ((1 / df["close"].shift(1) * df["high"]) - 1).fillna(0)
	#ReturnLow is Negativ or Zero
	df["Return Low"] = ((1 / df["close"].shift(1) * df["low"]) - 1).fillna(0)
	
	#Checking Data manual
	#df.to_html("DataFrame.html")
	
	#Split Index
	split = int(splitPercentage * len(features))
	
	#Clearly Represented
	label = df["Return Close"]
	
	# Train Set Creation
	X_Train = features.iloc[:split].shift(-1).fillna(0) # Want to predict the next Element
	Y_Train = label.iloc[:split]
	
	# Test Set Creation
	X_Test = features.iloc[split:].shift(-1).fillna(0) # Want to predict the next Element
	Y_Test = label.iloc[split:]
	
	# Scaling Features
	sc = StandardScaler()
	
	X_Train_SC = sc.fit_transform(X_Train)
	X_Test_SC = sc.transform(X_Test)
	
	# PCA Features
	pca = PCA(n_components=min(features.shape[0], features.shape[1]))
	X_Train_PCA = pca.fit_transform(X_Train_SC)
	X_Test_PCA = pca.transform(X_Test_SC)
	
	return (df, X_Train_PCA, X_Test_PCA, Y_Train, Y_Test)
	
	
#df = (LoadData("EURUSD", "Daily", "Major Daily 2021"))