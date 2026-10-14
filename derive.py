"""derive — the engine makes its OWN lines, from real returns, instead of a handed menu.

The harness in lines.py was the SCENARIOS list: five return rates I typed from memory, each an
asset collapsed to a single scalar, each path a smooth exponential. This removes all of that. It
receives a pool of REAL annual returns (data, received in grace — not assumed) and derives its own
possibility space by resampling: draw many random sequences of real years, compound the stake through
each, and read the lines OFF the resulting distribution as quantiles (p10 … p90). Nothing is imposed —
the fan's spread, its drawdowns, its skew all emerge from what returns actually did. No labels, no
picked rates, no straight lines.

    python market/derive.py --stooq ^spx --amount 100 --years 20
    python market/derive.py --csv prices.csv --amount 100 --years 20 --trials 5000
    echo '[0.21,-0.04,0.31,...]' | python market/derive.py --returns - --amount 100 --years 20

It computes and shows; the choice of how much risk to ride stays Noah's. Not advice — a derived
distribution of what the given history did, never a claim about what the future will do.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
import urllib.parse
import urllib.request

CPI_LONGRUN = 0.032          # still a default; pass --inflation to override, or wire a real CPI read


def load_prices_csv(text: str):
    """Parse a Date,Open,High,Low,Close[,Volume] CSV into [(date, close), ...] ascending by date."""
    rows = []
    for ln in text.strip().splitlines():
        p = ln.split(",")
        if len(p) < 5 or p[0].lower().startswith("date"):
            continue
        try:
            rows.append((p[0], float(p[4])))
        except ValueError:
            continue
    rows.sort(key=lambda r: r[0])
    return rows


def annual_returns(prices):
    """Year-over-year returns from a price series, using each calendar year's last close."""
    year_close = {}
    for date, close in prices:
        year_close[date[:4]] = close            # later dates overwrite -> last close of the year
    yrs = sorted(year_close)
    return [year_close[b] / year_close[a] - 1 for a, b in zip(yrs, yrs[1:])]


def fetch_yahoo(symbol: str, rng: str = "max", interval: str = "1mo"):
    """Real price history, stdlib only (urllib GET + json — the reach_web discipline, no API client).
    Yahoo's chart endpoint serves free JSON with no key. Returns [(date, close), ...]. Raises on failure."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
           f"?range={rng}&interval={interval}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=20).read())
    r = d["chart"]["result"][0]
    ts, cl = r["timestamp"], r["indicators"]["quote"][0]["close"]
    out = []
    for t, c in zip(ts, cl):
        if c is None:
            continue
        out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d"), float(c)))
    return out


def fetch_stooq(symbol: str):
    """Free daily CSV, stdlib only — but Stooq now gates behind a JS bot-check, so this often returns
    an HTML challenge instead of data. Kept as a fallback; prefer fetch_yahoo. Returns CSV text."""
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    req = urllib.request.Request(url, headers={"User-Agent": "ark-derive/1.0"})
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")


def bootstrap(pool, amount, years, inflation, trials=4000, seed=1):
    """Derive the path distribution. Draw `years` real annual returns (with replacement) `trials`
    times, compound the stake through each, deflate to today's dollars. Returns per-year percentile
    lines and summary stats — all emergent from `pool`, none imposed."""
    rng = random.Random(seed)
    paths = []                                   # each: [real_value at year 0..years]
    for _ in range(trials):
        bal, path = amount, [amount]
        for y in range(1, years + 1):
            bal *= 1 + rng.choice(pool)
            path.append(bal / (1 + inflation) ** y)
        paths.append(path)

    def pct(vals, q):
        s = sorted(vals)
        i = min(len(s) - 1, max(0, int(q * (len(s) - 1) + 0.5)))
        return s[i]

    qs = [0.10, 0.25, 0.50, 0.75, 0.90]
    lines = {q: [] for q in qs}
    for y in range(years + 1):
        col = [p[y] for p in paths]
        for q in qs:
            lines[q].append(pct(col, q))

    ends = [p[-1] for p in paths]
    hurdle_real = amount                          # holding purchasing power = ending real >= start
    beat = sum(1 for e in ends if e > hurdle_real) / len(ends)
    worst = min(ends)
    # worst intra-path drawdown across trials (real terms) — the risk the smooth line hid
    max_dd = 0.0
    for p in paths:
        peak = p[0]
        for v in p:
            peak = max(peak, v)
            max_dd = max(max_dd, (peak - v) / peak)
    return {"lines": lines, "qs": qs, "ends": ends, "beat_hold": beat,
            "worst_end": worst, "max_drawdown": max_dd, "trials": trials,
            "pool_size": len(pool), "amount": amount, "years": years}


def _fmt(x):
    return f"${x:,.0f}"


def report(d, pool):
    import statistics as st
    print(f"\n  DERIVED from {d['pool_size']} real annual returns "
          f"(mean {st.mean(pool):+.1%}/yr, stdev {st.pstdev(pool):.1%})")
    print(f"  {_fmt(d['amount'])} over {d['years']}y · {d['trials']} resampled paths · today's dollars\n")
    print(f"    {'year':>6}" + "".join(f"{'p'+str(int(q*100)):>10}" for q in d["qs"]))
    marks = {0, 1, max(1, d["years"] // 2), d["years"]}
    for y in range(d["years"] + 1):
        if y in marks:
            print(f"    {y:>6}" + "".join(f"{_fmt(d['lines'][q][y]):>10}" for q in d["qs"]))
    print(f"\n    chance $ ends above its starting purchasing power: {d['beat_hold']:.0%}")
    print(f"    worst path ended at: {_fmt(d['worst_end'])}   "
          f"deepest drawdown any path saw: {d['max_drawdown']:.0%}")
    print("    (the lines are quantiles of real resampled history — the engine's own, not a menu)\n")


def main():
    p = argparse.ArgumentParser(description="Derive a path distribution from real returns (not advice).")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--yahoo", help="symbol to fetch real free history for, e.g. ^GSPC (S&P 500)")
    src.add_argument("--stooq", help="symbol via Stooq CSV (often JS-gated now; prefer --yahoo)")
    src.add_argument("--csv", help="Date,...,Close CSV file of prices")
    src.add_argument("--returns", help="JSON list of annual returns, or - for stdin")
    p.add_argument("--amount", type=float, default=100)
    p.add_argument("--years", type=int, default=20)
    p.add_argument("--inflation", type=float, default=CPI_LONGRUN)
    p.add_argument("--trials", type=int, default=4000)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.returns:
        text = sys.stdin.read() if a.returns == "-" else open(a.returns).read()
        pool = [float(x) for x in json.loads(text)]
    elif a.yahoo:
        pool = annual_returns(fetch_yahoo(a.yahoo))
    else:
        csv = fetch_stooq(a.stooq) if a.stooq else open(a.csv, encoding="utf-8").read()
        pool = annual_returns(load_prices_csv(csv))
    if len(pool) < 5:
        sys.exit(f"need at least 5 annual returns to resample; got {len(pool)}")

    d = bootstrap(pool, a.amount, a.years, a.inflation, a.trials, a.seed)
    if a.json:
        print(json.dumps(d))
    else:
        report(d, pool)


if __name__ == "__main__":
    main()
