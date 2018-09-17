import numpy as np
import pandas as pd
import cvxportfolio as cp

seed = 100

factor_loadings = pd.get_dummies(pd.Series(np.random.randint(0,6,100)))

r_hat_s = pd.Series(np.random.random(100))
r_hat_s.T['USDOLLAR']=0
r_hat = pd.DataFrame(r_hat_s, columns=[pd.Timestamp('2017-01-03')]).T

prices_s = pd.Series(np.random.randint(20, 75, 100))
prices_noUSD = pd.DataFrame(prices_s, columns=[pd.Timestamp('2017-01-03')]).T
prices_s.T['USDOLLAR']=1.0
prices = pd.DataFrame(prices_s, columns=[pd.Timestamp('2017-01-03')]).T


spo_policy = cp.SinglePeriodOpt(
    return_forecast=r_hat,
    costs=[],
    constraints=[
        cp.LeverageLimit(1),
        cp.constraints.DollarNeutral(),
        cp.constraints.MaxWeights(0.10),
        cp.constraints.MinWeights(-0.10),
        #cp.FactorMaxLimit(factor_loadings, 1.0),
        #cp.FactorMinLimit(factor_loadings, -1.0)        
    ]
)

current_portfolio = pd.Series(index=r_hat.columns, data=0)
current_portfolio.USDOLLAR=10000
#import pdb; pdb.set_trace()
shares_to_trade = spo_policy.get_rounded_trades(
    current_portfolio,
    prices,
    t=pd.Timestamp('2017-01-04')
)
