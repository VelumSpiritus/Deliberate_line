"""Trend-level variance arithmetic discussed in the public paper.
R-squared measures fit to historical log-price levels. Its complement is
unexplained level variance, not loss probability or an investment risk budget.
"""
import math
from forward_sim import monthly_logp, fit_line

ms,y=monthly_logp()
b,a=fit_line(y)
mean=sum(y)/len(y)
r2=1-sum((v-(a+b*i))**2 for i,v in enumerate(y))/sum((v-mean)**2 for v in y)
print(f"Historical log-price level fit, {ms[0]} to {ms[-1]}: R2={r2:.6f}")
print(f"Unexplained log-level variance fraction: {1-r2:.6f}")
print(f"Residual/total log-level standard deviation: {math.sqrt(1-r2):.6f}")
print("These are historical level-fit statistics. They do not measure drawdown probability,")
print("forecast uncertainty, a hedge's effectiveness, or an investor's probability of loss.")
