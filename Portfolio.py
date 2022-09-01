# Createdt			2022-04-02
# Updated			2022-04-04
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal				All Rights Reserved

# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import TechnicalAnalysis as TA
import ta as ta
import warnings
import sys
import ReturnMetrics as RM
import MachineLearning as ML
import Optimization as OM
from Data import LoadData, PreprocessData

warnings.filterwarnings("ignore")

def AverageSpread(closeSeries, name):
	#Source: GlobalPrime
	"AUDUSD", "EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"
	spreadDictionary = {"AUDUSD": 0.000028,"EURUSD": 0.000016, "GBPUSD": 0.000075, "USDCAD": 0.000067, "USDCHF": 0.000073, "USDJPY": 0.0039}
	
	spreadPercentage = 1 - ((closeSeries - spreadDictionary[name]) / closeSeries)
	
	#print("Spread Percentage", spreadPercentage)

	return spreadPercentage
	
def MaximumProfit(df):
	
	#High is maximum Profit
	highSeries = df["Return High"].loc[df["Position"].shift(1) == 1]
	
	#Low is maximum Profit
	lowSeries = df["Return Low"].loc[df["Position"].shift(1) == -1] * -1
	
	#Zero is maximum Profit
	zeroSeries = df["Position"].loc[df["Position"].shift(1) == 0]
	
	#Try to merge on Index
	maximumProfit = pd.concat([highSeries, lowSeries, zeroSeries])
	
	#pd.DataFrame(maximumProfit).to_html("MaxProfit.html")
	
	return maximumProfit
	
def MaximumLoss(df):
	
	#High is maximum Loss
	highSeries = df["Return High"].loc[df["Position"].shift(1) == -1] * -1
	
	#Low is maximum Loss
	lowSeries = df["Return Low"].loc[df["Position"].shift(1) == 1]
	
	#Zero is maximum Loss
	zeroSeries = df["Position"].loc[df["Position"].shift(1) == 0]
	
	#Try to merge on Index
	maximumLoss = pd.concat([highSeries, lowSeries, zeroSeries])
	
	#pd.DataFrame(maximumProfit).to_html("MaxLoss.html")
	
	return maximumLoss
	
def HandleData(name, timeFrame = "Daily", folder = "Data", output = "Full", setting = "RELVOL-KAMA", spread = True, model = "SupportVectorMachineRegressor", splitPercentage = 0.8, optimize = False):
	df = LoadData(name, timeFrame, folder)
	
	#Shift(1) Features because Return is Lagging(1)
	#FillNa(0) is a workaround to have same Length Data
	features = TA.TechnicalAnalysisFeatures(name, timeFrame, folder, setting).shift(1).fillna(0)
	#features = ta.add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True).shift(1).fillna(0)
	
	#Preprocess Data
	df, X_Train, X_Test, Y_Train, Y_Test = PreprocessData(df, features, splitPercentage)
	
	#Machine Learning
	if model == "SupportVectorMachineRegressor":
		prediction = ML.ModelSupportVectorMachineRegressor(X_Train, X_Test, Y_Train, Y_Test)
	elif model == "DecisionTreeRegressor":
		prediction = ML.ModelDecisionTreeRegressor(X_Train, X_Test, Y_Train, Y_Test)
	elif model == "RandomForestRegressor":
		prediction = ML.ModelRandomForestRegressor(X_Train, X_Test, Y_Train, Y_Test)
		
	prediction.index = df.index
	
	# Handel Postions and calculate Return Series, maximum Profit and maximum Loss
	df["Position"] = np.sign(prediction)
	df["Return"] = (df["Return Close"] * df["Position"].shift(1)).fillna(0)
	df["Max Profit"] = MaximumProfit(df)
	df["Max Profit"] = df["Max Profit"].fillna(0)
	df["Max Loss"] = MaximumLoss(df)
	df["Max Loss"] = df["Max Loss"].fillna(0)
	
	# Calculate Spred in Percentage and Subtract it from Return
	# Minus Spread because Return is already adjustet for long short or flat Position in Line 84
	if spread == True:
		spreadSeries = abs(AverageSpread(df["close"], name) * df["Position"]) # Spread Zero if flat Position
		df["Return"] = df["Return"] - spreadSeries
	
	# Order of StopLoss and TakeProfit makes no Different
	if optimize == True:
		df["Return"] = OM.TakeProfit(df["Return"], df["Max Profit"], threshold = 0.005)
		df["Return"] = OM.StopLoss(df["Return"], df["Max Loss"], threshold = -0.005)
	
	# Train, Test or Full Set
	split = int(splitPercentage * len(df))
	
	if output == "Full":
		returnSeries = df["Return"]
		maximumProfit = df["Max Profit"]
		maximumLoss = df["Max Loss"]
	elif output == "Train":
		returnSeries = df["Return"].iloc[:split]
		maximumProfit = df["Max Profit"].iloc[:split]
		maximumLoss = df["Max Loss"].iloc[:split]
	elif output == "Test":
		returnSeries = df["Return"].iloc[split:]
		maximumProfit = df["Max Profit"].iloc[split:]
		maximumLoss = df["Max Loss"].iloc[split:]
	
	return (returnSeries, maximumProfit, maximumLoss)

