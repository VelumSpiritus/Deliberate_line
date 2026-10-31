# -*- coding: utf-8 -*-
"""war_funds — does the extraction co-move with military spending? (empirical leg, §3c)

Honest operationalization of "war funds the machine":
  - extraction state  : deviation d(t) = log(S&P) - (a + b*t), annual (the line's own residual)
  - excess            : nominal S&P growth - nominal GDP growth (the >=2%/yr skim), annual
  - war proxy         : national-defense spending as a share of nominal GDP, annual (FRED)
Tests (contemporaneous and lead/lag), each against a moving-block bootstrap null built from the
war series' OWN reshuffled increments (same discipline as string_correlates). Sign reported straight:
  "war funds the machine" predicts POSITIVE (more defense -> more extraction);
  Scheidel (mass-mobilization war COMPRESSES inequality) predicts NEGATIVE.
Reads only; fetches FRED/Yahoo to the local data/raw cache; writes nothing else.
"""
from __future__ import annotations
import math, sys
import numpy as np
import data

def annual_from_dated(pairs):
    """[(YYYY-MM-DD, value)] -> {year: last observation that year}."""
    by = {}
    for ds, v in pairs:
        y = int(ds[:4]); by[y] = v   # last wins -> year-end-ish
    return by

def sp_annual():
    cd = data.closes_dated("^GSPC")
    by = {}
    for ds, c in cd:
        by[int(ds[:4])] = c
    return by

def fred_annual(series_id):
    return annual_from_dated(data.fred(series_id))

def fit_line(years, logp):
    t = np.array(years, float); y = np.array(logp, float)
    A = np.vstack([np.ones_like(t), t]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    a, b = coef
    resid = y - (a + b*t)
    ss = 1 - np.sum(resid**2)/np.sum((y-y.mean())**2)
    return a, b, resid, ss

def pearson(x, y):
    x = np.asarray(x,float); y=np.asarray(y,float)
    return float(np.corrcoef(x,y)[0,1])

def block_boot_null(x, y, block=4, draws=2000, seed=12):
    """Null: reshuffle y's increments in blocks, rebuild, correlate with x. Returns (mean, lo, hi)."""
    rng = np.random.default_rng(seed)
    dy = np.diff(y); n = len(dy)
    cors = []
    for _ in range(draws):
        idx = []
        while len(idx) < n:
            s = rng.integers(0, n)
            idx.extend(range(s, min(s+block, n)))
        idx = idx[:n]
        ys = np.concatenate([[y[0]], y[0] + np.cumsum(dy[idx])])
        cors.append(pearson(x, ys))
    cors = np.array(cors)
    return float(cors.mean()), float(np.percentile(cors,2.5)), float(np.percentile(cors,97.5))

def main():
    sp = sp_annual()
    # nominal GDP (annual, $B) and national defense outlay (annual, $B) — candidate ids, first that loads
    gdp = fred_annual("GDPA")                       # nominal GDP, annual
    defense = None; def_id=None
    for cid in ("FDEFX", "A997RC1A027NBEA", "A824RC1A027NBEA"):
        try:
            d = fred_annual(cid)
            if len(d) > 30:
                defense = d; def_id = cid; break
        except Exception as e:
            continue
    if defense is None:
        print("NO_DEFENSE_SERIES"); return
    rgdp = fred_annual("GDPCA")                      # real GDP, annual (for excess)

    years = sorted(y for y in sp if 1970 <= y <= 2026 and y in gdp and y in defense)
    logp = [math.log(sp[y]) for y in years]
    a,b,resid,ss = fit_line(years, logp)
    print(f"line: slope b={b*1:.4f}/yr  R2={ss:.3f}  n={len(years)}  (expect ~0.08, ~0.96)")

    share = np.array([defense[y]/gdp[y] for y in years])   # defense / nominal GDP
    d_state = resid                                         # extraction state
    print(f"defense series: {def_id}   share {share.min()*100:.1f}%..{share.max()*100:.1f}%  (start {years[0]}, end {years[-1]})")

    # excess: nominal S&P growth - nominal GDP growth, year over year
    exc=[]; exy=[]
    for i in range(1,len(years)):
        y0,y1 = years[i-1], years[i]
        if y1-y0!=1: continue
        g_sp = math.log(sp[y1]/sp[y0]); g_gdp = math.log(gdp[y1]/gdp[y0])
        exc.append(g_sp-g_gdp); exy.append(y1)
    exc=np.array(exc)
    share_for_exc = np.array([defense[y]/gdp[y] for y in exy])

    def report(name, x, y, lo=None):
        r = pearson(x,y)
        m,lob,hib = block_boot_null(x, y)
        inside = lob <= r <= hib
        print(f"  {name:38s} r={r:+.3f}   null[{lob:+.3f},{hib:+.3f}] mean {m:+.3f}   {'INSIDE band (not distinguishable)' if inside else 'OUTSIDE band'}")
        return r, inside

    print("\nCONTEMPORANEOUS:")
    report("deviation d  vs  defense share", d_state, share)
    report("excess(SP-GDP) vs defense share", exc, share_for_exc)

    print("\nLEAD/LAG (defense share leads extraction state by k years):")
    for k in (1,2,3,5):
        if len(years)>k:
            report(f"d(t) vs defense share(t-{k})", d_state[k:], share[:-k])

    # war-period dummy: major mobilizations
    war_years = set(range(1970,1976)) | set(range(2001,2012))  # late Vietnam; post-9/11
    inwar = np.array([1.0 if y in war_years else 0.0 for y in years])
    print("\nWAR-PERIOD DUMMY (late Vietnam 1970-75; post-9/11 2001-11):")
    dm = d_state[inwar==1].mean(); dp = d_state[inwar==0].mean()
    print(f"  mean deviation d  in-war {dm:+.3f}   peace {dp:+.3f}   diff {dm-dp:+.3f}")

    print("\nREAD: 'war funds the machine' => POSITIVE; Scheidel (war compresses) => NEGATIVE; inside-band => not an empirical co-movement.")

if __name__=="__main__":
    main()
