# Created		2022-04-02
# Updated		2022-09-02
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal			Read only Policy

# Imports
import pandas as pd
import numpy as np
import ReturnMetrics as RM
from scipy.optimize import minimize

def TakeProfit(returnSeries, maximumProfit, threshold = 0.005):
	
	#If maximum Profit greater Threshold then Return is Threshold else it is Return
	returnSeries = np.where(maximumProfit.values > threshold, threshold, returnSeries.values)
	
	return returnSeries

def StopLoss(returnSeries, maximumLoss, threshold = -0.005):
	#If maximum Loss smaller Threshold then Return is Threshold else it is Return
	returnSeries = np.where(maximumLoss.values < threshold, threshold, returnSeries.values)
	
	return returnSeries

def FindBestTakeProfit(returnSeries, maximumProfit, timeFrame):
	
	series = pd.Series(data = [RM.SortinoRatio(TakeProfit(returnSeries, maximumProfit, threshold), timeFrame) for threshold in np.linspace(0.001, 0.03, 10)], \
	index = np.linspace(0.001, 0.03, 10), name = "Sortino Ratio")
	
	return series

def FindBestStopLoss(returnSeries, maximumLoss, timeFrame):
	
	series = pd.Series(data = [RM.SortinoRatio(StopLoss(returnSeries, maximumLoss, -threshold), timeFrame) for threshold in np.linspace(0.001, 0.03, 10)], \
	index = np.linspace(0.001, 0.03, 10), name = "Sortino Ratio")
	
	return series