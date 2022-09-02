# Created			2022-03-16
# Update 			2022-04-01
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal				All Rights Reserved

# Imports
import numpy as np
import pandas as pd
from Data import LoadData

sampleReturn = pd.Series([-0.01,0.02,0.04,0.02,-0.03,-0.01,-0.05,0.04])

# print(sampleReturn)

def ActualReturn(returnSeries):
	return returnSeries.cumsum()[-1] * 100

def AnnualizedReturn(returnSeries, timeFrame = "Daily"):
	internalSeries = returnSeries.fillna(0).to_numpy()
	annualBars = 0
	actualBars = 0
	totalReturn = 0
	annualizedReturn = 0
	
	# Approximation of traded Bars per Year for Forex Markets
	if timeFrame == "Daily":
		annualBars = 252
	elif timeFrame == "Hourly":
		annualBars = 252 * 24
	elif timeFrame == "TestTen":
		annualBars = 10
		
	# Get actual Bars of ReturnTimeSeries
	actualBars = len(returnSeries)
	
	#Calculate Total Return (Compounding Method)
	#totalReturn = (np.cumprod(1 + internalSeries) - 1)[-1] #Get last Element
	
	#Calculate Total Return (Simple Method)
	totalReturn = np.cumsum(internalSeries)[-1] #Get last Element
	
	#Calculate Annual Return and scale it to Hundert
	number = actualBars / annualBars
	annualizedReturn = (np.power((1 + totalReturn),(1/number)) - 1) * 100
	
	return annualizedReturn

def DrawdownSeries(returnSeries):
	internalSeries = returnSeries.fillna(0)
	
	cummulativeReturns = (1 + internalSeries).cumprod()
	#cummulativeReturns = internalSeries.cumsum() + 1
	runningMaximum = np.maximum.accumulate(cummulativeReturns)
	
	#Calculate relativ Drawdown and Change leading Sign to Positiv
	drawdownSeries = ((cummulativeReturns / runningMaximum) - 1) * -1
	
	return drawdownSeries

# Maximum relative Drawdown is a bit to optimistic because Balance (Returns) and not Equity (High and Lows) is used
def MaximumRelativDrawdown(returnSeries):
	drawdownArray = DrawdownSeries(returnSeries)
	maximumRelativDrawdown = np.amax(drawdownArray) * 100
	
	return maximumRelativDrawdown

def Performance(returnSeries, timeFrame = "Daily"):
	annualziedReturn = AnnualizedReturn(returnSeries, timeFrame)
	maximumRelativDrawdown = MaximumRelativDrawdown(returnSeries)
	
	performance = annualziedReturn / maximumRelativDrawdown
	
	return performance

def SortinoRatio(returnSeries, timeFrame = "Daily"):
	
	if timeFrame == "Daily":
		annualBars = 252
	elif timeFrame == "Hourly":
		annualBars = 252 * 24
	
	#Calculate Annualized Sortino Ratio
	mean = np.mean(returnSeries)
	downwardVolatility = np.std(returnSeries[returnSeries < 0])
	sortinoRatio = np.sqrt(annualBars) * mean / downwardVolatility
	
	return sortinoRatio

def Beta(returnSeries, folder = "SP500", timeFrame = "Daily"):
	df = LoadData("SP500", folder, timeFrame)
	benchmarkSeries = df["close"].pct_change(1)
	benchmarkSeries.name = "Return SP500"
	
	values = pd.concat((returnSeries, benchmarkSeries), axis=1).dropna()
	covarianceVarianceMatrix = np.cov(values.values, rowvar=False)
	covarianceReturnBenchmark = covarianceVarianceMatrix[0][1]
	varianceBenchmark = covarianceVarianceMatrix[1][1]
	
	beta = covarianceReturnBenchmark / varianceBenchmark
	
	#print(f"covarianceReturnBenchmark:\t\t{'%.10f' % covarianceReturnBenchmark}")
	#print(f"varianceBenchmark:\t\t{'%.10f' % varianceBenchmark}")
	
	return beta
	
def Alpha(returnSeries, folder = "SP500", timeFrame = "Daily"):
	df = LoadData("SP500", folder, timeFrame)
	benchmarkSeries = df["close"].pct_change(1)
	benchmarkSeries.name = "Return SP500"
	
	if timeFrame == "Daily":
		annualBars = 252
	elif timeFrame == "Hourly":
		annualBars = 252 * 24
	
	meanReturn = returnSeries.mean() * annualBars
	meanBenchmark = benchmarkSeries.mean() * annualBars
	beta = Beta(returnSeries, folder, timeFrame)
	
	alpha = (meanReturn - beta * meanBenchmark) * 100
	
	return alpha

def RiskRewardRatio(returnSeries):
	# Approximation because each Bar counts as Trade
	risk = abs(returnSeries[returnSeries < 0].mean())
	reward = returnSeries[returnSeries > 0].mean()
	ratio = reward / risk
	
	return ratio

def WinRate(returnSeries):
	# Approximation because each Bar counts as Trade
	winTrades = len(returnSeries[returnSeries > 0])
	totalTrades = len(returnSeries)
	winRate = winTrades / totalTrades * 100
	
	return winRate
	
