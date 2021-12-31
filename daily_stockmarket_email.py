import time
start_time = time.time()

import pandas as pd
import numpy as np
from datetime import timedelta, date
import pandas_datareader.data as web

# import sys
# sys.path.insert(0, '..')
from sendgrid_email import send_email
from sp500_tickers import sp500_ticker_list
tickers = sp500_ticker_list()
# tickers = ['FB', 'AAPL', 'MSFT','GOOG', 'NFLX']

# start date is more than 7 days
# because API only returns trading days
start = date.today() - timedelta(days=11)
end = date.today()
# yesterday = date.today() - timedelta(days=1)
# last_year_day_shift = date.today() - timedelta(days=366)

import logging
logging.basicConfig(level=logging.DEBUG ,datefmt='%d-%b-%y %H:%M:%S' , format='%(filename)s - %(asctime)s - %(levelname)s: [Message] - %(message)s')



class DataAnalysisHelpers:

    def __init__(self, df, shift_days=None,metric_col_name=None, rolling_window=None):
        self.df = df
        self.shift_days = shift_days
        self.metric_col_name = metric_col_name
        self.rolling_window = rolling_window

    def cumulative_return(self):
        target_metric = self.metric_col_name
        output = ( 1 + ((self.df[target_metric] / self.df[target_metric].shift(self.shift_days))-1) ).cumprod()
        return output

    def returns_calculation(self):
        target_metric = self.metric_col_name     
        output = (self.df[target_metric] / self.df[target_metric].shift(self.shift_days))-1
        return output
    
    def moving_average(self):
        target_metric = self.metric_col_name     
        output = self.df[target_metric].rolling(window=self.rolling_window).mean(),
        return output

helpers = DataAnalysisHelpers

output = []
counter = 0

for tick in tickers:
    try: 
        logging.debug(f"Running Process for Ticker: {tick}")
        stock_data = web.DataReader(name=tick, data_source='yahoo', start=start, end=end)
        stock_data = (
            stock_data.assign(
                    Ticker=tick,
                    # movingaverage_10d=stock_data['Open'].rolling(window=10).mean(),
                    Returns_1d=helpers(df=stock_data, shift_days=1, metric_col_name='Close').returns_calculation(),
                    Returns_7d=helpers(df=stock_data, shift_days=7, metric_col_name='Close').returns_calculation(),
                    Cumulative_return=helpers(df=stock_data, shift_days=1, metric_col_name='Close').cumulative_return()
                    )
                    .round(3)
                )

        counter = counter + 1
        logging.debug(f"Loop #: {counter}")
        logging.debug(f"# of Days in Data: {len(stock_data)}")
        execution_time_since_start = (time.time() - start_time)
        execution_time_since_start = str(round(execution_time_since_start, 2))
        logging.debug(f'Execution time since script start: {execution_time_since_start}')
        output.append(stock_data)

    except BaseException as e:
        logging.debug(f"UnidentifiedError: {e}")
        # If error occurs - continue script
        continue

output = pd.concat(output)
data = (output.reset_index()
        .sort_values(by='Returns_1d', ascending=False)
        )

datetime_tranformation = pd.to_datetime(data['Date'].drop_duplicates())
most_recent_date = datetime_tranformation.max().strftime('%Y-%m-%d')

todays_metrics = data.loc[data['Date'].isin([most_recent_date])]

growers = todays_metrics.loc[todays_metrics['Returns_1d'] > 0.04]
growers['Type'] = 'growers'
decliners = todays_metrics.loc[todays_metrics['Returns_1d'] < -0.04]
decliners['Type'] = 'decliners'

frames = [growers, decliners]
result = pd.concat(frames)
result = result.drop(columns=['Volume', 'Adj Close','Cumulative_return'])
result = result[['Date','Type','Ticker','Returns_1d', 'Returns_7d', 'Open', 'Close', 'High', 'Low']]

print(result)

send_email(
dataframe = result,
all_stock_data = data,
subject_line=f'Email Alert - SP500 - Large Stock Swings Today [{end}]',
content= f"""
    Below are the largest changes (growth and declines) from SP500 on <b><u>{end}</b></u>.
    <br><br>
    This includes tickers that either <b><u>grew or declined more than 4% today.
""")

end_time = (time.time() - start_time)
end_time = str(round(end_time, 2))
logging.debug(f'Execution time since script start: {end_time}')