def DrawdownBreak(returnSeries, threshold = 0.01):
	# Standard Threshold is one Percent
	drawdownSeries = RM.DrawdownSeries(returnSeries)
	
	returnSeries.loc[drawdownSeries.shift(1) >= threshold] = 0
	
	return returnSeries

def OptimizationPortfolio():
	listFolders = ["Major Daily 2021", "Major Daily 2020", "Major Daily 2019", "Major Daily 2018", "Major Daily 2017", "Major Daily 2016", \
	"Major Daily 2015"]
	listFolders.sort()
	majorCurrencyPairs = ["AUDUSD", "EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"]
	settingsList = ["KAMA", "RELVOL-KAMA", "OBV-KAMA"]
	setting = settingsList[1]
	modelList = ["SupportVectorMachineRegressor", "DecisionTreeRegressor", "RandomForestRegressor"]
	model = modelList[0]
	timeFrame = "Daily"
	output = "Test"
	spread = True
	splitPercentage = 0.8	

	#Empty DataFrame
	portfolio = pd.DataFrame()
	
	for name in majorCurrencyPairs:
		
		# Empty Series
		returnSeries = pd.Series()
		maximumProfit = pd.Series()
		maximumLoss = pd.Series()
		
		for folder in listFolders:
			
			returnTuple = HandleData(name, timeFrame, folder, output, setting, spread, model, splitPercentage)
			returnSeries = pd.concat([returnSeries,returnTuple[0]]) #Get Element returnSeries from Tuple
			maximumProfit = pd.concat([maximumProfit,returnTuple[1]]) #Get Element maximumProfit from Tuple
			maximumLoss = pd.concat([maximumLoss,returnTuple[2]]) #Get Element maximumLoss from Tuple

		portfolio[f"Sortino Ratio TP {name}"] = OM.FindBestTakeProfit(returnSeries, maximumProfit, timeFrame)
		portfolio[f"Sortino Ratio SL {name}"] = OM.FindBestStopLoss(returnSeries, maximumLoss, timeFrame)
	
	portfolio.to_html("Optimization Portfolio.html")

def SingleAsset(name = "EURUSD", folder = "Major Daily 2021"):
	#Setting Options
	settingsList = ["KAMA", "RELVOL-KAMA", "OBV-KAMA"]
	modelList = ["SupportVectorMachineRegressor", "DecisionTreeRegressor", "RandomForestRegressor"]
	timeFrame = "Daily"
	setting = settingsList[1]
	SP500 = False
	output = "Test"
	drawdownBreakAssets = False
	breakDrawdownPortfolio = False
	spread = True
	leverage = 1.20
	model = modelList[0]
	
	#Empty DataFrames
	df = pd.DataFrame()
	market = pd.DataFrame()
	
	df[f"Return {name}"] = HandleData(name, timeFrame, folder, output, setting, spread, model)[0] # Get Element returnSeries of Tuple
	market[f"Return {name}"] = LoadData(name, timeFrame, folder)["close"].pct_change(1).fillna(0)
		
	df[f"Return {name}"] = df[f"Return {name}"] * leverage
	market[f"Return {name}"] = market[f"Return {name}"] * leverage
		
	if drawdownBreakAssets == True:
		df[f"Return {name}"] = DrawdownBreak(df[f"Return {name}"], 0.01)
	
	#Get Metrics of Asset
	tableDescritpion = RM.TableDesciption(df[f"Return {name}"], (name + " " + folder), timeFrame, folder, SP500)
	
	tableDescritpion.to_html("Table Asset.html")
			
