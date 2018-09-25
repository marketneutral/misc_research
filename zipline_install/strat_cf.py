from zipline.api import symbol, order_target_percent, record, future_symbol, continuous_future

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
    order_target_percent(contract, 1.0)
    log.info(contract)
