"""Residual-growth readings used in the public paper.
A: real price growth minus real output growth.
B: valuation-multiple growth plus corporate-margin growth.
C: historical wealth-share growth. Negative readings are floored at zero
when interpreted as the proposed charge. Differences are printed separately."""
from __future__ import annotations
import csv, io, os, math

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENS = os.path.join(_HERE, "data", "ensemble")
_RAW = os.path.join(_HERE, "data", "raw")


def _rows(path):
    return list(csv.reader(io.StringIO(open(path, "rb").read().decode("utf-8", "replace"))))


def _yr(datestr):
    # 'YYYY-MM-01' -> fractional year
    y, m, _d = datestr.split("-")
    return int(y) + (int(m) - 1) / 12.0


def _shiller():
    """{fyear: {sp500(nominal), pe10}} -- claims and the multiple, 1871-> .
    Real claims are formed by deflating nominal S&P with FRED CPI in reading_A, because Shiller's
    own Real-Price column is zeroed in the recent tail (CPI not yet backfilled) -- deflating the
    live nominal price by the live FRED CPI keeps the claims series current to the present."""
    rows = _rows(os.path.join(_ENS, "shiller_sp500_monthly.csv"))
    hdr = rows[0]
    i_sp, i_pe = hdr.index("SP500"), hdr.index("PE10")
    out = {}
    for r in rows[1:]:
        try:
            sp, pe = float(r[i_sp]), float(r[i_pe])
        except (ValueError, IndexError):
            continue
        if sp <= 0:
            continue
        out[_yr(r[0])] = {"sp500": sp, "pe10": (pe if pe > 0 else None)}
    # extend PE10 past the csv's endpoint with the CAPE cache (never overwrite a csv value)
    for y, cape in _cape_extension().items():
        if y in out and out[y]["pe10"] is None:
            out[y]["pe10"] = cape
            out[y]["pe10_src"] = "cape_multpl_monthly.json"
        elif y not in out and y > max(out):
            out[y] = {"sp500": None, "pe10": cape, "pe10_src": "cape_multpl_monthly.json"}
    return out


def _cape_extension():
    """{fyear: cape} from data/ensemble/cape_multpl_monthly.json (Shiller's CAPE as published monthly by
    multpl.com; retrieved 2026-09-20 with page sha and byte count). Extends the
    cached Shiller csv's PE10 past its 2023-09 endpoint. The csv is never rewritten -- the extension is a
    second source laid beside it, and the window printout states which endpoint was used."""
    import json
    p = os.path.join(_ENS, "cape_multpl_monthly.json")
    if not os.path.exists(p):
        return {}
    d = json.loads(open(p, "rb").read().decode("utf-8", "replace"))
    return {_yr(r["date"]): float(r["cape"]) for r in d.get("rows", []) if r.get("cape")}


def _apulia():
    """Alfani & Sardone 2024 Table 3 (Apulia, 1550-1750): {"excluded": {year: top10}, "included": {year: top10}}.
    The primary-table grain of the composite Reading C reads; tentative 1550 anchor kept and flagged."""
    import json
    p = os.path.join(_ENS, "alfani_sardone_2024_apulia_wealth_table3.json")
    if not os.path.exists(p):
        return {}
    d = json.loads(open(p, "rb").read().decode("utf-8", "replace"))
    return {"excluded": {r["year"]: float(r["top10_share"]) for r in d.get("propertyless_excluded", [])},
            "included": {r["year"]: float(r["top10_share"]) for r in d.get("propertyless_included", [])}}


def _alfani():
    """{year: top-10% wealth share of Europe} -- the deep-time within-society wedge, 1300-2010.
    Cached content-addressed (Alfani 2017 VoxEU via a Wayback snapshot; EINITE + Piketty 2014)."""
    import json
    d = json.loads(open(os.path.join(_ENS, "alfani_top10_wealth_voxeu.json"), "rb").read().decode("utf-8", "replace"))
    return {p["year"]: float(p["share"]) for p in d["points"]}


def _fred(name):
    rows = _rows(os.path.join(_RAW, "fred_%s.csv" % name))
    out = {}
    for r in rows[1:]:
        try:
            out[_yr(r[0])] = float(r[1])
        except (ValueError, IndexError):
            continue
    return out


def _at(series, target, tol=0.6):
    """nearest observation to fractional-year target, within tol years, else None."""
    v, _y = _at_yr(series, target, tol)
    return v


