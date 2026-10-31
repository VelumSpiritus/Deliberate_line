# -*- coding: utf-8 -*-
"""The STRING of correlates, not the one bead.

The deliberate line is the 0 ratio (log-linear fit).  The deviation from it is the live ratio.
The correlate is corr(deviation, forward return).  The -0.47 was ONE horizon on ONE split.
Here is the whole string: every horizon, walk-forward, each bead placed in its own-motion null
(the walk's actual increments moving-block-resampled -- never an imported Gaussian).  Then the
same string represented on its two faces: forward RETURNS (below the line) and LOSSES (above)."""
from __future__ import annotations
import math, statistics as st, sys, random
import data as D

HS = [1,3,6,12,24,36,60,84,120]   # months: 1mo ... 10yr
TMIN = 120
DRAWS = 1000
BLOCK = 12
rng = random.Random(7)

def monthly_logp():
    by={}
    for d,c in D.closes_dated("^GSPC"):
        if c>0: by[d[:7]]=math.log(c)
    ms=sorted(by); return ms,[by[m] for m in ms]

def corr(a,b):
    if len(a)<3: return float('nan')
    am,bm=st.mean(a),st.mean(b)
    cov=sum((a[i]-am)*(b[i]-bm) for i in range(len(a)))
    d=math.sqrt(sum((x-am)**2 for x in a)*sum((y_-bm)**2 for y_ in b))
    return cov/d if d else 0.0

def ols(x,y):
    xm,ym=st.mean(x),st.mean(y); sxx=sum((xi-xm)**2 for xi in x) or 1e-12
    return sum((x[i]-xm)*(y[i]-ym) for i in range(len(x)))/sxx

def full_fit(y):
    n=len(y); xm,ym=(n-1)/2,st.mean(y)
    b=sum((i-xm)*(y[i]-ym) for i in range(n))/(sum((i-xm)**2 for i in range(n)) or 1)
    a=ym-b*xm
    ss=sum((y[i]-(a+b*i))**2 for i in range(n)); tot=sum((v-ym)**2 for v in y)
    return a,b,1-ss/tot

def wf_dev(y):
    N=Sx=Sxx=Sy=Sxy=0.0; out={}
    for t in range(len(y)):
        N+=1; Sx+=t; Sxx+=t*t; Sy+=y[t]; Sxy+=t*y[t]
        if t>=TMIN:
            den=N*Sxx-Sx*Sx
            b=(N*Sxy-Sx*Sy)/den if den else 0.0; a=(Sy-b*Sx)/N
            out[t]=y[t]-(a+b*t)
    return out

def block_path(y,diffs):
    """surrogate path: moving-block resample of the ACTUAL increments (walk's own motion)."""
    n=len(y); need=n-1; s=[y[0]]; k=len(diffs)
    while len(s)-1<need:
        start=rng.randrange(0,k)
        for j in range(BLOCK):
            if len(s)-1>=need: break
            s.append(s[-1]+diffs[(start+j)%k])
    return s

ms,y=monthly_logp(); n=len(y)
a,b,r2=full_fit(y)
dev=wf_dev(y)
diffs=[y[i+1]-y[i] for i in range(n-1)]

print(f"\n  THE 0 RATIO (deliberate line, full sample {ms[0]}..{ms[-1]}, n={n})")
print(f"    slope {(math.exp(b*12)-1)*100:.2f}%/yr   R2={r2:.3f}\n")

# null string: each surrogate gives its own correlate at each horizon
null_by_H={H:[] for H in HS}
for _ in range(DRAWS):
    s=block_path(y,diffs); pdv=wf_dev(s)
    for H in HS:
        ts=[t for t in pdv if t<=n-1-H]
        rr=corr([pdv[t] for t in ts],[s[t+H]-s[t] for t in ts])
        if rr==rr: null_by_H[H].append(rr)

def hlab(H):
    return f"{H}mo" if H<12 else f"{H//12}yr"

print("  THE STRING OF CORRELATES  (walk-forward corr(deviation, forward return), each in own-motion null)\n")
print(f"    {'horizon':>8} {'n':>5} {'correlate':>10} {'retention':>10} {'null mean':>10} {'null 2.5%':>10} {'null 97.5%':>11} {'place':>26}")
string=[]
for H in HS:
    ts=[t for t in dev if t<=n-1-H]
    d0=[dev[t] for t in ts]; fwd=[y[t+H]-y[t] for t in ts]
    r=corr(d0,fwd)
    ts2=[t for t in ts if (t+H) in dev]
    R=ols([dev[t] for t in ts2],[dev[t+H] for t in ts2]) if len(ts2)>5 else float('nan')
    nb=sorted(null_by_H[H]); lo=nb[int(0.025*len(nb))]; hi=nb[int(0.975*len(nb))]; nm=st.mean(nb)
    place=("OUTSIDE (below 2.5%)" if r<lo else "OUTSIDE (above 97.5%)" if r>hi else "inside own-motion band")
    string.append((H,r))
    print(f"    {hlab(H):>8} {len(d0):>5} {r:>+10.3f} {R:>+10.3f} {nm:>+10.3f} {lo:>+10.3f} {hi:>+11.3f} {place:>26}")

print("\n  THE SAME STRING ON ITS TWO FACES  (12-mo forward, by deviation decile)")
print("    below the line -> the RETURNS ; above the line -> the LOSSES\n")
H=12
ts=[t for t in dev if t<=n-1-H]
rows=sorted(((dev[t], y[t+H]-y[t]) for t in ts))
m=len(rows);
print(f"    {'decile':>7} {'dev range (log)':>22} {'mean dev':>9} {'fwd 12mo ret':>13} {'annualized':>11}  face")
for q in range(10):
    lo_i=q*m//10; hi_i=(q+1)*m//10
    chunk=rows[lo_i:hi_i]
    dv=[c[0] for c in chunk]; fr=[c[1] for c in chunk]
    mdv=st.mean(dv); mfr=st.mean(fr); ann=math.exp(mfr)-1
    face="LOSS (above line)" if mdv>0 else "return (below line)"
    print(f"    {q+1:>7} {min(dv)*100:>+9.1f}%..{max(dv)*100:>+6.1f}% {mdv*100:>+8.1f}% {mfr*100:>+12.1f}% {ann*100:>+10.1f}%  {face}")

nowdev=y[-1]-(a+b*(n-1))
print(f"\n  NOW ({ms[-1]}): price vs line = {nowdev*100:+.1f}%  ({'above -> loss-side' if nowdev>0 else 'below -> return-side'})")
print("  string summary:", ", ".join(f"{hlab(H)} {r:+.2f}" for H,r in string))
