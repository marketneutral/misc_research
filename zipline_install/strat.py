from zipline.api import symbol, order_target_percent, record, future_symbol, continuous_future, get_datetime

from logbook import Logger, StderrHandler, DEBUG, INFO

log_handler = StderrHandler(
    format_string='[{record.time:%Y-%m-%d %H:%M:%S.%f}]: ' +
    '{record.level_name}: {record.func_name}: {record.message}',
    level=INFO
)
log_handler.push_application()
log = Logger('Algorithm')


def initialize(context):
    #context.my_cf = continuous_future('A6', roll='calendar')
    pass
        
def handle_data(context, data):
    #fut = future_symbol('A6F18')
    #log.info(data.current(fut, 'close'))
    log.info(get_datetime())
