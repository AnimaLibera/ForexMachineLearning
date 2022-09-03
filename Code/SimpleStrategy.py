# Created		2022-03-16
# Updated		2022-03-20
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal			Red onyl Policy

# Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Code.ReturnMetrics as RM
from Code.Data import LoadData
	
def SimpleMovingAverage(name):
	df = LoadData(name, "Major Daily 2011-2021")
	df["SMA"] = df["open"].rolling(20).mean()
	df["Previous SMA"] = df["SMA"].shift(1)
	
	# Fill Position with Zeros (No Position is Standard Position)
	df["Positions"] = 0
	
	# Uptrend
	df.loc[df["SMA"] > df["Previous SMA"], "Trend"] = 1

	# Downtrend
	df.loc[df["SMA"] < df["Previous SMA"], "Trend"] = -1

	# Notrend
	df.loc[df["SMA"] == df["Previous SMA"], "Trend"] = 0
	
	# Long Position
	df.loc[df["Trend"] == 1, "Position"] = 1

	# Short Position
	df.loc[df["Trend"] == -1, "Position"] = -1

	# No Position
	df.loc[df["Trend"] == 0, "Position"] = 0
	
	df["Return"] = df["Position"].shift(1) * df["open"].pct_change(1)
	df["Return"] = df["Return"].fillna(value=0)
	
	return df["Return"]

def Portfolio():
	namesList = ["AUDUSD", "EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"]
	
	#Empty DataFrame
	df = pd.DataFrame()
	
	for name in namesList:
		df[f"Return {name}"] = SimpleMovingAverage(name)
	
	df["Return Portfolio"] = df.sum(axis=1)
	
	return RM.TableDesciption(df["Return Portfolio"], "", "SMA")

def Choice():
	Portfolio().to_html("./Presentation/Simple Moving Average Strategie.html")
	print("Finisched calculate Simple Moving Average Strategie")

if __name__ == "__main__":
	Choice()