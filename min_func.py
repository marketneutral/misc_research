from scipy.optimize import minimize


def fun(x):
    return 4*x**4 - 8*x**3 + 6*x*x - 12


bnds = (-3, 3)
res = minimize(fun, -10, bounds=[bnds])
