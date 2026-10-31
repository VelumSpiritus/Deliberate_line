# -*- coding: utf-8 -*-
"""labor_cost — the hinge of the chain: harsher extraction against labor = labor share DOWN.

The paper links: force -> stronger border -> harsher extraction against labor cost -> death -> more
extraction. The death link is the cited embodiment canon (Case & Deaton tie deaths of despair to
labor-market extraction directly). This measures the LABOR link: does the extraction state move
INVERSELY with labor's share of output, and does labor share break at the 1979 hinge?
  extraction state : deviation d(t) = log(S&P) - (a+b t), annual  AND  WID US top-1% share
  labor share      : FRED nonfarm business labor share (index), annual
Prediction: labor share DOWN as extraction UP -> STRONG NEGATIVE correlation; break ~1979.
Moving-block resampling uses labor-share increments. Reads pinned inputs only.
"""
from __future__ import annotations
import math, statistics
import numpy as np
import data, ensemble, csv, io

def sp_annual():
    by={}
    for ds,c in data.closes_dated("^GSPC"): by[int(ds[:4])]=c
    return by

def fred_annual(sid):
    by={}
    for ds,v in data.fred(sid): by[int(ds[:4])]=v
    return by

def us_top1():
    raw=ensemble._load()
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8","replace"))))
    col=[c for c in rows[0].keys() if "Share" in c][0]
    by={}
    for r in rows:
        if r.get("Entity")=="United States":
            try: by[int(r["Year"])]=float(r[col])
            except: pass
    return by

def pearson(x,y):
    return float(np.corrcoef(np.asarray(x,float),np.asarray(y,float))[0,1])

def block_null(x,y,block=4,draws=2000,seed=7):
    rng=np.random.default_rng(seed); dy=np.diff(y); n=len(dy); cs=[]
    for _ in range(draws):
        idx=[]
        while len(idx)<n:
            s=rng.integers(0,n); idx.extend(range(s,min(s+block,n)))
        idx=idx[:n]; ys=np.concatenate([[y[0]],y[0]+np.cumsum(dy[idx])]); cs.append(pearson(x,ys))
    cs=np.array(cs); return float(cs.mean()),float(np.percentile(cs,2.5)),float(np.percentile(cs,97.5))

def main():
    sp=sp_annual()
    lab=None; lid=None
    for cid in ("PRS85006173","W270RE1A156NBEA","LABSHPUSA156NRUG"):
        try:
            d=fred_annual(cid)
            if len(d)>25: lab=d; lid=cid; break
        except Exception: pass
    if lab is None: print("NO_LABOR_SERIES"); return
    top1=us_top1()

    yrs=sorted(y for y in sp if 1970<=y<=2026 and y in lab)
    logp=np.array([math.log(sp[y]) for y in yrs]); t=np.array(yrs,float)
    A=np.vstack([np.ones_like(t),t]).T; (a,b),*_=np.linalg.lstsq(A,logp,rcond=None)
    d_state=logp-(a+b*t)
    labv=np.array([lab[y] for y in yrs])
    print(f"labor series {lid}: {labv.min():.1f}..{labv.max():.1f}  n={len(yrs)}  ({yrs[0]}-{yrs[-1]})")

    r1=pearson(d_state,labv); m,lo,hi=block_null(d_state,labv)
    print(f"\ndeviation d  vs  labor share:   r={r1:+.3f}   null[{lo:+.3f},{hi:+.3f}]   {'OUTSIDE (real)' if not(lo<=r1<=hi) else 'inside'}")

    yT=sorted(y for y in top1 if 1970<=y<=2024 and y in lab)
    if len(yT)>15:
        r2=pearson([top1[y] for y in yT],[lab[y] for y in yT])
        m2,lo2,hi2=block_null(np.array([top1[y] for y in yT]),np.array([lab[y] for y in yT]))
        print(f"top-1% share vs labor share:    r={r2:+.3f}   null[{lo2:+.3f},{hi2:+.3f}]   {'OUTSIDE (real)' if not(lo2<=r2<=hi2) else 'inside'}   (n={len(yT)})")

    # break at 1979: mean labor share pre/post, and slope change
    pre=[lab[y] for y in yrs if y<1979]; post=[lab[y] for y in yrs if y>=1979]
    print(f"\nlabor-share index: pre-1979 mean {statistics.mean(pre):.1f}  post-1979 mean {statistics.mean(post):.1f}  drop {statistics.mean(pre)-statistics.mean(post):+.1f} index points")
    # peak year
    pk=max(yrs,key=lambda y:lab[y]); print(f"labor-share peak year: {pk} ({lab[pk]:.1f}); latest {yrs[-1]} ({lab[yrs[-1]]:.1f})")
    print("\nREAD: chain predicts STRONG NEGATIVE (labor share down as extraction up) + a post-1979 drop.")
    print("Death link = cited canon (Case & Deaton: deaths of despair <- labor-market extraction). No new run.")

if __name__=="__main__":
    main()
