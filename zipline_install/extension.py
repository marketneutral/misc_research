from logbook import Logger, StreamHandler
import pandas as pd
import sys
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities


handler = StreamHandler(sys.stdout, format_string=" | {record.message}")
logger = Logger(__name__)
logger.handlers.append(handler)

#------------

import datetime
import os
import numpy as np
import pandas as pd
from six import iteritems
from tqdm import tqdm
from trading_calendars import get_calendar

from zipline.assets.futures import CME_CODE_TO_MONTH
from zipline.data.bundles import core as bundles

def csvdir_futures(tframes=None, csvdir=None, quandl=False):
    return CSVDIRFutures(tframes, csvdir, quandl).ingest


class CSVDIRFutures:

    def __init__(self, tframes=None, csvdir=None, quandl=False):
        self.tframes = tframes
        self.csvdir = csvdir
        self.quandl = quandl

    def ingest(self,
               environ,
               asset_db_writer,
               minute_bar_writer,
               daily_bar_writer,
               adjustment_writer,
               calendar,
               start_session,
               end_session,
               cache,
               show_progress,
               output_dir):

        futures_bundle(environ,
                       asset_db_writer,
                       minute_bar_writer,
                       daily_bar_writer,
                       adjustment_writer,
                       calendar,
                       start_session,
                       end_session,
                       cache,
                       show_progress,
                       output_dir,
                       self.tframes,
                       self.csvdir,
                       self.quandl)


def third_friday(year, month):
    """Return datetime.date for monthly 3rd Friday expiration given year and
    month
    """
    # The 15th is the lowest third day in the month
    third = datetime.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))
    return third


def load_data(parent_dir):
    """Given a parent_dir of cross-sectional daily files,
       read in all the days and return a big dataframe.
    """
    
    #list the files
    filelist = os.listdir(parent_dir) 
    #read them into pandas
    df_list = [
        pd.read_csv(os.path.join(parent_dir, file), parse_dates=[1])
        for file
        in tqdm(filelist)
    ]
    #concatenate them together
    big_df = pd.concat(df_list)
    big_df.columns = map(str.lower, big_df.columns)
    big_df.symbol = big_df.symbol.astype('str')
    mask = big_df.symbol.str.len() == 5  # e.g., ESU18; doesn't work prior to year 2000; TODO: fix this! doesn't work for 1 or 3 letter root 
    return big_df.loc[mask]

def load_quandl_cme(quandl_file):
    big_df = pd.read_csv(
        quandl_file,
        names=['symbol', 'date', 'open', 'high', 'low', 'close',
               'change', 'settle', 'volume', 'prev_day_open_int'],
        parse_dates=[1]
    )

    big_df.symbol = big_df.symbol.astype('str').str.strip()
    mask1 = ~big_df.symbol.str.contains('_')
    mask2 = (big_df.symbol.str.len() <=8) # ZM2018, ESU2018, CPOF2018
    mask3 = (big_df.date > pd.Timestamp('2018-01-01'))
    return big_df[mask1 & mask2 & mask3]
    


