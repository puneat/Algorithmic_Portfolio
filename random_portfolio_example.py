'''
    Example returns safe and risky basket with their sharp ratios
'''

start_ = 0
data = DataPreprocessing(daily, company, indicators, lookback = 21, start =start_)
trend = TrendProcessing(data, 14, 3)
safe, risky= trend.random_portfolio_generator()

#day wise mean returns of all safe assets
safe_returns = safe.mean(axis=1)

#day wise mean returns of all risky assets
risky_returns = risky.mean(axis=1)