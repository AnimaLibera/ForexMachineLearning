# Createdt			2022-03-18
# Updated			2022-04-03
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal				All Rights Reserved

# Imports
import pandas as pd
import ta as ta
import matplotlib.pyplot as plt
from Data import LoadData

def RelativeVolume(volume, window=20):
	meanVolume = volume.rolling(window).mean()
	relativeVolume = volume / meanVolume
	relativeVolume.name = "Relative Volume"
	
	#fig, axes = plt.subplots(3,1)
	#axes[0].plot(volume)
	#axes[1].plot(meanVolume)
	#axes[2].plot(relativeVolume)
	#plt.show()
	
	return relativeVolume
	
def KaufmanAdaptivMovingAverage(close, ChangePercantage = False):
	KAMA = ta.momentum.KAMAIndicator(close).kama()
	KAMA.name = "KAMA"

	if ChangePercantage == True:
		KAMA = KAMA.pct_change(1)
		
	return KAMA

def AverageDirectinalMovementIndex(high, low, close):
	ADX = ta.trend.ADXIndicator(high, low, close).adx()
	
	return ADX
		
def TechnicalAnalysisFeatures(name, timeFrame = "Daily", folder = "Data", setting = "RELVOL-KAMA"):
	df = LoadData(name, timeFrame, folder)
	
	relativeVolume = RelativeVolume(df["volume"])
	onBalanceVolume = ta.volume.OnBalanceVolumeIndicator(close = df["close"], volume = df["volume"], fillna = True).on_balance_volume()
	KAMA = KaufmanAdaptivMovingAverage(df["close"])
	#KAMAPercentage = KaufmanAdaptivMovingAverage(df["close"], ChangePercantage = True)
	
	#print("Type OBV:", type(onBalanceVolume))
	
	if setting == "KAMA":
		indicators = pd.DataFrame(KAMA)
	elif setting == "RELVOL-KAMA":
		indicators = pd.concat([KAMA, relativeVolume], axis=1)
	elif setting == "OBV-KAMA":
		indicators = pd.concat([KAMA, onBalanceVolume], axis=1)
	#df["close"].plot()
	#KAMA.plot()
	#plt.show()
	
	#fig, axes = plt.subplots(2,1)
	#axes[0].plot(df["close"])
	#axes[1].plot(onBalanceVolume)
	#plt.show()
	
	return indicators
	
def TestFunctions():
	#volume = pd.Series([100,120,80,90,100])
	#relativeVolume = RelativeVolume(volume, 2)
	#print(f"Relative Volume: {relativeVolume}")

	features = TechnicalAnalysisFeatures("EURUSD")
	print(features)
	
	
#TestFunctions()