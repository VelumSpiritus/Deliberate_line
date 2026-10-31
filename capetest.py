# -*- coding: utf-8 -*-
"""Does CAPE (PE10, earnings-based — NOT the price's own trend) predict forward real return,
and does it survive a null? Null = block bootstrap of monthly real returns (preserves return
autocorrelation + overlapping structure) with REAL CAPE held fixed, breaking the genuine link."""
from __future__ import annotations
import math, statistics as st, csv, os, random
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ensemble")

def load():
    rows = list(csv.DictReader(open(os.path.join(BASE, "shiller_sp500_monthly.csv"))))
    ds, cape, lrp = [], [], []
    for r in rows:
        try:
            pe = float(r["PE10"]); rp = float(r["Real Price"])
            if pe > 0 and rp > 0:
                ds.append(r["Date"][:7]); cape.append(pe); lrp.append(math.log(rp))
        except (ValueError, KeyError):
            pass
    return ds, cape, lrp

def corr(a, b):
    if len(a) < 3: return float('nan')
    am, bm = st.mean(a), st.mean(b)
    cov = sum((a[i]-am)*(b[i]-bm) for i in range(len(a)))
    d = math.sqrt(sum((x-am)**2 for x in a)*sum((x-bm)**2 for x in b))
    return cov/d if d else 0.0

ds, cape, lrp = load()
n = len(ds)
lcape = [math.log(c) for c in cape]
print(f"\n  CAPE test — Shiller PE10 vs forward REAL return, {ds[0]}..{ds[-1]} (n={n} valid months)\n")
print(f"  {'horizon':>8} {'sample':>10} {'n':>5} {'corr(lnCAPE,fwd)':>17} {'r^2':>6} {'null 5%':>8} {'null 1%':>8} {'%<=real':>8}  verdict")

def run(H, lo, label):
    idx = [t for t in range(lo, n-H)]
    x = [lcape[t] for t in idx]; fwd = [lrp[t+H]-lrp[t] for t in idx]
    r = corr(x, fwd)
    # block bootstrap null on real monthly returns
    g = [lrp[i+1]-lrp[i] for i in range(lo, n-1)]
    L = 60; DRAWS = 1000; rng = random.Random(3); band = []
    for _ in range(DRAWS):
        surr = []
        while len(surr) < len(g):
            s = rng.randrange(0, max(1, len(g)-L))
            surr.extend(g[s:s+L])
        surr = surr[:len(g)]
        # rebuild surrogate log-price path from lo
        path = [lrp[lo]]
        for v in surr: path.append(path[-1]+v)
        # forward returns on surrogate aligned to same idx offset
        m = len(path)
        fs = [path[(t-lo)+H]-path[(t-lo)] for t in idx if (t-lo)+H < m]
        xs = [lcape[t] for t in idx if (t-lo)+H < m]
        rc = corr(xs, fs)
        if rc == rc: band.append(rc)
    band.sort(); p5 = band[int(0.05*len(band))]; p1 = band[int(0.01*len(band))]
    frac = sum(1 for z in band if z <= r)/len(band)
    verdict = ("REAL (beyond 1% null)" if r < p1 else "real (beyond 5% null)" if r < p5
               else "inside null")
    print(f"  {H//12:>6}yr {label:>10} {len(idx):>5} {r:>+17.3f} {r*r:>6.3f} {p5:>+8.3f} {p1:>+8.3f} {frac*100:>7.1f}%  {verdict}")

# find index where post-1970 starts
lo70 = next((i for i,d in enumerate(ds) if d >= "1970-01"), 0)
for H in (60, 120):
    run(H, 0, "full 1881+")
    run(H, lo70, "1970+")

# non-overlapping overlap-free sanity (full, 10yr)
H = 120
step = H
xs = [lcape[t] for t in range(0, n-H, step)]; fs = [lrp[t+H]-lrp[t] for t in range(0, n-H, step)]
print(f"\n  overlap-free check (10yr, non-overlapping windows, n={len(xs)}): corr = {corr(xs,fs):+.3f}")

now_cape = cape[-1]
print(f"\n  NOW: CAPE = {now_cape:.1f}  (percentile vs history: "
      f"{sum(1 for c in cape if c<=now_cape)/len(cape)*100:.0f}%)\n")
