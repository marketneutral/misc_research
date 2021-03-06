import datetime
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from trading_calendars import get_calendar

from zipline.assets.futures import CME_CODE_TO_MONTH
from zipline.data.bundles import core as bundles

def csvdir_futures():
    return CSVDIRFutures.ingest


class CSVDIRFutures:
    """
    Wrapper class to call csvdir_bundle with provided
    list of time frames and a path to the csvdir directory
    """

    def __init__(self):
        pass

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
                       output_dir)



def third_friday(year, month):
    """Return datetime.date for monthly option expiration given year and
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
    mask = big_df.symbol.str.len() == 5  # e.g., ESU18; doesn't work prior to year 2000
    return big_df.loc[mask]


def gen_asset_metadata(data, show_progress, exchange='EXCH'):
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
    data['root_symbol'] = data.symbol.str.slice(0,2)

    data['exp_month_letter'] = data.symbol.str.slice(2,3)
    data['exp_month'] = data['exp_month_letter'].map(CME_CODE_TO_MONTH)
    data['exp_year'] = 2000 + data.symbol.str.slice(3,5).astype('int')
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
                   output_dir):

    raw_data = load_data('/Users/jonathan/devwork/pricing_data/CME_2018')
    asset_metadata = gen_asset_metadata(asset_data, False)

    asset_db_writer.write(asset_metadata)

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
