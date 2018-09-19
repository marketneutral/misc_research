#from macrostrats.zipline_etc.utils import NoSlippage

from zipline.api import (
    date_rules,
    order_target_percent,
    set_slippage,
    schedule_function,
    symbol,
    time_rules
)

def initialize(context):
#    set_slippage(NoSlippage())
    schedule_function(
        func=rebalance,
        date_rule=date_rules.month_end(),
        time_rule=time_rules.market_close(minutes=15)
    )

def rebalance(context, data):
    order_target_percent(symbol('XYZ'), -1.0)
