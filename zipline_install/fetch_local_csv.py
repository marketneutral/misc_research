from six import iteritems
import pandas as pd
import pytz
from zipline.sources.requests_csv import PandasCSV


class PandasFileCSV(PandasCSV):

    def __init__(self,
                 url,
                 pre_func,
                 post_func,
                 asset_finder,
                 trading_day,
                 start_date,
                 end_date,
                 date_column,
                 date_format,
                 timezone,
                 symbol,
                 mask,
                 symbol_column,
                 data_frequency,
                 special_params_checker=None,
                 **kwargs):

        remaining_kwargs = {
            k: v for k, v in iteritems(kwargs)
            if k not in self.requests_kwargs
        }

        self.namestring = type(self).__name__
        self.url = url

        super(PandasFileCSV, self).__init__(
            pre_func,
            post_func,
            asset_finder,
            trading_day,
            start_date,
            end_date,
            date_column,
            date_format,
            timezone,
            symbol,
            mask,
            symbol_column,
            data_frequency,
            **remaining_kwargs
        )

        self.df = self.load_df()

    def fetch_data(self):
        try:
            frames = pd.read_csv(self.url, **self.pandas_kwargs)
        except pd.parser.CParserError:
            # could not parse the data, raise exception
            raise Exception('Error parsing remote CSV data.')
        return frames


def fetch_local_csv(
        context,
        url,
        pre_func=None,
        post_func=None,
        date_column='date',
        date_format=None,
        timezone=pytz.utc.zone,
        symbol=None,
        mask=True,
        symbol_column=None,
        special_params_checker=None,
        **kwargs):
    """
    The built-in Zipline fetch_csv function relies on the Python requests
    package, which does not handle local files. This function, when called
    within the initialize block of a strategy will load a **local** csv 
    file and allow the strategy to natively interact with the data via, e.g.,
    data.current(...)
    """

    csv_data_source = PandasFileCSV(
        url,
        pre_func,
        post_func,
        context.asset_finder,
        context.trading_calendar.day,
        context.sim_params.start_session,
        context.sim_params.end_session,
        date_column,
        date_format,
        timezone,
        symbol,
        mask,
        symbol_column,
        data_frequency=context.data_frequency,
        special_params_checker=special_params_checker,
        **kwargs
    )

    # ingest this into dataportal
    context.data_portal.handle_extra_source(
        csv_data_source.df,
        context.sim_params
    )