def Portfolio(folder = "Major Daily 2021"):
	# Source: GlobalPrime
	majorCurrencyPairs = ["AUDUSD", "EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"]
	settingsList = ["KAMA", "RELVOL-KAMA", "OBV-KAMA"]
	modelList = ["SupportVectorMachineRegressor", "DecisionTreeRegressor", "RandomForestRegressor"]
	timeFrame = "Daily"
	setting = settingsList[1]
	SP500 = False
	output = "Test"
	drawdownBreakAssets = False
	breakDrawdownPortfolio = False
	spread = True
	leverage = 1.20
	model = modelList[0]
	
	#Empty DataFrames
	df = pd.DataFrame()
	market = pd.DataFrame()
	
	for name in majorCurrencyPairs:
		df[f"Return {name}"] = HandleData(name, timeFrame, folder, output, setting, spread, model)[0] # Get Element returnSeries of Tuple
		market[f"Return {name}"] = LoadData(name, timeFrame, folder)["close"].pct_change(1).fillna(0)
		
		df[f"Return {name}"] = df[f"Return {name}"] * leverage
		market[f"Return {name}"] = market[f"Return {name}"] * leverage
		
		if drawdownBreakAssets == True:
			df[f"Return {name}"] = DrawdownBreak(df[f"Return {name}"], 0.01)
		
		#print(f"Drawdown {name}: {'%.2f' % RM.MaximumRelativDrawdown(df[f'Return {name}'])}")
	
	# Assets ar Equal Weighted
	df["Return Portfolio"] = df.sum(axis=1) / df.shape[1] # Summation and Number of Columns
	market["Return Market"] = market.sum(axis=1) / market.shape[1]
	
	#Portfolio DrawdownBreak
	if breakDrawdownPortfolio == True:
		df["Return Portfolio"] = DrawdownBreak(df["Return Portfolio"], threshold = 0.02)
	
	#Get Metrics of Market
	#print("Market Describtion")
	#print(RM.ShortDescribtion(market["Return Market"], timeFrame, folder))
	
	#Get Metrics of Portfolio
	return (RM.TableDesciption(df["Return Portfolio"], folder, timeFrame, folder, SP500))
	
	#Show all Returns (Portfolio + Assets)
	#fig, axs = plt.subplots(3)
	#axs[0].plot(df.cumsum() * 100)
	#axs[1].plot(market["Return Market"].cumsum() * 100)
	#axs[2].plot(df["Return Portfolio"].cumsum() * 100)
	#plt.show()

def MultiPortfolio():
	listFolders = ["Major Daily 2021", "Major Daily 2020", "Major Daily 2019", "Major Daily 2018", "Major Daily 2017", "Major Daily 2016", \
	"Major Daily 2015"]
	
	#Empty DataFrame
	tablePortfolios = pd.DataFrame()
	
	for folder in listFolders:
		tablePortfolios = pd.concat([tablePortfolios, Portfolio(folder)], axis = 0)
	
	tablePortfolios.to_html("Table Portfolios.html")

def Choice():
	
	argument = "SingleAsset" # Default Argument
	
	if len(sys.argv) > 1:
		argument = sys.argv[1]
	
	if argument in ["SingleAsset", "SA", "1"]:
		SingleAsset("EURUSD")
		print("Finished calculating SingleAsset!")
	elif argument in ["MultiPortfolio", "MP", "2"]:
		MultiPortfolio()
		print("Finished calculating Multiportfolio!")
	elif argument in ["OptimizationPortfolio", "OP", "3"]:
		OptimizationPortfolio()
		print("Finished calculating OptimizationPortfolio!")
	else:
		print(f"Argument \"{argument}\" not supported!")
	
if __name__ == "__main__":
	Choice()