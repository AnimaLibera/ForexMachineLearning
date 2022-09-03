# Created		2022-09-3
# Updated		2022-09-3
# Autor Nickname	AnimaLibera
# Autor RealName	Gianni-Lauritz Grubert
# Legal			Read only Policy

#Imports
import Code.MarketAnalysis as MA
import Code.Portfolio as PF

#Running
MA.Choice("GeneralAnalysis")
PF.Choice("SingleAsset")
PF.Choice("Portfolio")
PF.Choice("MultiPortfolio")
PF.Choice("OptimizationPortfolio")