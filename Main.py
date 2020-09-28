'''
APPROACH
                                                
    1. Clean the data : Create a basket of all stocks that are available only on that rebalancing date.
    
    2. Gather bb_live data of those stocks for the given fixed lookback window.
    
    3. Generate the returns on each day for all stocks from the cleaned bb_live data assets basket.
    
    4. Derive the SPTR Index values for those dates and generate its daily returns.
    
    5. Store all this as class objects    
    
    6. Derive mean and standard deviation(volatility) of the asset and SPTR Index returns.
    
    7. Using the SPTR Index as a benchmark for volatility, classify assets as either risky
        or safe depending upon whether their volatlity in the past 63 days has been more
        than or less than the volatlity of the Index.
        
    8. Also compute their mean returns, volatility and Information ratio using SPTR returns 
        as the benchmark returns. Remove assets from both the baskets which have information 
        ratio less than 0.
        
    9. Perform a Monte-Carlo Simulation to randpmly choose  N assets from the risky basket and 50-N
        assets from the safe basket and create a portfolio. Perform this X number of time and compute
        the information ratio over the defined period for all the portfolios.
        
    10. Rank all the portfolios according to their information ratio and choose the best portfolio as
        the portfolio with the highest information ratio.
    
    11. This becomes our portfolio to which we need to rebalance to. rebalancing is done by default on
        a bi-monthly basis or if any asset currently in the portfolio drops out of the S&P500.
        
'''

'''
One improvement is to keep checking the portfolio on a daily basis and if its information ratio drops
below 0 then rebalance the portfolio.

'''

import alphien
import pandas as pd
import numpy as np
import itertools
import random
import time
from alphien.data import *

def construct(port,data):
    best_portfolios = port.to_frame()
    date = data.available_basket_returns.index[-1]
    temp = pd.DataFrame(index=[date], columns=data.available_basket.columns)
    for i in range(0, best_portfolios.shape[0]):
        temp[best_portfolios.iloc[i,0]] = 0.02
    return temp

def myPayout(df):
    
    sp500 = alphien.data.getTickersSP500()
    tkr = getTickersSP500().ticker.unique().tolist()
    px = alphien.data.getHistoryData(tkr,zoom='2007::2016',field=['bb_live'])
    dataList = alphien.data.getTickersSP500Data()
    sec_data=alphien.data.getHistoryData(dataList.ticker.to_numpy(),zoom="2007::2016")
    final = pd.DataFrame() 
    
    #running for the entire period
    for i in range(0,px.shape[0],42):
        #if less than 42 days are left, then stop the loop and don't rebalance
        if px.shape[0]-i<42:
            break
        #clean and get the required data
        data = alphien.DataPreprocessing(px, sp500, sec_data, df, start=i,lookback=42)
        # evalute trends
        trends = alphien.TrendProcessing(data)
        
        #run monte-carlo and get best portfolio
        portfolio_list, portfolio_metrics, best_portfolio = trends.monte_carlo_sim(1000,40,10)
        
        #construct a dataframe for output to the backtesting function
        best = construct(best_portfolio, data)
        
        #append rebalancing date index with portfolio weights to our final dataframe
        final = final.append(best)
        
    final=final.fillna(0)
    return final ## output