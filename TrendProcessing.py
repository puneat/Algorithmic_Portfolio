import pandas as pd
import numpy as np
import itertools
import random

class TrendProcessing():
  def __init__(self, data_preprocessing, ma_far=21, ma_near=7):
    self.data = data_preprocessing
    self.ma_far = ma_far
    self.ma_near = ma_near

    def derive_stats(self):
      data_stats = self.data.available_basket_returns.describe()
      secondary_stats = self.data.secondary_index_returns.describe()
      return data_stats, secondary_stats  # mean = 1, std =2

    self.data_stats, self.secondary_stats = derive_stats(self)

    def get_sma_far(self):
      sma_far_ = self.data.available_basket_bb_live.rolling(self.ma_far).mean()
      sma_far_ = sma_far_.dropna(axis=0, how='all')
      return sma_far_

    #self.sma_far_val = get_sma_far(self)

    def get_sma_near(self):
      sma_near_ = self.data.available_basket_bb_live.rolling(self.ma_near).mean()
      sma_near_ = sma_near_.dropna(axis=0, how='all')
      return sma_near_

    #self.sma_near_val = get_sma_near(self)

    def get_ema_far(self):
      ema_far_ = self.data.available_basket_bb_live.ewm(span = self.ma_far, adjust=False).mean()
      ema_far_ = ema_far_.dropna(axis=0, how='all')
      return ema_far_

    #self.ema_far_val = get_ema_far(self)

    def get_ema_near(self):
      ema_near_ = self.data.available_basket_bb_live.ewm(span = self.ma_near, adjust=False).mean()
      ema_near_ = ema_near_.dropna(axis=0, how='all')
      return ema_near_

    #self.ema_near_val = get_ema_near(self)

    def build_safe_risky_baskets(self):
      risky_assets_ = pd.DataFrame()
      safe_assets_ = pd.DataFrame()

      benchmark_volatility = 1.5*self.secondary_stats.iloc[2,0]
      risk_free_volatility = self.secondary_stats.iloc[2,1]
      risk_free_return = self.secondary_stats.iloc[1,1]
      benchmark_return = self.secondary_stats.iloc[1,0]

      for i in range(0, self.data_stats.shape[1]):
        if (self.data_stats.iloc[2,i] > benchmark_volatility):

          risky_assets = pd.DataFrame(index=[self.data_stats.columns[i]])

          risky_assets['Returns'] = self.data_stats.iloc[1,i]

          risky_assets['Volatility'] = self.data_stats.iloc[2,i]

          risky_assets['SharpeRatio'] = (self.data_stats.iloc[1,i] - risk_free_return)/np.std(
                self.data.available_basket_returns[self.data_stats.columns[i]]-risk_free_return)
          
          risky_assets['InformationRatio'] = (self.data_stats.iloc[1,i] - benchmark_return)/np.std(
              self.data.available_basket_returns[self.data_stats.columns[i]]-benchmark_return)
          
          risky_assets_  = risky_assets_.append(risky_assets)

        elif (self.data_stats.iloc[2,i] <= benchmark_volatility):

          safe_assets = pd.DataFrame(index=[self.data_stats.columns[i]])

          safe_assets['Returns'] = self.data_stats.iloc[1,i]

          safe_assets['Volatility'] = self.data_stats.iloc[2,i]

          safe_assets['SharpeRatio'] = (self.data_stats.iloc[1,i] - risk_free_return)/np.std(
              self.data.available_basket_returns[self.data_stats.columns[i]]-risk_free_return)
          
          safe_assets['InformationRatio'] = (self.data_stats.iloc[1,i] - benchmark_return)/np.std(
              self.data.available_basket_returns[self.data_stats.columns[i]]-benchmark_return)
          
          safe_assets_  = safe_assets_.append(safe_assets)

      risky_assets_ = risky_assets_[risky_assets_['InformationRatio'] >= 0]
      safe_assets_ = safe_assets_[safe_assets_['InformationRatio'] >= 0]

      #risky_assets_ = risky_assets_.sort_values(by=['InformationRatio'], ascending=False)
      #safe_assets_ = safe_assets_.sort_values(by=['InformationRatio'], ascending=False)
      
      return risky_assets_, safe_assets_

    self.risky_universe, self.safe_universe = build_safe_risky_baskets(self)

  def random_portfolio_generator(self, risk_num, safe_num):
      # split is 30% safe and 70% risky
    safe_pick = pd.DataFrame()
    risky_pick = pd.DataFrame()
    risky_sample = list(random.sample(list(self.risky_universe.index),risk_num))
    safe_sample = list(random.sample(list(self.safe_universe.index),safe_num))

    for i in range(0, len(safe_sample)):
      for j in range(0, self.data.available_basket_returns.shape[1]):
        if (safe_sample[i] == self.data.available_basket_returns.columns[j]):
          safe_pick[safe_sample[i]] = None
          safe_pick[safe_sample[i]] = self.data.available_basket_returns.iloc[:,j]

    for i in range(0,len(risky_sample)):
      for j in range(0, self.data.available_basket_returns.shape[1]):
        if (risky_sample[i] == self.data.available_basket_returns.columns[j]):
          risky_pick[risky_sample[i]] = None
          risky_pick[risky_sample[i]] = self.data.available_basket_returns.iloc[:,j]

    portfolio = pd.concat([risky_pick, safe_pick], axis=1)
          
    return portfolio

  def monte_carlo_sim(self, number_of_sims,risk_num, safe_num):
    max_info_ratio = -1000
    max_diversification_ratio = 1000
    max_score = -100
    
    for i in range(0,number_of_sims):
      random_portfolio = self.random_portfolio_generator(risk_num, safe_num)
      consolidated_portfolio = random_portfolio.mean(axis=1)
      info_ratio = (consolidated_portfolio.mean() - self.secondary_stats.iloc[1,0])/np.std(consolidated_portfolio-self.secondary_stats.iloc[1,0])
      corr = np.corrcoef(random_portfolio,random_portfolio)
      diversification_ratio = corr[np.triu_indices_from(corr,1)].mean()
      score = 0.625*info_ratio - 0.375*abs(diversification_ratio)

      if info_ratio > max_info_ratio:
        max_info_ratio = info_ratio
        best_ir_portfolio = random_portfolio
        best_ir_score = score
        best_ir_dr = diversification_ratio

      if abs(diversification_ratio)!=0:
        if abs(diversification_ratio) < abs(max_diversification_ratio):
          max_diversification_ratio = diversification_ratio
          best_diversified_portfolio = random_portfolio
          best_dr_score = score
          best_dr_ir = info_ratio

      if score > max_score:
        max_score = score
        optimal_portfolio = random_portfolio
        optimal_dr = diversification_ratio
        optimal_ir = info_ratio
    
    print('Maximum Portfolio Information Ratio, DR, Score: ', max_info_ratio," , ",best_ir_dr," , ",best_ir_score )
    print('Maximum Portfolio Diversification Ratio, IR, Score: ', max_diversification_ratio," , ",best_dr_ir," , ",best_dr_score)
    print('Maximum Portfolio Score, DR, IR: ', max_score," , ",optimal_dr," , ",optimal_ir )

    return optimal_portfolio, best_ir_portfolio, best_diversified_portfolio