"""Full-sample AR(1) gap-closing arithmetic used by the paper.
This is a fitted historical projection; publication-driven price impact
is an interpretation for which this script has no measured diffusion model.
"""
from __future__ import annotations
import math, statistics as st, sys
import data as D

def monthly_logp():
    by={}
    for d,c in D.closes_dated("^GSPC"):
        if c>0: by[d[:7]]=math.log(c)
    ms=sorted(by); return ms,[by[m] for m in ms]

def full_fit(y):
    n=len(y); xm,ym=(n-1)/2,st.mean(y)
    b=sum((i-xm)*(y[i]-ym) for i in range(n))/(sum((i-xm)**2 for i in range(n)) or 1)
    a=ym-b*xm
    ss=sum((y[i]-(a+b*i))**2 for i in range(n)); tot=sum((v-ym)**2 for v in y)
    return a,b,1-ss/tot

def ar1(x):
    "phi in x[t+1] = phi*x[t] (through origin, since deviation mean ~0)"
    num=sum(x[i]*x[i+1] for i in range(len(x)-1)); den=sum(x[i]*x[i] for i in range(len(x)-1))
    return num/den if den else float('nan')

ms,y=monthly_logp(); n=len(y)
a,b,r2=full_fit(y)
dev=[y[t]-(a+b*t) for t in range(n)]           # full-sample (in-sample) deviation
phi=ar1(dev)                                    # monthly reversion retention
hl=math.log(0.5)/math.log(phi)                  # half-life in months
d0=dev[-1]                                       # current deviation (log)
yr=lambda m: m/12.0


print(f"Pinned monthly history: {ms[0]} to {ms[-1]}")
print(f"Nominal price CAGR {math.expm1(b*12)*100:.2f}%/year; R2={r2:.6f}")
print(f"Monthly AR(1) retention {phi:.6f}; half-life {hl/12:.2f} years")
t90=math.log(.1)/math.log(phi)
print(f"90% gap-close time {t90/12:.2f} years")
print(f"Current deviation {d0*100:.2f}% log; price premium {math.expm1(d0)*100:.2f}%")
for months in (12,24,36,60,120):
    projected=d0*phi**months
    closed=d0-projected
    print(f"{months} months: remaining deviation {projected*100:.2f}% log; gap closed {closed*100:.2f}% log")
print(f"Price fraction above the line: {(1-math.exp(-d0))*100:.2f}%")
