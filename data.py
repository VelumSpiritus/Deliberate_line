"""data — the data floor for the engine.

The read is only as honest as what it stands on. So: FULL daily history via period1/period2 (never
range=max, which Yahoo silently coarsens to quarterly; never a thin 10y window), fetched ONCE and
content-addressed with a sha256 in data/raw/provenance.json, thereafter reread offline. Same bytes ->
same read: a run is reproducible and touches no network once the raw file is present. Nothing
synthetic, nothing re-pulled-differently each run.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import urllib.parse
import urllib.request

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
PROV = os.path.join(RAW, "provenance.json")


def _load_prov() -> dict:
    return json.load(open(PROV, encoding="utf-8")) if os.path.exists(PROV) else {}


def _key(symbol: str, interval: str) -> str:
    return f"{symbol}_{interval}".replace("^", "_").replace("=", "_")


# intraday can't use period1/period2 (Yahoo coarsens it) — each finer interval has a max window it
# will serve. These are the measured maxima (2026-08-24); the window rolls, so an intraday pull is a
# timestamped snapshot (provenance records fetched_at), not fixed history like the daily series.
INTRADAY = {"1m": "7d", "2m": "60d", "5m": "60d", "15m": "60d",
            "30m": "60d", "60m": "730d", "1h": "730d", "90m": "60d"}


def _url(symbol: str, interval: str) -> str:
    q = urllib.parse.quote(symbol)
    if interval in INTRADAY:
        return (f"https://query1.finance.yahoo.com/v8/finance/chart/{q}"
                f"?range={INTRADAY[interval]}&interval={interval}")
    return (f"https://query1.finance.yahoo.com/v8/finance/chart/{q}"
            f"?period1=0&period2=9999999999&interval={interval}")


def _download(url: str) -> bytes:
    """Yahoo answers the browser UA; keep a bare attempt as fallback (a spoofed UA is the failure on
    some hosts, so never assume one disguise works for every host)."""
    last = None
    for headers in ({"User-Agent": "Mozilla/5.0"}, {}):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45).read()
        except Exception as exc:
            last = exc
    raise last


def fetch(symbol: str, interval: str = "1d", *, refresh: bool = False) -> str:
    """Download the full history once; thereafter return the preserved file. A file recorded under a
    different url is stale and refetched. sha256 + fetched_at recorded either way."""
    key, url, path = _key(symbol, interval), _url(symbol, interval), None
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, key + ".json")
    rec = _load_prov().get(key, {})
    if os.path.exists(path) and not refresh and rec.get("url") == url:
        return path
    data = _download(url)
    with open(path, "wb") as fh:
        fh.write(data)
    prov = _load_prov()
    prov[key] = {"symbol": symbol, "interval": interval, "url": url,
                 "sha256": hashlib.sha256(data).hexdigest(),
                 "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "bytes": len(data)}
    with open(PROV, "w", encoding="utf-8") as fh:
        json.dump(prov, fh, indent=2)
    return path


def closes(symbol: str, interval: str = "1d", *, refresh: bool = False) -> list[float]:
    """Full-history closes for a symbol, from the preserved raw file (fetched once)."""
    payload = json.load(open(fetch(symbol, interval, refresh=refresh), encoding="utf-8"))
    q = payload["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    return [float(c) for c in q if c is not None]


def fred(series_id: str, *, refresh: bool = False):
    """A FRED series (the reserve's own published record — CPI, fed funds, M2, ...) as [(date, value)],
    content-addressed like the price series. The LENS the market can't read for itself. FRED refuses a
    spoofed 'Mozilla' UA (the disguise is the failure there), so try bare first. Missing values ('.' on
    a date) are gaps, skipped, never zeroed."""
    key = f"fred_{series_id}"
    path = os.path.join(RAW, key + ".csv")
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    os.makedirs(RAW, exist_ok=True)
    rec = _load_prov().get(key, {})
    if not (os.path.exists(path) and not refresh and rec.get("url") == url):
        last = None
        data = None
        for headers in ({}, {"User-Agent": "Mozilla/5.0"}):   # bare FIRST for FRED
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45).read()
                break
            except Exception as exc:
                last = exc
        if data is None:
            raise last
        with open(path, "wb") as fh:
            fh.write(data)
        prov = _load_prov()
        prov[key] = {"series": series_id, "url": url, "sha256": hashlib.sha256(data).hexdigest(),
                     "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "bytes": len(data)}
        with open(PROV, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    out = []
    for line in open(path, encoding="utf-8").read().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                out.append((parts[0], float(parts[1])))
            except ValueError:
                continue        # "." = no observation that day
    return out


def closes_dated(symbol: str, interval: str = "1d", *, refresh: bool = False):
    """[(YYYY-MM-DD, close), ...] — closes carrying their timestamps, so the price series can be
    aligned to a dated lens (FRED) causally: only lens values published on/before a market day."""
    payload = json.load(open(fetch(symbol, interval, refresh=refresh), encoding="utf-8"))
    r = payload["chart"]["result"][0]
    ts, q = r["timestamp"], r["indicators"]["quote"][0]["close"]
    out = []
    for t, c in zip(ts, q):
        if c is None:
            continue
        out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d"), float(c)))
    return out


def verify(symbol: str, interval: str = "1d") -> dict:
    """Re-hash the preserved bytes against provenance — same bytes => same read."""
    key = _key(symbol, interval)
    rec = _load_prov().get(key)
    path = os.path.join(RAW, key + ".json")
    if not rec or not os.path.exists(path):
        return {"symbol": symbol, "verified": False, "reason": "no cache/provenance"}
    actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return {"symbol": symbol, "verified": actual == rec["sha256"], "sha256": actual}


if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "^GSPC"
    c = closes(sym)
    print(f"{sym}: {len(c)} closes cached; verify -> {verify(sym)['verified']}")
