from alphatools.algo.utils import log
from alphatools.algo.risk import calc_portfolio_risk, value_at_risk

from zipline.api import (
    commission,
    date_rules,
    get_datetime,
    order_target_percent,
    record,
    schedule_function,
    set_commission,
    set_slippage,
    slippage,
    symbol,
    time_rules
)


def initialize(context):
    # This code runs once, when the sim starts up
    log.debug('scheduling rebalance and recording')

    set_slippage(slippage.FixedSlippage(spread=0.0))
    set_commission(commission.PerShare(cost=0, min_trade_cost=0))
     
    schedule_function(
        func=rebalance,
        date_rule=date_rules.month_end(),
        time_rule=time_rules.market_close(minutes=15)
    )

    schedule_function(
        func=record_daily,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_close()
    )
    

def before_trading_start(context, data):
    # This code runs before each daily trading session
    pass


def rebalance(context, data):
    log.debug(data.current(symbol('US1'), fields='price'))
    
    order_target_percent(symbol('US1'), -1.0)


def record_daily(context, data):
    risk = calc_portfolio_risk(
        context,
        data,
        value_at_risk,
        hist_days=252,
        alpha=0.95
    )
    risk99 = calc_portfolio_risk(
        context,
        data,
        value_at_risk,
        hist_days=252,
        alpha=0.99
    )
    record(daily_95_1d_var = risk)
    record(daily_99_1d_var = risk99)
