'''
    Example returns safe and risky basket with their sharp ratios
'''

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import random
import time

daily = pd.read_csv('/gdrive/My Drive/UBS/S&P500/data/bb_live.csv')
company = pd.read_csv('/gdrive/My Drive/UBS/S&P500/data/company_data.csv')
indicators = pd.read_csv('/gdrive/My Drive/UBS/S&P500/data/secondary_data.csv')

start_ = 0

data = DataPreprocessing(daily, company, indicators, lookback = 21, start =start_)
trends = TrendProcessing(data, 7, 3)
st = time.perf_counter()

optimal_portfolio, best_ir_portfolio, best_div_portfolio = trends.monte_carlo_sim(1000)

end  = time.perf_counter()
print(end-st)
