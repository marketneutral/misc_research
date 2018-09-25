from zipline.api import symbol, order_target, order_target_percent, order_target_value, record, future_symbol, continuous_future, get_datetime

from logbook import Logger, StderrHandler, DEBUG, INFO

log_handler = StderrHandler(
    format_string='[{record.time:%Y-%m-%d %H:%M:%S.%f}]: ' +
    '{record.level_name}: {record.func_name}: {record.message}',
    level=INFO
)
log_handler.push_application()
log = Logger('Algorithm')


def initialize(context):
    context.my_cf = continuous_future('CL')
        
def handle_data(context, data):
    contract = data.current(context.my_cf, 'contract')
    log.info(contract)
    log.info(get_datetime)
    x = data.current(contract, 'price')
    log.info(x)
   # order_target(contract, 10)
    #order_target_value(contract, 100000)
    order_target_percent(contract, 1.0)