def LossRate(returnSeries):
	# Approximation because each Bar counts as Trade
	lossTrades = len(returnSeries[returnSeries < 0])
	totalTrades = len(returnSeries)
	lossRate = lossTrades / totalTrades * 100
	
	return lossRate

def Expectancy(returnSeries):
	# Approximation because each Bar counts as Trade
	winRate = WinRate(returnSeries) / 100
	lossRate = LossRate(returnSeries) / 100
	meanWinner = returnSeries[returnSeries > 0].mean()
	meanLosser = abs(returnSeries[returnSeries < 0].mean())
	expectancy = (meanWinner * winRate - meanLosser * lossRate) * 100
	
	return expectancy

def Edge(returnSeries):
	# Approximation because each Bar counts as Trade
	riskRewardRatio = RiskRewardRatio(returnSeries)
	breakEvenRate = 100 / (riskRewardRatio + 1)
	winRate = WinRate(returnSeries)
	edge = winRate - breakEvenRate
	
	return edge
	
def ShortDescribtion(returnSeries, folder, timeFrame = "Daily"):
	message = (f"Actual Return:\t\t\t{'%.2f' % ActualReturn(returnSeries)} %\n")
	message += (f"Annualized Return:\t\t{'%.2f' % AnnualizedReturn(returnSeries, timeFrame)} % p.a.\n")
	message +=(f"Maximum Relativ Drawdown:\t{'%.2f' % MaximumRelativDrawdown(returnSeries)} %\n")
	message +=(f"Performance:\t\t\t{'%.2f' % Performance(returnSeries, timeFrame)}\n")
	
	return message

def LongDescribtion(returnSeries, folder, timeFrame = "Daily", SP500 = True):
	message = (f"Actual Return:\t\t\t{'%.2f' % ActualReturn(returnSeries)} %\n")
	message += (f"Annualized Return:\t\t{'%.2f' % AnnualizedReturn(returnSeries, timeFrame)} % p.a.\n")
	message += (f"Maximum Relativ Drawdown:\t{'%.2f' % MaximumRelativDrawdown(returnSeries)} %\n")
	message += (f"Performance:\t\t\t{'%.2f' % Performance(returnSeries, timeFrame)}\n")
	
	if SP500 == True:
		SP500Folder = "SP500"
		message += (f"Alpha SP500:\t\t\t{'%.2f' % Alpha(returnSeries, SP500Folder, timeFrame)}\n")
		message += (f"Beta SP500:\t\t\t{'%.3f' % Beta(returnSeries, SP500Folder, timeFrame)}\n")
		
	message += (f"Annualized Sortino Ratio:\t{'%.3f' % SortinoRatio(returnSeries, timeFrame)}\n")
	message += (f"Risk-Reward-Ratio:\t\t{'%.2f' % RiskRewardRatio(returnSeries)}\n")
	message += (f"WinRate:\t\t\t{'%.2f' % WinRate(returnSeries)} %\n")
	message += (f"LossRate:\t\t\t{'%.2f' % LossRate(returnSeries)} %\n")
	message += (f"Expectancy:\t\t\t{'%.4f' % Expectancy(returnSeries)} %\n")
	message += (f"Edge:\t\t\t\t{'%.2f' % Edge(returnSeries)} %\n")
	message += (f"Number of Trades / Bars:\t{len(returnSeries)}\n")
	
	return message

def TableDesciption(returnSeries, folder, name = "Default", timeFrame = "Daily", SP500 = True):
	index = ["Actual Return", "Annualized Return", "Maximum Relativ Drawdown", "Performance"]
	values = [f"{'%.2f' % ActualReturn(returnSeries)} %", f"{'%.2f' % AnnualizedReturn(returnSeries, timeFrame)} % p.a."]
	values += [f"{'%.2f' % MaximumRelativDrawdown(returnSeries)} %", f"{'%.2f' % Performance(returnSeries, timeFrame)}"]
	
	if SP500 == True:
		SP500Folder = "SP500"
		index += ["Alpha SP500", "Beta SP500"]
		values += [f"{'%.2f' % Alpha(returnSeries, SP500Folder, timeFrame)}", f"{'%.3f' % Beta(returnSeries, SP500Folder, timeFrame)}"]
	
	index += ["Annualized Sortino Ratio", "Risk-Reward-Ratio", "WinRate", "LossRate", "Expectancy", "Edge", "Number of Trades / Bars"]
	values += [f"{'%.3f' % SortinoRatio(returnSeries, timeFrame)}", f"{'%.2f' % RiskRewardRatio(returnSeries)}"]
	values += [f"{'%.2f' % WinRate(returnSeries)} %", f"{'%.2f' % LossRate(returnSeries)} %"]
	values += [f"{'%.4f' % Expectancy(returnSeries)} %", f"{'%.2f' % Edge(returnSeries)} %"]
	values += [f"{len(returnSeries)}"]
		
	df = pd.DataFrame(data = values, index = index, columns = [name])
	df = df.transpose()
	#df.style.set_properties(**{'text-align': 'left'})
	
	return df
	
	