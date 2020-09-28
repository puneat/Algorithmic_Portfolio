import pandas as pd
import numpy as np
import itertools
import random

'''
This is a Trend Processing class that we use to find our optimal portfolio
assets to choose on any given rebalancing date. The steps involved in our 
allocation decsions are:

    1. Derive mean and standard deviation(volatility) of the asset and SPTR Index returns.
    
    2. Using the SPTR Index as a benchmark for volatility, classify assets as either risky
        or safe depending upon whether their volatlity in the past 63 days has been more
        than or less than the volatlity of the Index.
        
    3. Also compute their mean returns, volatility and Information ratio using SPTR returns 
        as the benchmark returns. Remove assets from both the baskets which have information 
        ratio less than 0.
        
    4. Perform a Monte-Carlo Simulation to randpmly choose  N assets from the risky basket and 50-N
        assets from the safe basket and create a portfolio. Perform this X number of time and compute
        the information ratio over the defined period for all the portfolios.
        
    5. Rank all the portfolios according to their information ratio and choose the best portfolio as
    the portfolio with the highest information ratio.
    
    6. This becomes our portfolio to which we need to rebalance to. rebalancing is done by default on
        a bi-monthly basis or if any asset currently in the portfolio drops out of the S&P500.

The class inherits from the DataPreprocessing class.

'''
class TrendProcessing():
  def __init__(self, data_preprocessing):
    self.data = data_preprocessing

# derive mean and standard deviation

    def derive_stats(self):
      data_stats = self.data.available_basket_returns.describe()
      secondary_stats = self.data.secondary_index_returns.describe()
      return data_stats, secondary_stats

    self.data_stats, self.secondary_stats = derive_stats(self)

# build the safe and risky baskets based on volatility

    def build_safe_risky_baskets(self):
      risky_assets_ = pd.DataFrame()
      safe_assets_ = pd.DataFrame()

      benchmark_volatility = 1.5*self.secondary_stats.iloc[2,0]

      benchmark_return = self.secondary_stats.iloc[1,0]

      for i in range(0, self.data_stats.shape[1]):
        if (self.data_stats.iloc[2,i] > benchmark_volatility):

          risky_assets = pd.DataFrame(index=[self.data_stats.columns[i]])

          risky_assets['Returns'] = self.data_stats.iloc[1,i]

          risky_assets['Volatility'] = self.data_stats.iloc[2,i]
          
          risky_assets['InformationRatio'] = (self.data_stats.iloc[1,i] - benchmark_return)/np.std(
              self.data.available_basket_returns[self.data_stats.columns[i]]-benchmark_return)
          
          risky_assets_  = risky_assets_.append(risky_assets)

        elif (self.data_stats.iloc[2,i] <= benchmark_volatility):

          safe_assets = pd.DataFrame(index=[self.data_stats.columns[i]])

          safe_assets['Returns'] = self.data_stats.iloc[1,i]

          safe_assets['Volatility'] = self.data_stats.iloc[2,i]
          
          safe_assets['InformationRatio'] = (self.data_stats.iloc[1,i] - benchmark_return)/np.std(
              self.data.available_basket_returns[self.data_stats.columns[i]]-benchmark_return)
          
          safe_assets_  = safe_assets_.append(safe_assets)

      risky_assets_ = risky_assets_[risky_assets_['InformationRatio'] >= 0]
      safe_assets_ = safe_assets_[safe_assets_['InformationRatio'] >= 0]
      
      return risky_assets_, safe_assets_

    self.risky_universe, self.safe_universe = build_safe_risky_baskets(self)
    
# random portfolio generator function that outputs a list of 50 stocks randomly chosen from the safe
# and risky baskets.

  def random_portfolio_generator(self, num_of_risky_assets, num_of_safe_assets):
      
    safe_pick = pd.DataFrame()
    risky_pick = pd.DataFrame()

    if self.risky_universe.shape[0] < num_of_risky_assets:
      risky_sample = list(random.sample(list(self.risky_universe.index),self.risky_universe.shape[0]))
      safe_sample = list(random.sample(list(self.safe_universe.index),(num_of_safe_assets+(num_of_risky_assets - self.risky_universe.shape[0]))))

    elif self.safe_universe.shape[0] < num_of_safe_assets:
      safe_sample = list(random.sample(list(self.safe_universe.index),self.safe_universe.shape[0]))
      risky_sample = list(random.sample(list(self.risky_universe.index),(num_of_risky_assets+(num_of_safe_assets - self.safe_universe.shape[0]))))
    else:
      safe_sample = list(random.sample(list(self.safe_universe.index),num_of_safe_assets))
      risky_sample = list(random.sample(list(self.risky_universe.index),num_of_risky_assets))


    for i in range(0, len(safe_sample)):
      safe_pick[safe_sample[i]] = None
      safe_pick[safe_sample[i]] = self.data.available_basket_returns[safe_sample[i]]

    for i in range(0,len(risky_sample)):
      risky_pick[risky_sample[i]] = None
      risky_pick[risky_sample[i]] = self.data.available_basket_returns[risky_sample[i]]

    portfolio = pd.concat([risky_pick, safe_pick], axis=1)
          
    return portfolio
  
#driver function to generate a number of portfolios, rank them and choose the best portfolio among them.

  def monte_carlo_sim(self, number_of_sims, risky, safe):
    portfolio_list = pd.DataFrame()
    portfolio_metrics = pd.DataFrame()
    rows = []
    for i in range(0, number_of_sims):
      rows.append(i)
      metrics=[]
      random_portfolio = self.random_portfolio_generator(risky, safe)
      portfolio_list = portfolio_list.append([random_portfolio.columns])

      day_returns = random_portfolio.mean(axis=1)
      info_ratio = (day_returns.mean() - self.secondary_stats.iloc[1,0])/np.std(day_returns-self.secondary_stats.iloc[1,0])
      metrics.append(info_ratio)

      portfolio_metrics = portfolio_metrics.append([metrics])

    portfolio_list = portfolio_list.set_index([rows])
    portfolio_metrics = portfolio_metrics.set_index([rows])
    portfolio_metrics.columns=["InformationRatio"]
    portfolio_metrics = portfolio_metrics.sort_values(by=["InformationRatio"],ascending=False)
    best_portfolio = portfolio_list.loc[portfolio_metrics.index[0]]

    return portfolio_list, portfolio_metrics, best_portfolio