def gen_asset_metadata(data, show_progress, quandl=False, exchange='EXCH'):
    if show_progress:
        log.info('Generating asset metadata.')

    data = data.groupby(
        by='symbol'
    ).agg(
        {'date': [np.min, np.max]}
    )
    data.reset_index(inplace=True)
    data['start_date'] = data.date.amin
    data['end_date'] = data.date.amax
    del data['date']
    data.columns = data.columns.get_level_values(0)

    data['exchange'] = exchange

    def quandl_symbol_split(symbol):
        l = len(symbol)
        year = int(symbol[l-4:l+1])
        month_letter = symbol[l-5:l-4]
        root_symbol = symbol[:l-5]
        return root_symbol, month_letter, year

    if quandl:
        data['root_symbol'] = ''
        data['exp_month_letter'] = ''
        data['exp_year'] = np.nan

        #data['root_symbol'], data['exp_month_letter'], data['exp_year'] = \
        #    data.apply(lambda x: quandl_symbol_split(x.symbol), axis=1)
        for index, row in data.iterrows():
            a, b, c = quandl_symbol_split(row.symbol)
            #print(
            #    str(index) + ": " + str(a) + ":" + str(b) + ":" + str(c)
            #)
            data.iloc[index]['root_symbol'], data.iloc[index]['exp_month_letter'], data.ilocc[index]['exp_year'] = a,b,c
        
    else:
        data['root_symbol'] = data.symbol.str.slice(0,2)
        data['exp_month_letter'] = data.symbol.str.slice(2,3)
        data['exp_year'] = 2000 + data.symbol.str.slice(3,5).astype('int')

    data['exp_month'] = data['exp_month_letter'].map(CME_CODE_TO_MONTH)
    data['expiration_date'] = data.apply(lambda x: third_friday(x.exp_year, x.exp_month), axis=1)

    del data['exp_month_letter']
    del data['exp_month']
    del data['exp_year']
    
    data['auto_close_date'] = data['end_date'].values + pd.Timedelta(days=1)
    data['notice_date'] = data['auto_close_date']

    data['tick_size'] = 0.0001   # Placeholder for now
    data['multiplier'] = 1       # Placeholder for now
    
    return data

def parse_pricing_and_vol(data,
                          sessions,
                          symbol_map):
    for asset_id, symbol in iteritems(symbol_map):
        asset_data = data.xs(
            symbol,
            level=1
        ).reindex(
            sessions.tz_localize(None)
        ).fillna(0.0)
        yield asset_id, asset_data


@bundles.register('futures')
def futures_bundle(environ,
                   asset_db_writer,
                   minute_bar_writer,
                   daily_bar_writer,
                   adjustment_writer,
                   calendar,
                   start_session,
                   end_session,
                   cache,
                   show_progress,
                   output_dir,
                   tframes=None,
                   csvdir=None,
                   quandl=None):

    if not csvdir:
        csvdir = environ.get('CSVDIR')
        if not csvdir:
            raise ValueError("CSVDIR environment variable is not set")

    if not tframes:
        tframes = set(["daily", "minute"]).intersection(os.listdir(csvdir))

        if not tframes:
            raise ValueError("'daily' and 'minute' directories "
                             "not found in '%s'" % csvdir)
    

    #raw_data = load_data('/Users/jonathan/devwork/pricing_data/CME_2018')
    if quandl:
        raw_data = load_quandl_cme(csvdir)
    else:
        raw_data = load_data(csvdir)

    import pdb; pdb.set_trace()
    asset_metadata = gen_asset_metadata(raw_data, False, True)
    root_symbols = asset_metadata.root_symbol.unique()
    root_symbols = pd.DataFrame(root_symbols, columns = ['root_symbol'])
    root_symbols['root_symbol_id'] = root_symbols.index.values

    # TODO: the root_symbols must have exchage
    exch = asset_metadata.groupby('root_symbol')['exchange'].last(),
    root_symbols['exchange'] = 'EXCH'  # hack
    
    asset_db_writer.write(futures=asset_metadata, root_symbols=root_symbols)

    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)
    raw_data.set_index(['date', 'symbol'], inplace=True)
    daily_bar_writer.write(
        parse_pricing_and_vol(
            raw_data,
            sessions,
            symbol_map
        ),
        show_progress=show_progress
    )







#-----------

register(
    'futures',
    csvdir_futures(
        'daily',
        '/Users/jonathan/devwork/misc_research/zipline_install/CME_20180920.csv',
        True
    ),
    calendar_name='CME',
)


#register(
#    'futures',
#    csvdir_futures(
#        'daily',
#        '/Users/jonathan/devwork/pricing_data/CME_2018'
#    ),
#    calendar_name='CME',
#)


start_session = pd.Timestamp('1991-01-02', tz='utc')
end_session = pd.Timestamp('2017-12-29', tz='utc')

#start_session = pd.Timestamp('2014-01-28', tz='utc')
#end_session = pd.Timestamp('2014-02-07', tz='utc')

register(
#    'csvdir',
    'treasury-futures',
    csvdir_equities(
        ["daily"],
        '/Users/jonathan/devwork/misc_research/futures'
    ),
    start_session=start_session,
    end_session=end_session
)