def _at_yr(series, target, tol=0.6):
    """nearest observation AND its actual year; (None, None) if none within tol."""
    best, by, bd = None, None, 1e9
    for y, v in series.items():
        d = abs(y - target)
        if d < bd:
            best, by, bd = v, y, d
    return (best, by) if bd <= tol else (None, None)


def _cagr(v0, v1, years):
    if not v0 or not v1 or v0 <= 0 or v1 <= 0 or years <= 0:
        return None
    return (math.log(v1) - math.log(v0)) / years * 100.0   # %/yr, log (continuous)


def reading_A(sh, rgdp, cpi, y0, y1):
    """real claims growth - real realized-output growth, %/yr.
    real claims = nominal S&P / CPI (both live to the present)."""
    nom = {y: d["sp500"] for y, d in sh.items() if d.get("sp500")}
    def realclaim(t):
        n, p = _at(nom, t), _at(cpi, t)
        return (n / p) if (n and p) else None
    c0, c1 = realclaim(y0), realclaim(y1)
    g0, g1 = _at(rgdp, y0), _at(rgdp, y1)
    rc, rg = _cagr(c0, c1, y1 - y0), _cagr(g0, g1, y1 - y0)
    if rc is None or rg is None:
        return None, rc, rg
    return rc - rg, rc, rg


def reading_B(sh, cp, ngdp, y0, y1):
    """multiple-expansion rate (PE10, over its ACTUAL available span) + margin-expansion rate
    (CP/GDP), %/yr. PE10 is price against a 10yr real-earnings base -- independent of GDP, which is
    what makes B a genuine second reading rather than an algebraic re-slice of A. Returns the PE10
    endpoint actually used, so a stale cache is emitted as a failure address, never hidden."""
    pe = {y: d["pe10"] for y, d in sh.items() if d["pe10"]}
    (pe0, py0), (pe1, py1) = _at_yr(pe, y0, tol=1.0), _at_yr(pe, y1, tol=3.5)
    mult = _cagr(pe0, pe1, (py1 - py0)) if (py0 and py1 and py1 > py0) else None
    # profit share = CP/GDP (nominal, aligned)
    def share(t):
        c, g = _at(cp, t), _at(ngdp, t)
        return (c / g) if (c and g) else None
    s0, s1 = share(y0), share(y1)
    marg = _cagr(s0, s1, y1 - y0)
    if mult is None or marg is None:
        return None, mult, marg, py1
    return (mult or 0.0) + (marg or 0.0), mult, marg, py1


def reading_C(alf, y0, y1):
    """DEEP-TIME residual rate: annualized growth of the top-10% wealth share (Alfani), %/yr.
    A rising concentration share = claims/holdings outran the broad commons's realized growth
    (residual rate > 0); a falling share = reversion (the Black Death 1300->1450, the 20th-c leveling
    1910->2010), floored to 0. Independent base (within-society WEALTH) from A (output) and B
    (earnings) -- and it carries residual rate back ~700 years, before the S&P existed. Nearest-point match
    on a 7-point series; coarse by construction, said so."""
    s0, sy0 = _at_yr(alf, y0, tol=80)
    s1, sy1 = _at_yr(alf, y1, tol=80)
    if not (s0 and s1 and sy1 > sy0):
        return None, sy0, sy1
    return _cagr(s0, s1, sy1 - sy0), sy0, sy1


def reading_wider(sh, cpi, gdpdef, ngdp, ndp, z1, y0, y1):
    """THE WIDER BASES, LAID BESIDE A (not replacing it) -- additional comparison bases.
    Each is the same subtraction as Reading A with one term widened, real vs real, %/yr:
      A_ndp  = real S&P claims growth  - real NET domestic product growth   (growth 'received into use',
               net of depreciation: NDP = GDP - consumption of fixed capital, FRED A362RC1Q027SBEA / GDPDEF)
      A_z1   = real growth of ALL-SECTOR total financial assets (Z.1, FRED BOGZ1FL894090005Q) - real GDP
               growth   (the broadest 'common claims brought forward')
      A_eq   = real growth of corporate-equity market value (Z.1, NCBEILQ027S) - real GDP growth
               (the equity claim as the Z.1 measures it, not as an index)
      A_hh   = real growth of household total financial assets (Z.1, TFAABSHNO) - real GDP growth
    Gathered 2026-09-20 from public sources (data/raw/fred_wider_bases_provenance.json carries the
    sha of each csv). Z.1 levels start 1945Q4; all windows here are 1947+."""
    nom = {y: d["sp500"] for y, d in sh.items() if d.get("sp500")}
    def real(series, t, deflator):
        n, p = _at(series, t), _at(deflator, t)
        return (n / p) if (n and p) else None
    out = {}
    # A_ndp: claims as in A; growth = real NDP
    c0, c1 = real(nom, y0, cpi), real(nom, y1, cpi)
    n0, n1 = real(ndp, y0, gdpdef), real(ndp, y1, gdpdef)
    rc, rn = _cagr(c0, c1, y1 - y0), _cagr(n0, n1, y1 - y0)
    out["A_ndp"] = (None if rc is None or rn is None else rc - rn, rc, rn)
    # A_z1 / A_eq / A_hh: claims widened (deflated by CPI like the S&P), growth = real GDP as in A
    g0, g1 = real(ngdp, y0, gdpdef), real(ngdp, y1, gdpdef)
    rg = _cagr(g0, g1, y1 - y0)
    for key, sid in (("A_z1", "BOGZ1FL894090005Q"), ("A_eq", "NCBEILQ027S"), ("A_hh", "TFAABSHNO")):
        ser = z1.get(sid) or {}
        k0, k1 = real(ser, y0, cpi), real(ser, y1, cpi)
        rk = _cagr(k0, k1, y1 - y0)
        out[key] = (None if rk is None or rg is None else rk - rg, rk, rg)
    return out


