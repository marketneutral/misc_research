from zipline.api import symbol, order_target_percent, record

def handle_data(context, data):
    order_target_percent(symbol('US1'), 1.0)
    record(US1_avg=data.history(symbol('US1'), 'close', 20, '1d').mean())
    record(US1=data.current(symbol('US1'), 'close'))
