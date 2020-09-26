import pandas as pd
import numpy as np
import itertools
import random

class DataPreprocessing():
  def __init__(self, daily_bb_live, SP500_data, other_indicators, start, lookback = 21):
    self.daily_bb_live = daily_bb_live
    self.SP500_data = SP500_data
    self.lookback = lookback
    self.start = start
    self.other_indicators = other_indicators


    def convert_to_dates(self):
      SP500_data_ = self.SP500_data
      daily_bb_live_ = self.daily_bb_live
      other_indicators_ = self.other_indicators
      daily_bb_live_['date'] = self.daily_bb_live.index
      other_indicators_['date'] = self.other_indicators.index
      other_indicators_['date'] = pd.to_datetime(other_indicators_['date'])
      SP500_data_['constituentEnd'] = pd.to_datetime(SP500_data_['constituentEnd'])
      SP500_data_['constituentStart'] = pd.to_datetime(SP500_data_['constituentStart'])
      daily_bb_live_['date'] = pd.to_datetime(daily_bb_live_['date'])
      return daily_bb_live_ , SP500_data_ , other_indicators_
    
    self.daily_bb_live, self.SP500_data, self.other_indicators   = convert_to_dates(self)

    def current_sp500_constituents(self, day):
      current_companies_df = pd.DataFrame(index=[day])
      for start in range(0, self.SP500_data.shape[0]):
        if ((self.SP500_data['constituentStart'].iloc[start]<day)==True):
          if (pd.isnull(self.SP500_data['constituentEnd'].iloc[start])==True):
            company = str(self.SP500_data.ticker.iloc[start])
            current_companies_df[company] = None
            current_companies_df[company] = [1]
          elif (pd.isnull(self.SP500_data['constituentEnd'].iloc[start])==False):
            if (self.SP500_data['constituentEnd'].iloc[start]>day)==True:
              company = str(self.SP500_data.ticker.iloc[start])
              current_companies_df[company] = None
              current_companies_df[company] = [1]
          elif (self.SP500_data['constituentEnd'].iloc[start]<day)==True:
            company = str(self.SP500_data.ticker.iloc[start])
            current_companies_df[company] = None
            current_companies_df[company] = [0]
        else:
          company = str(self.SP500_data.ticker.iloc[start])
          current_companies_df[company] = None
          current_companies_df[company] = [0]

      return current_companies_df

    def create_basket(self):
      available_basket = pd.DataFrame()
      for i in range(self.start, self.start + self.lookback): # assuming month has 21 days
        daily_companies = current_sp500_constituents(self,
            self.daily_bb_live.date.iloc[i])
        available_basket = available_basket.append(daily_companies)
      return available_basket

    self.available_basket = create_basket(self)
    ############### correct till here #####################################################

    def selectable_data(self,index):
      bb_df = pd.DataFrame(index=[self.daily_bb_live.date.iloc[index]])  
      for k in range(0,self.daily_bb_live.shape[1]):
        for j in range(0, self.available_basket.shape[1]):
          if self.daily_bb_live.columns[k]==self.available_basket.columns[j]:
            daily_price = self.available_basket.iloc[index-self.start,j]*self.daily_bb_live.iloc[index,k]
            bb_df[self.daily_bb_live.columns[k]] = None
            bb_df[self.daily_bb_live.columns[k]] = [daily_price]
      return bb_df

    def create_bb_live_basket(self):
      bb_live_basket = pd.DataFrame()
      for i in range(self.start, self.start + self.lookback): # assuming month has 21 days
        daily_price = selectable_data(self,i)
        bb_live_basket = bb_live_basket.append(daily_price)
      return bb_live_basket

    def clean_basket(self):
      temp = create_bb_live_basket(self)
      temp = temp.replace(to_replace=0.0, value=np.nan)
      temp = temp.dropna(axis=1,how='all')
      return temp

    self.available_basket_bb_live = clean_basket(self)

    def create_returns_basket(self):
      returns_basket = self.available_basket_bb_live.pct_change()
      returns_basket = returns_basket.dropna(axis=0,how='all')
      return returns_basket

    self.available_basket_returns = create_returns_basket(self)

    def check_date_get_value(self, date):
      df = pd.DataFrame()
      for index in range(0, self.other_indicators.shape[0]):
        if (self.other_indicators['date'].iloc[index]==date):
          df = pd.DataFrame(index=[self.other_indicators.date.iloc[index]])
          df['SPTRIndex'] = None
          df['SPTRIndex'] = [self.other_indicators['SPTR Index'].iloc[index]]
          df['USGG2YRIndex'] = None
          df['USGG2YRIndex'] = [self.other_indicators['USGG2YR Index'].iloc[index]]
      return df  

    def derive_secondary_index(self):
      secondary_index = pd.DataFrame()
      for i in range(0, self.lookback):
        date = self.available_basket_bb_live.index[i]
        index_value = check_date_get_value(self, date)
        secondary_index = secondary_index.append(index_value)
      return secondary_index

    self.secondary_index = derive_secondary_index(self)

    def get_secondary_index_returns(self):
      secondary_returns = self.secondary_index.pct_change()
      secondary_returns = secondary_returns.dropna(axis=0, how='all')
      return secondary_returns

    self.secondary_index_returns = get_secondary_index_returns(self)