def _fmt(x):
    return "   n/a" if x is None else "%5.2f" % x


def main():
    sh = _shiller()
    alf = _alfani()
    rgdp, ngdp, cp, cpi = _fred("GDPC1"), _fred("GDP"), _fred("CP"), _fred("CPIAUCSL")
    def _opt(name):
        try:
            return _fred(name)
        except (OSError, IndexError):
            return {}
    gdpdef, ndp = _opt("GDPDEF"), _opt("A362RC1Q027SBEA")
    z1 = {sid: _opt(sid) for sid in ("BOGZ1FL894090005Q", "NCBEILQ027S", "TFAABSHNO")}

    windows = [
        ("1947 -> 2026 (full FRED)", 1947.0, 2026.25),
        ("1971 -> 2026 (post gold)", 1971.0, 2026.25),
        ("1985 -> 2026 (modern)",    1985.0, 2026.25),
        ("2006 -> 2026 (last 20y)",  2006.0, 2026.25),
        ("1871 -> 2026 (Shiller, A needs FRED>=1947)", 1871.0, 2026.25),
    ]

    print("residual growth rate  --  residual inflation carried by claims that outran realized growth  (%/yr)")
    print("  READING A = real claims growth - real GDP growth      (Deliberate Line, Sec.1)")
    print("  READING B = multiple(PE10, extended by the CAPE cache) + margin(CP/GDP)  (Sec.3)")
    print("  charge = max(0, residual rate)   |   divergence |A-B| is the published residual (public paper)")
    print("=" * 78)
    print("%-42s %6s %6s | %6s %6s | %6s %6s" %
          ("window", "A", "B", "clmA", "gdpA", "multB", "margB"))
    print("-" * 78)
    for label, y0, y1 in windows:
        A, rc, rg = reading_A(sh, rgdp, cpi, y0, y1)
        B, mult, marg, pe_end = reading_B(sh, cp, ngdp, y0, y1)
        print("%-42s %6s %6s | %6s %6s | %6s %6s" %
              (label, _fmt(A), _fmt(B), _fmt(rc), _fmt(rg), _fmt(mult), _fmt(marg)))
        tauA = None if A is None else max(0.0, A)
        tauB = None if B is None else max(0.0, B)
        div = None if (A is None or B is None) else abs(A - B)
        stale = ""
        if pe_end and pe_end < y1 - 0.75:
            stale = "  [PE10 endpoint %.1f -- cache stale, refresh the dated CAPE snapshot]" % pe_end
        elif pe_end and pe_end > 2023.75:
            stale = "  [PE10 to %.2f via cape_multpl_monthly.json]" % pe_end
        print("%-42s charge_A=%s charge_B=%s   divergence(next address)=%s%s" %
              ("", _fmt(tauA), _fmt(tauB), _fmt(div), stale))
    if ndp and gdpdef:
        print("=" * 78)
        print("THE WIDER BASES, laid beside A (additional comparison bases; %/yr, floored at 0 when taxed)")
        print("  A_ndp = claims - real NDP (net of depreciation) | A_z1 = all-sector Z.1 financial assets - real GDP")
        print("  A_eq  = Z.1 corporate-equity market value - real GDP | A_hh = household financial assets - real GDP")
        print("-" * 78)
        print("%-30s %7s %7s %7s %7s   (A for comparison)" % ("window", "A_ndp", "A_z1", "A_eq", "A_hh"))
        for label, y0, y1 in windows[:4]:
            wd = reading_wider(sh, cpi, gdpdef, ngdp, ndp, z1, y0, y1)
            A, _, _ = reading_A(sh, rgdp, cpi, y0, y1)
            print("%-30s %7s %7s %7s %7s   A=%s" % (label.split(" (")[0], _fmt(wd["A_ndp"][0]), _fmt(wd["A_z1"][0]),
                                                    _fmt(wd["A_eq"][0]), _fmt(wd["A_hh"][0]), _fmt(A)))
        print("  read off the numbers (not written before them): A_ndp ~ A (depreciation barely moves the base);")
        print("  A_eq ~ A and a little wider (the Z.1 market value of equity agrees with the index); A_z1 and A_hh")
        print("  run NARROWER than A -- all financial claims together (deposits, bonds, equity) outran the economy")
        print("  by LESS than the equity claim alone. So the wedge is carried by the EQUITY claim specifically, not")
        print("  by claims in general: the broadest base does not widen residual rate, it dilutes it. Each is its own reading;")
        print("  none replaces A; the spread across them is the next address, published here, not averaged.")
    print("=" * 78)
    print("READING C -- DEEP-TIME residual rate (Alfani top-10% wealth share, %/yr; floored at 0)")
    print("  the same extraction wedge, carried back ~700 years before the S&P existed")
    print("-" * 78)
    deep = [
        ("1300 -> 1450  (Black Death)", 1300, 1450),
        ("1450 -> 1910  (the long rise)", 1450, 1910),
        ("1810 -> 1910  (industrial peak)", 1810, 1910),
        ("1910 -> 2010  (20th-c leveling)", 1910, 2010),
        ("1300 -> 2010  (whole span)", 1300, 2010),
    ]
    for label, y0, y1 in deep:
        C, cy0, cy1 = reading_C(alf, y0, y1)
        tauC = None if C is None else max(0.0, C)
        note = "" if C is None else ("  (reversion -> charge=0)" if C < 0 else "  (extraction)")
        print("%-42s C=%s  charge_C=%s%s" % (label, _fmt(C), _fmt(tauC), note))
    ap = _apulia()
    if ap:
        print("-" * 78)
        print("READING C' -- the PRIMARY-TABLE grain (Alfani & Sardone 2024, Table 3: Apulia, top-10% wealth share)")
        for tag, key in (("propertyless excluded", "excluded"), ("propertyless included", "included")):
            ser = ap.get(key) or {}
            ys = sorted(ser)
            if len(ys) >= 2:
                C = _cagr(ser[ys[0]], ser[ys[-1]], ys[-1] - ys[0])
                tent = "  [1550 anchor tentative: rural areas only]" if ys[0] == 1550 else ""
                print("%-42s C'=%s  charge=%s  (extraction; %s)%s" %
                      ("%d -> %d  (%s)" % (ys[0], ys[-1], tag), _fmt(C), _fmt(max(0.0, C)),
                       " ".join("%d:%.1f" % (y, ser[y]) for y in ys), tent))
        print("  the composite's 1650->1810 rise (64->82) read at the primary grain: Apulia 67.1->72.8 (excl.)")
        print("  / 70.1->78.4 (incl.) by 1750 -- same direction, same level band; the taking-face at 50-year steps.")
    print("=" * 78)
    print("FAILURE ADDRESSES (emitted, not hidden):")
    print(" - three distinct constructions (A output / B earnings / C wealth); shared inputs are explicit;")
    print("   |A-B| is published, not averaged; C is sign-comparable, not magnitude-comparable.")
    print(" - floored at 0: a negative reading = no tax that interval (growth was NOT outrun).")
    print(" - bases used in the public paper: claims = the market line's series,")
    print("   growth = GDP, form = rate. The wider bases (Z.1 total claims; NDP) are GATHERED and laid")
    print("   beside A above -- further independent readings, published addresses, never a replacement.")
    print(" - PE10 is extended past the Shiller csv (2023-09) by the CAPE cache; each window prints the")
    print("   endpoint it used; the csv itself is never rewritten.")
    print(" - Reading C (deep time) is 7 coarse points on a wealth-share base -- structural sign,")
    print("   not a precise century rate; C' reads one of the composite's four states at 50-year steps.")
    print(" - the wedge is ENFORCED (force thread, THE_DELIBERATE_LINE_PUBLIC.md, sections 3 and 7): a rate read off it is the")
    print("   enforced taking read back as the return; the reading does not launder the force.")


if __name__ == "__main__":
    main()
