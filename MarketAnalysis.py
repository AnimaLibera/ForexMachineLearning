# Createdt		2022-04-03
# Updated		2022-09-01
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal			All Rights Reserved

# Imports
import pandas as pd
import numpy as np
import warnings
import sys
import TechnicalAnalysis as TA
from Data import LoadData

warnings.filterwarnings("ignore")

def TrendBehaviour(high, low, close):
		ADX = TA.AverageDirectinalMovementIndex(high, low, close)
		totalBars = ADX.size
		trendingBars = ADX[ADX > 25].size
		rangingBars = ADX[ADX <= 25].size
		trendingPercentage = 100 / totalBars * trendingBars
		rangingPercentage = 100 / totalBars * rangingBars
		
		return (trendingPercentage, rangingPercentage)

def StandardDeviation(returnSeries):
	return np.std(returnSeries)
	
def AnnualVolatility(returnSeries, timeFrame = "Daily"):
	
	if timeFrame == "Daily":
		annualBars = 252

	return np.std(returnSeries) * np.sqrt(annualBars)

def SeveralMean(returnSeries):
	
	overallMean = np.mean(returnSeries)
	positivMean = np.mean(returnSeries[returnSeries > 0])
	negativMean = np.mean(returnSeries[returnSeries < 0])
	
	return (overallMean, positivMean, negativMean)

def PositivAndNegativBars(returnSeries):
	
	totalBars = returnSeries.size
	positivBars = returnSeries[returnSeries > 0].size
	negativBars = returnSeries[returnSeries < 0].size
	
	return (positivBars / totalBars, negativBars / totalBars)

def PrettyPercentage(value, adjustPercent = False, digits = 2):
	
	if adjustPercent == True:
		value *= 100
	
	return (f"{f'%.{digits}f' % value} %")

def GeneralAnalysis():
	listFolders = ["Major Daily 2021", "Major Daily 2020", "Major Daily 2019", "Major Daily 2018", "Major Daily 2017", "Major Daily 2016", \
	"Major Daily 2015"]
	listFolders.sort()
	majorCurrencyPairs = ["AUDUSD", "EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"]
	timeFrame = "Daily"
	
	# Empty Series
	trending = pd.Series(name = "Trending")
	ranging = pd.Series(name = "Ranging")
	standardDeviation = pd.Series(name = "Standard Deviation")
	annualVolatility = pd.Series(name = "Annual Volatility")
	overallMean = pd.Series(name = "Overall Mean")
	positivMean = pd.Series(name = "Positiv Mean")
	negativMean = pd.Series(name = "Negativ Mean")
	positivBars = pd.Series(name = "Positiv Bars")
	negativBars = pd.Series(name = "Negativ Bars")
	
	for name in majorCurrencyPairs:
		
		# Empty DataFrame
		df = pd.DataFrame()
		
		for folder in listFolders:
			df = pd.concat([df, LoadData(name, timeFrame, folder)])
		
		df["Return"] = df["close"].pct_change(1).fillna(0)
		
		trending[name], ranging[name] = TrendBehaviour(df["high"], df["low"], df["close"])
		standardDeviation[name] = StandardDeviation(df["Return"])
		annualVolatility[name] = AnnualVolatility(df["Return"], "Daily")
		overallMean[name], positivMean[name], negativMean[name] = SeveralMean(df["Return"])
		positivBars[name], negativBars[name] = PositivAndNegativBars(df["Return"])
		
	trending = trending.map(PrettyPercentage)
	ranging = ranging.map(PrettyPercentage)
	standardDeviation = standardDeviation.apply(PrettyPercentage, args = (True,))
	annualVolatility = annualVolatility.apply(PrettyPercentage, args = (True,))
	overallMean = overallMean.apply(PrettyPercentage, args = (True,4))
	positivMean = positivMean.apply(PrettyPercentage, args = (True,))
	negativMean = negativMean.apply(PrettyPercentage, args = (True,))
	positivBars = positivBars.apply(PrettyPercentage, args = (True,))
	negativBars = negativBars.apply(PrettyPercentage, args = (True,))
	
	analysis = pd.DataFrame(data = [trending, ranging, standardDeviation, annualVolatility, overallMean, positivMean, \
									negativMean, positivBars, negativBars])
	analysis = analysis.transpose()
	
	return analysis

def Choice():
	
	argument = "GeneralAnalysis" # Default Argument
	
	if len(sys.argv) > 1:
		argument = sys.argv[1]
	
	if argument in ["GeneralAnalysis", "GA", "1"]:
		GeneralAnalysis().to_html("./Presentation/General Analysis.html")
		print("Finisched General Analysis!")
		print("Saved Result unter Presentation!")
	else:
		print(f"Argument \"{argument}\" not supported!")
	
if __name__ == "__main__":
	Choice()