import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web

import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.stats.mstats import mquantiles
import statsmodels.api as sm

def get_single_stock_data(start_date,end_date,symbol,source):
    '''
    start_date: datetime.datetime; first date to download stock data
    end_date: datetime.datetime; last date to download stock data
    symbol: string; stock symbol specific to the data source 
    source: string; data source to get stock info from

    Example: 
    start_date = datetime.datetime(2010,1,1)
    end_date = datetime.datetime(2018,1,1)
    symbol = "IBM"   ("F")
    source = "yahoo"   ("google")
    '''
    data = web.DataReader(symbol,source,start_date,end_date)
    return data
if __name__ == "__main__":
    start_date = datetime.datetime(2017, 1, 1)
    end_date = datetime.datetime(2020, 9, 1)
    symbol = "TSLA"
    source = "yahoo"

    # download data 
    data = get_single_stock_data(start_date,end_date,symbol,source)


    # download index 
    ind_data = get_single_stock_data(start_date,end_date,'^DJI',source) 

    # computed the daily returns
    rtn_srs = data.Close.pct_change(1).dropna()

    # computed volatility on a rolling basis looking back 252 days (1 trading year)
    rolling_volatility = rtn_srs.rolling(252).std()

    # Sharpe Ratio (daily return/daily volatility)
    rolling_return = rtn_srs.rolling(252).sum() # Year over year return
    rolling_mean_rtn = rtn_srs.rolling(252).mean() # average daily return 
    
    rolling_sharpe_ratio = np.sqrt(252.)*rolling_mean_rtn/rolling_volatility  # rolling daily daily

    # VaR (Value at Risk)
    # 95% VaR or equiv. the q=0.05 quantile of the return distribution
    var99, var95 = mquantiles(rtn_srs,[0.01,0.05])
    print("95% VaR: " + str(round(100*var95,4)) + "%")
    print("99% VaR: " + str(round(100*var99,4)) + "%")

    # Rolling Value at Risk
    varfct = lambda x: float(mquantiles(x,[0.05]))
    rolling_var95 = rtn_srs.rolling(252).apply(varfct)
    
    # Beta to the S&P 500
    index_return = ind_data.Close.pct_change(1).dropna()
    x = index_return.values
    y = rtn_srs.values
    x = sm.add_constant(x)
    model = sm.OLS(y,x)   
    results = model.fit()
    alpha,beta = results.params

    ## do rolling beta over past 1 year!

    plt.figure(1)
    plt_data = data['Close']
    plt.plot(plt_data.index,plt_data.values)  ## display x and y values of the stock
    plt.xlabel('Date')
    plt.ylabel('Closing Prices')
    title_str = 'End of Day Closing Prices for ' + symbol + ' for Source ' + source
    plt.title(title_str)
    plt.gcf().autofmt_xdate()

    plt.figure(2)
    plt.plot(rolling_volatility.index,rolling_volatility.values)
    plt.xlabel('Date')
    plt.ylabel('Daily Volatility')
    title_str = '252 Day Rolling Volatility of ' + symbol + ' for Source ' + source
    plt.title(title_str)

    plt.figure(3)
    plt.plot(rolling_sharpe_ratio.index,rolling_sharpe_ratio.values)
    plt.xlabel('Date')
    plt.ylabel('Sharpe Ratio')
    title_str = '252 Day Rolling Annualized Sharpe Ratio ' + symbol + ' for Source ' + source
    plt.title(title_str)

    plt.figure(4)
    plt.plot(rolling_return.index,rolling_return.values)
    plt.xlabel('Date')
    plt.ylabel('Annual Return')
    title_str = 'Year on Year (Annual Return) ' + symbol + ' for Source ' + source
    plt.title(title_str)


    plt.figure(5)
    plt.plot(rolling_var95.index,rolling_var95.values)
    plt.title('Rolling 95% Value at Risk for ' + symbol)
    plt.ylabel('Percentage Daily Loss')

    plt.show()
