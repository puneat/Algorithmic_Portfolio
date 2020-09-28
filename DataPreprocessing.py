import pandas as pd
import numpy as np
import itertools
import random

'''
This is a Data Processing class that we use to clean our input data. It utilises a 
fixed window of 21 days (252/12) that we consider as the average number of working days
in a month. The class also makes use of the DataFeatures function of Alphien to get the
availability of stock on any given day. Nonetheless, we also defined our custom function
to do the same (commented out in QLib but removed in notebook).. The steps involved in our 
cleaning decsions are:
    1. Clean the data : Create a basket of all stocks that are available only on that rebalancing date.
    
    2. Gather bb_live data of those stocks for the given fixed lookback window.
    
    3. Generate the returns on each day for all stocks from the cleaned bb_live data assets basket.
    
    4. Derive the SPTR Index values for those dates and generate its daily returns.
    
    5. Store all this as class objects
'''

'''
INPUTS:
    
    1. daily_bb_live: This is the daily bb_live dataframe of all assets in the S&P500 Universe.
    
    2. SP500_data: Ticker data of all the assets that were at any given point in time (2007-2016)
                    in the S&P500. 
                    
    3. other_indicators: This is the other indicator data  from which we extract the SPTR Index
    
    4. df: DataFeatures object of Alphien.
    
    5. start: The starting index from which we start our historical data window.
    
    6. lookback: The lookback period for our historical data window.

'''

class DataPreprocessing():
  def __init__(self, daily_bb_live, SP500_data, other_indicators, df,start, lookback = 21):
    self.daily_bb_live = daily_bb_live
    self.SP500_data = SP500_data
    self.lookback = lookback
    self.start = start
    self.other_indicators = other_indicators
    self.df = df

# Function to convert date columns to datetime objects
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

#creates a universe of all available assets on any given date

    def create_basket(self):
      #available_basket = pd.DataFrame()
      inclusionMatrix = getTickersSP500(ticker=self.df.tickers, startDate=self.df.startDate, endDate=self.df.endDate, asMatrix=True)
      if self.start == 0:
        available_basket = inclusionMatrix[2:self.lookback+2]
      else:
        available_basket = inclusionMatrix[self.start:self.start+self.lookback]
        
      return  available_basket

    self.available_basket = create_basket(self)

#Masks the fixed window to only generate returns for dates that we want and assets that are available.

    def selectable_data(self,index):
      bb_df = pd.DataFrame(index=[self.daily_bb_live.date.iloc[index]])  
      for k in range(0,self.daily_bb_live.shape[1]):
        for j in range(0, self.available_basket.shape[1]):
          if self.daily_bb_live.columns[k]==self.available_basket.columns[j]:
            daily_price = self.available_basket.iloc[index-self.start,j]*self.daily_bb_live.iloc[index,k]
            bb_df[self.daily_bb_live.columns[k]] = None
            bb_df[self.daily_bb_live.columns[k]] = [daily_price]
      return bb_df

#Creates a dataframe object containing our bb_live data masked with available assets

    def create_bb_live_basket(self):
      bb_live_basket = pd.DataFrame()
      for i in range(self.start, self.start + self.lookback): # assuming month has 21 days
        daily_price = selectable_data(self,i)
        bb_live_basket = bb_live_basket.append(daily_price)
      return bb_live_basket

# driver function to clean and create our final bb_live dataframe

    def clean_basket(self):
      temp = create_bb_live_basket(self)
      temp = temp.replace(to_replace=0.0, value=np.nan)
      temp = temp.dropna(axis=1,how='all')
      return temp

    self.available_basket_bb_live = clean_basket(self)

# driver function to  create our returns dataframe
    
    def create_returns_basket(self):
      returns_basket = self.available_basket_bb_live.pct_change()
      returns_basket = returns_basket.dropna(axis=0,how='all')
      return returns_basket

    self.available_basket_returns = create_returns_basket(self)

# helper function to extract the SPTR Index data that is also our benchmark data
    
    def check_date_get_value(self, date):
      df = pd.DataFrame()
      for index in range(0, self.other_indicators.shape[0]):
        if (self.other_indicators['date'].iloc[index]==date):
          df = pd.DataFrame(index=[self.other_indicators.date.iloc[index]])
          df['SPTRIndex'] = None
          df['SPTRIndex'] = [self.other_indicators['SPTR Index'].iloc[index]]
          #df['USGG2YRIndex'] = None
          #df['USGG2YRIndex'] = [self.other_indicators['USGG2YR Index'].iloc[index]]
      return df  

# driver function to extract the SPTR Index data that is also our benchmark data

    def derive_secondary_index(self):
      secondary_index = pd.DataFrame()
      for i in range(0, self.lookback):
        date = self.available_basket_bb_live.index[i]
        index_value = check_date_get_value(self, date)
        secondary_index = secondary_index.append(index_value)
      return secondary_index

    self.secondary_index = derive_secondary_index(self)

#function to extract the SPTR Index returns

    def get_secondary_index_returns(self):
      secondary_returns = self.secondary_index.pct_change()
      secondary_returns = secondary_returns.dropna(axis=0, how='all')
      return secondary_returns

    self.secondary_index_returns = get_secondary_index_returns(self)