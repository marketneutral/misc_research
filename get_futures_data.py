import quandl
import pandas as pd
import trading_calendars
from six import iteritems

items = {
    'CHRIS/CME_US1': 'US1.csv',
    'CHRIS/CME_TY1': 'TY1.csv',
    'CHRIS/CME_FV1': 'FV1.csv',
    'CHRIS/CME_TU1': 'TU1.csv'
}    

for k,v in items.iteritems():
    mydata = quandl.get(k)
    mydata.rename(columns={'Last':'Close'}, inplace=True)
    mydata.columns = map(str, mydata.columns)
    mydata.columns = map(str.lower, mydata.columns)
    mydata = mydata[['open', 'high', 'low', 'close', 'volume']]
    mydata = mydata['1991':]

    cal = trading_calendars.get_calendar('NYSE')
    dates = cal.sessions_in_range('1991', '2017').tz_localize(None)
    dates_df = pd.DataFrame(index=dates)
    dates_df = dates_df.join(mydata)

    dates_df.to_csv('./futures/daily/'+v)


# Change benchmark.py to this to kill it
import pandas as pd
from trading_calendars import get_calendar

def get_benchmark_returns(symbol, first_date, last_date):
    cal = get_calendar('NYSE')
    dates = cal.sessions_in_range(first_date, last_date)
    data = pd.DataFrame(index=dates, columns=['Close'])
    return data.sort_index().pct_change(1).iloc[0:]
