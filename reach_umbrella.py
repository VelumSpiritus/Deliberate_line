# -*- coding: utf-8 -*-
"""reach_umbrella — territorialization as REACH, tested straight (war claim, empirical leg).

Hypothesis (one law for both groups): the extraction regime propagates to each economy at the moment
it comes under the enforced (dollar/security) umbrella, so
        TURN-YEAR  ~=  max(1979 hinge, umbrella-entry year).
  - Inside by 1979 (13 advanced economies, order since ~1945-49): turn WITH the seat at the ~1979 hinge.
  - Outside in 1979 (Communist bloc, closed/non-aligned economies): turn at ENTRY (liberalization/
    integration), which is later.
For late integrators the pre-entry level is a socialist/closed FLOOR, so the trough is that floor and
the signal is the RISE-ONSET (first sustained climb). We detect onset and compare to max(1979, entry).
Descriptive comparison using WID top-1% before-tax income shares via OWID.
Reads the SAME cached WID CSV; writes nothing. Entry years are a historical overlay, stated as such.
"""
from __future__ import annotations
import csv, io, statistics
import ensemble

# non-umbrella-in-1979 economies with a defensible umbrella/integration ENTRY year (overlay, cited in prose)
ENTRY = {
    "China": 1992, "Russia": 1991, "Poland": 1990, "Hungary": 1990, "Czechia": 1993,
    "Czech Republic": 1993, "Romania": 1990, "Ukraine": 1991, "India": 1991, "Vietnam": 1986,
    "Indonesia": 1967, "Mexico": 1994, "Chile": 1975, "Argentina": 1991, "South Africa": 1994,
    "Egypt": 1991, "Bulgaria": 1990, "Slovakia": 1993, "Slovenia": 1991, "Lithuania": 1991,
    "Latvia": 1991, "Estonia": 1991, "Brazil": 1990, "Thailand": 1980, "Malaysia": 1980,
}

def series_by_entity(raw):
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8","replace"))))
    col = [c for c in rows[0].keys() if "Share" in c][0]
    by = {}
    for r in rows:
        try:
            by.setdefault(r["Entity"], []).append((int(r["Year"]), float(r[col])))
        except (ValueError, KeyError):
            continue
    for e in by: by[e].sort()
    return by

def onset(series, lo=1960, hi=2024, frac=0.25):
    """Trough year in [lo,hi]; rise-onset = first year after trough reaching `frac` of trough->latest rise."""
    win = [(y,v) for y,v in series if lo<=y<=hi]
    if len(win) < 8: return None
    ty, tv = min(win, key=lambda x:x[1])
    ly, lv = series[-1]
    rise = lv - tv
    if rise <= 0: return {"trough_year": ty, "onset_year": None, "trough": tv, "latest": lv, "rise": rise, "cov": (series[0][0], series[-1][0])}
    thr = tv + frac*rise
    on = next((y for y,v in series if y>=ty and v>=thr), ly)
    return {"trough_year": ty, "onset_year": on, "trough": round(tv,1), "latest": round(lv,1),
            "rise": round(rise,1), "cov": (series[0][0], series[-1][0])}

def main():
    raw = ensemble._load()
    by = series_by_entity(raw)

    print("=== UMBRELLA SET (inside by 1979; entry ~1945-49 => predicted turn ~1979) ===")
    u = ensemble.turns(raw)
    tys = [r["trough_year"] for r in u]
    print("  n=%d  median turn %d  range %d-%d  stdev %.1f" % (len(u), statistics.median(tys), min(tys), max(tys), statistics.pstdev(tys)))

    print("\n=== NON-UMBRELLA SET (predicted onset ~ max(1979, entry)) ===")
    print("  %-14s %-9s %-7s %-7s %-7s %-8s %s" % ("country","cov","entry","pred","onset","gap","rise"))
    gaps=[]
    for e in sorted(ENTRY):
        s = by.get(e)
        if not s: continue
        o = onset(s)
        if not o or o["onset_year"] is None:
            print("  %-14s %-9s (flat/declining; no onset)" % (e, "%d-%d"%o["cov"] if o else "--"))
            continue
        entry = ENTRY[e]; pred = max(1979, entry); gap = o["onset_year"] - pred
        covok = s[0][0] <= pred   # coverage must predate the predicted turn to be a real test
        flag = "" if covok else "  (cov starts after pred — weak)"
        if covok: gaps.append(gap)
        print("  %-14s %-9s %-7d %-7d %-7d %-+8d +%.1f%s" % (e, "%d-%d"%o["cov"], entry, pred, o["onset_year"], gap, o["rise"], flag))

    if gaps:
        print("\n  gap = onset - max(1979,entry), countries with coverage predating the prediction: n=%d" % len(gaps))
        print("  median gap %+.0f yr, mean %+.1f, stdev %.1f, |gap|<=5 in %d/%d"
              % (statistics.median(gaps), statistics.mean(gaps), statistics.pstdev(gaps),
                 sum(1 for g in gaps if abs(g)<=5), len(gaps)))
    print("\nREAD: if onset clusters near max(1979,entry) (gap ~0) across a broad non-umbrella set, the")
    print("extraction turn propagates with the umbrella's REACH, not by calendar year — territorialization")
    print("made measurable. BOUNDS: WID before-tax coverage uneven; entry years are historical overlay;")
    print("simple onset detector (clustering carries it); countries whose coverage starts after the")
    print("prediction cannot be tested (flagged).")

if __name__=="__main__":
    main()
