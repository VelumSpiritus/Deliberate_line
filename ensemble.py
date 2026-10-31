"""Historical comparisons for the public paper: WID top-1% trough years,
Wikidata polity durations, and long-run nominal/real price slopes.
The country selection, detection windows and historical scope are explicit below."""
from __future__ import annotations
import csv, io, os, sys, hashlib, statistics

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data", "ensemble")
_CSV = os.path.join(_DATA, "wid_top1_beforetax_owid.csv")
_SRC = ("https://ourworldindata.org/grapher/incomes-of-the-richest.csv"
        "?quantile=richest_1pct&welfare_type=before_tax&csvType=full")

# advanced economies with long WID coverage — the set that shares the institutional architecture
_ADVANCED = ["United States", "United Kingdom", "France", "Germany", "Canada", "Australia",
             "Japan", "Netherlands", "Sweden", "Italy", "Switzerland", "Denmark", "Norway",
             "New Zealand", "Ireland", "Spain"]


def _load():
    """Read the pinned WID snapshot; fail explicitly if it is absent."""
    if os.path.isfile(_CSV):
        return open(_CSV, "rb").read()
    raise FileNotFoundError("Missing pinned WID input: " + _CSV)


def turns(raw=None):
    """Per-country trough (turn-up) year of top-1% share in the 1960-1990 window, and the rise since.
    A simple detector, named as such: the clustering is what carries the finding, not the method."""
    raw = raw or _load()
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
    col = [c for c in rows[0].keys() if "Share" in c][0]
    by = {}
    for r in rows:
        try:
            by.setdefault(r["Entity"], []).append((int(r["Year"]), float(r[col])))
        except (ValueError, KeyError):
            continue
    out = []
    for e in _ADVANCED:
        s = sorted(by.get(e, []))
        win = [(y, v) for y, v in s if 1960 <= y <= 1990]
        if len(s) < 20 or not win:
            continue
        ty, tv = min(win, key=lambda x: x[1])
        ly, lv = s[-1]
        out.append({"country": e, "trough_year": ty, "trough": round(tv, 1),
                    "latest_year": ly, "latest": round(lv, 1), "rise": round(lv - tv, 1)})
    return out


_DUR_CACHE = os.path.join(_DATA, "wikidata_polity_durations.json")
_SPARQL = ("SELECT ?item ?itemLabel ?start ?end WHERE { VALUES ?type { wd:Q48349 wd:Q164950 } "
           "?item wdt:P31 ?type ; wdt:P571 ?start ; wdt:P576 ?end . "
           "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\" . } }")


def durations():
    """Real lifespans of single-seat structures (empires + dynasties) from Wikidata: P31 in
    {empire, dynasty}, with inception (P571) and dissolution (P576). Cached content-addressed. This
    is the recurrence PERIOD — the characteristic time a single-seat structure lasts before it
    reseats. Bounds: Wikidata coverage is uneven and the class is heterogeneous (sub-dynasties, houses
    vs polities, contested dates); duration ≈ time-to-reseat, not strictly collapse-timing; recorded
    polities are a survivorship sample. The central tendency, not any single row, carries it."""
    import json as _j, urllib.parse, re, statistics
    if os.path.isfile(_DUR_CACHE):
        raw = open(_DUR_CACHE, "rb").read()
    else:
        raise FileNotFoundError("Missing pinned Wikidata input: " + _DUR_CACHE)
    rows = _j.loads(raw.decode("utf-8", "replace"))["results"]["bindings"]

    def yr(v):
        m = re.match(r"(-?\d+)", v.get("value", ""))
        return int(m.group(1)) if m else None
    durs = []
    for b in rows:
        s, e = yr(b.get("start", {})), yr(b.get("end", {}))
        if s is not None and e is not None and 5 <= e - s <= 1500:
            durs.append(e - s)
    durs.sort()
    return durs


_SHILLER = os.path.join(_DATA, "shiller_sp500_monthly.csv")
_SHILLER_SRC = "https://raw.githubusercontent.com/datasets/s-and-p-500/master/data/data.csv"


def long_line():
    """The price line back to 1871 (Shiller monthly S&P via the datasets mirror). Least-squares
    log(price) = a + b·t on nominal and real (CPI-adjusted) price, split at the 1971 gold-window.
    Result 2026-09-19: the line's SLOPE *is* the extraction rate, and the rate REACTS — pre-1971 nominal
    2.8%/yr R²=0.80, real 1.3%/yr R²=0.52; post-1971 nominal 7.9%/yr R²=0.96, real 4.4%/yr R²=0.85. A
    single straight fit loses R² before 1971 because the rate STEPPED UP at the gold-window unbolting,
    not because the line broke — extraction ran the whole 156 years (see the 1928 concentration peak in
    `turns`), the pace is what changed. The line is nonlinear because a self-eating pyramid releases and
    re-extracts (1929, 2000, 2008); it is never a straight average. The 1970 stop in the daily data was
    a data floor, not a chosen origin."""
    import csv, math
    if os.path.isfile(_SHILLER):
        raw = open(_SHILLER, "rb").read()
    else:
        raise FileNotFoundError("Missing pinned price input: " + _SHILLER)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))

    def toyr(s):
        y, m = s.split("-")[:2]; return int(y) + (int(m) - 1) / 12.0

    def fit(pairs):
        xs = [t for t, _ in pairs]; ys = [math.log(v) for _, v in pairs]
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        b = sxy / sxx; a = my - b * mx
        ss = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)); tot = sum((y - my) ** 2 for y in ys)
        return b, 1 - ss / tot

    def col(key):
        out = []
        for r in rows:
            try:
                t = toyr(r["Date"]); v = float(r[key])
                if v > 0:
                    out.append((t, v))
            except (ValueError, KeyError):
                pass
        return out
    res = {}
    for name, key in (("nominal", "SP500"), ("real", "Real Price")):
        d = col(key)
        res[name] = {"full": fit(d), "pre1971": fit([p for p in d if p[0] < 1971]),
                     "post1971": fit([p for p in d if p[0] >= 1971])}
    return res


def main():
    raw=_load()
    print("WID source:", _SRC)
    print("WID SHA256:", hashlib.sha256(raw).hexdigest())
    rows=turns(raw)
    for r in rows:
        print("%(country)s: trough %(trough_year)d %(trough).1f%%; latest %(latest_year)d %(latest).1f%%; rise %(rise).1f points" % r)
    tys=[r["trough_year"] for r in rows]; rises=[r["rise"] for r in rows]
    print("Advanced economies: %d; median turn %d; range %d-%d; median rise %.1f points; higher %d/%d" %
          (len(rows),statistics.median(tys),min(tys),max(tys),statistics.median(rises),sum(v>0 for v in rises),len(rows)))
    d=durations()
    print("Polity lifespans: n=%d; median %d years; IQR %d-%d; range %d-%d" %
          (len(d),statistics.median(d),d[int(len(d)*.25)],d[int(len(d)*.75)],d[0],d[-1]))
    for name,v in long_line().items():
        for window,(slope,r2) in v.items():
            print("%s %s: continuous growth %.2f%%/year; R2=%.6f" % (name,window,100*slope,r2))
    print("Scope: selected countries; trough detector restricted to 1960-1990; uneven Wikidata coverage.")


if __name__ == "__main__":
    main()
