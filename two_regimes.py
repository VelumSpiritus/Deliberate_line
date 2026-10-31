"""Arithmetic behind the paper's two-regime comparison.
The 2% wedge is an explicit rounded paper input; the price fit and
reversion time are computed from the pinned series by forward_sim.py.
This calculation describes compounding and does not estimate price impact.
"""
import math
from forward_sim import monthly_logp, fit_line, ar1

ms, y = monthly_logp()
b, a = fit_line(y)
dev = [value-(a+b*i) for i,value in enumerate(y)]
phi = ar1(dev)
years = (len(y)-1)/12
wedge = 0.02
print(f"Pinned history: {ms[0]} to {ms[-1]}; {years:.2f} years")
print(f"Fitted nominal price CAGR: {math.expm1(12*b)*100:.2f}%")
print(f"Reversion half-life: {math.log(0.5)/math.log(phi)/12:.2f} years")
print(f"Current price fraction above the fitted line: {1-math.exp(-dev[-1]):.3f}")
print(f"Rounded annual wedge input: {wedge*100:.1f}%")
print(f"Compounded wedge: (1+{wedge})^{years:.2f} = {(1+wedge)**years:.2f}x")
print("The paper's contrasting effects of scale are its interpretation; no price-impact model is fitted here.")
