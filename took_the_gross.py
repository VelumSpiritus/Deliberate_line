"""Reproduce the paper's retrospective January-2024 price-gain example.
The fitted line ends in December 2023; the investment window is selected
in hindsight. Leveraged figures are simple gearing arithmetic excluding
financing, fees, liquidation and option pricing. The 6.2% economy-growth
input is the paper's rounded decomposition input, not fitted here.
"""
from __future__ import annotations
import math, statistics as st, sys
import data as D

START="2024-01"
def monthly():
    by={}
    for d,c in D.closes_dated("^GSPC"):
        if c>0: by[d[:7]]=c
    ms=sorted(by); return ms,[by[m] for m in ms]
ms,px=monthly(); n=len(ms)
logp=[math.log(p) for p in px]

def wf_fit_through(idx):
    "OLS line on logp[0..idx] inclusive; return (a,b)"
    N=idx+1; xs=range(N)
    xm=st.mean(xs); ym=st.mean(logp[:N])
    b=sum((i-xm)*(logp[i]-ym) for i in xs)/(sum((i-xm)**2 for i in xs) or 1)
    return ym-b*xm, b

i0=ms.index(START); iN=n-1
a23,b23=wf_fit_through(i0-1)                      # fit through Dec-2023 only (no hindsight)
dev24=logp[i0]-(a23+b23*i0)
p0,pN=px[i0],px[iN]
ret=pN/p0-1.0
yrs=(iN-i0)/12.0
econ=0.062                                        # economy-tracking part of the slope [two_regimes.py]
line_slope=math.exp(b23*12)-1


print(f"Historical window: {START} to {ms[iN]} ({yrs:.2f} years)")
print(f"Starting/ending monthly close: {p0:.2f}/{pN:.2f}; change {ret*100:.2f}%")
print(f"Fit through December 2023: slope {line_slope*100:.2f}%/year; start deviation {dev24*100:.2f}% log")
print("Arithmetic on $10,000; leverage is an explicit scenario input:")
for lev in (1,2,5):
    end=10000*(1+lev*ret)
    print(f"  {lev}x: ending equity ${end:.0f}, gain ${end-10000:.0f}")
econ_move=math.expm1(econ*yrs)
taken_frac=max(0.0,ret-econ_move)/ret if ret>0 else 0.0
print(f"Economy-growth assumption: {econ*100:.1f}% continuous/year; window growth {econ_move*100:.2f}%")
print(f"Share of realized gain above that assumed growth: {taken_frac*100:.1f}%")
print("The 5x scenario is not an option valuation; realized trade outcomes depend on path and costs.")
