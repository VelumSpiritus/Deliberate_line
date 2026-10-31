# -*- coding: utf-8 -*-
"""party_invariance - the line holds invariant to party and person (section 5), tested straight.

The claim is NOT "returns are the same under each party" - there is a known cyclical gap (Blinder &
Watson 2016: S&P real returns higher under Democratic presidents). The claim is STRUCTURAL: the
deliberate line's SLOPE - the ~8.2%/yr extraction trend - does not depend on who holds the seat. Test:
    log(price) = a + b*t + c*R + d*(R*t)
where R=1 in years a Republican holds the presidency. If d (the slope-difference term) is
indistinguishable from 0, the structural slope is party-invariant - the seat is the prize, not the
person. Also report mean deviation by party, and (kept honest) the cyclical annual-return gap that
does NOT touch the structural slope. Reads only (Yahoo via data.py cache)."""
from __future__ import annotations
import math
import numpy as np
import data

PARTY_R = {}
def _set(lo, hi, r):
    for y in range(lo, hi + 1):
        PARTY_R[y] = r
_set(1970, 1976, 1)   # Nixon/Ford
_set(1977, 1980, 0)   # Carter
_set(1981, 1992, 1)   # Reagan / GHW Bush
_set(1993, 2000, 0)   # Clinton
_set(2001, 2008, 1)   # GW Bush
_set(2009, 2016, 0)   # Obama
_set(2017, 2020, 1)   # Trump I
_set(2021, 2024, 0)   # Biden
_set(2025, 2026, 1)   # Trump II

def sp_annual():
    by = {}
    for ds, c in data.closes_dated("^GSPC"):
        by[int(ds[:4])] = c
    return by

def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    s2 = (resid @ resid) / (n - k)
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    return beta, se, resid

def main():
    sp = sp_annual()
    yrs = sorted(y for y in sp if 1970 <= y <= 2026 and y in PARTY_R)
    t = np.array(yrs, float); t = t - t.mean()
    logp = np.array([math.log(sp[y]) for y in yrs])
    R = np.array([PARTY_R[y] for y in yrs], float)

    b_full = np.polyfit(t, logp, 1)[0]
    print("full-sample slope b = %.2f%%/yr   n=%d  (%d-%d)" % (b_full*100, len(yrs), yrs[0], yrs[-1]))

    X = np.column_stack([np.ones_like(t), t, R, R * t])
    beta, se, resid = ols(X, logp)
    names = ["a", "b (slope)", "c (R level)", "d (R x t = slope diff)"]
    print("\ninteraction model  log(price) = a + b t + c R + d (R t):")
    for nm, bv, sv in zip(names, beta, se):
        tstat = bv / sv if sv else float('nan')
        tag = ""
        if nm.startswith("d"):
            tag = "  <-- indistinguishable from 0" if abs(tstat) < 2 else "  (|t|>=2: a real slope gap)"
        print("  %-24s %+.4f  (se %.4f, t %+.2f)%s" % (nm, bv, sv, tstat, tag))
    print("\n  => slope under D = %.2f%%/yr ; under R = %.2f%%/yr ; difference %+.2f pts/yr"
          % (beta[1]*100, (beta[1]+beta[3])*100, beta[3]*100))

    a0 = np.polyfit(t, logp, 1)[1]; b0 = np.polyfit(t, logp, 1)[0]
    dev = logp - (a0 + b0 * t)
    print("\n  mean deviation d:  D-years %+.3f   R-years %+.3f" % (dev[R==0].mean(), dev[R==1].mean()))

    rets = np.diff(logp); ry = np.array(yrs[1:]); rr = np.array([PARTY_R[y] for y in ry])
    print("\n  (kept honest) mean annual log-return:  D %+.1f%%/yr   R %+.1f%%/yr"
          % (rets[rr==0].mean()*100, rets[rr==1].mean()*100))
    print("  -- a cyclical gap (Blinder & Watson 2016) in RETURNS, not the structural slope.")
    print("\nREAD: if d (R x t) is indistinguishable from 0, the ~8%/yr slope does not depend on party")
    print("- the seat is the prize, not the person (section 5). BOUNDS: year-level party coding; the")
    print("1979 break is modeled as one slope; the claim is slope party-invariance, not R^2.")

if __name__ == "__main__":
    main()
