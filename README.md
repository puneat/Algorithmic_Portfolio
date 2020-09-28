# Algorithmic Portfolio Selection
Quantitative way to build a portfolio of N stocks picked from the S&amp;P 500 to beat the monthly returns of the S&amp;P 500

<b> Approach
  
  <li> Derive mean and standard deviation(volatility) of the asset and SPTR Index returns.</li>
    
  <li> Using the SPTR Index as a benchmark for volatility, classify assets as either risky
        or safe depending upon whether their volatlity in the past 63 days has been more
        than or less than the volatlity of the Index.</li>
        
  <li> Also compute their mean returns, volatility and Information ratio using SPTR returns 
        as the benchmark returns. Remove assets from both the baskets which have information 
        ratio less than 0.</li>
        
  <li> Perform a Monte-Carlo Simulation to randpmly choose  N assets from the risky basket and 50-N
        assets from the safe basket and create a portfolio. Perform this X number of time and compute
        the information ratio over the defined period for all the portfolios.</li>
        
  <li> Rank all the portfolios according to their information ratio and choose the best portfolio as
        the portfolio with the highest information ratio.</li>
    
  <li> becomes our portfolio to which we need to rebalance to. rebalancing is done by default on
        a bi-monthly basis or if any asset currently in the portfolio drops out of the S&P500.</li>
