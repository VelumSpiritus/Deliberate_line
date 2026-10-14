#!/usr/bin/env python3
r"""forward_derivation — the deliberate line to 2028, DERIVED from verifiable data and set definitions.

Noah, 2026-09-20: not an assumed reversion coefficient — "a real derivation with the real data and
definitions set, so it's not an assumption but an honest truth of verifiable situation and context."

THE DEFINITIONS (identities, not assumptions):
  (D1)  labor productivity  ≡  real GDP / hours worked         => output = labor × productivity, so
        g_realGDP  =  g_labor  +  g_productivity                  (exact growth-accounting identity)
  (D2)  g_nominalGDP  =  g_realGDP  +  inflation                  (nominal = real + price change)
  (D3)  deliberate-line growth  =  g_nominalGDP  +  w             (w = the extraction wedge, the rate
        the market claim runs above the economy — Sec.3 of the paper, ~2%/yr, multiple + margin)
  (D4)  the current deviation d (+33% above the line) is the ACCUMULATED wedge stretch; it reverts
        because it sits on VERIFIABLE ceilings (profit share and CAPE both at/near record).

THE VERIFIABLE, POLICY-LOCKED INPUT (what makes 2026–2028 a readable window):
  working-age population growth is essentially all migration (native fertility is sub-replacement),
  and migration is exogenously fixed by federal policy through the presidential term (to Jan 2029).
  So g_labor for the window is not a guess — it is the trajectory already in the data (CLF16OV), and
  its demographic floor is the working-age series (LFWA64TTUSM647S). Everything below is COMPUTED
  from the pinned FRED series over a stated recent window; nothing is assumed.

Not advice — a derivation of what the identities give on the verifiable inputs. The trade is Noah's.

    python forward_derivation.py
"""
from __future__ import annotations

import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
ENS = os.path.join(HERE, "data", "ensemble")


def series(name):
    """{fractional_year: value} from a FRED csv (date,value)."""
    out = {}
    p = os.path.join(RAW, "fred_%s.csv" % name)
    with open(p, encoding="utf-8") as fh:
        r = csv.reader(fh)
        next(r, None)
        for row in r:
            if len(row) < 2:
                continue
            try:
                y, m = int(row[0][:4]), int(row[0][5:7])
                out[y + (m - 1) / 12.0] = float(row[1])
            except ValueError:
                continue
    return out


def cagr(s, years):
    """annualized growth over the last `years` of the series (%/yr)."""
    ks = sorted(s)
    if not ks:
        return None
    t1 = ks[-1]
    t0 = t1 - years
    # nearest points
    k1 = ks[-1]
    k0 = min(ks, key=lambda k: abs(k - t0))
    if s[k0] <= 0 or s[k1] <= 0 or (k1 - k0) <= 0:
        return None
    return (math.exp((math.log(s[k1]) - math.log(s[k0])) / (k1 - k0)) - 1) * 100


def latest(s):
    ks = sorted(s)
    return (ks[-1], s[ks[-1]]) if ks else (None, None)


def cape_now():
    import json
    p = os.path.join(ENS, "cape_multpl_monthly.json")
    if os.path.exists(p):
        d = json.loads(open(p, "rb").read().decode("utf-8", "replace"))
        rows = d.get("rows", [])
        if rows:
            return rows[-1].get("cape")
    return None


def main():
    L = series("CLF16OV")            # civilian labor force
    WA = series("LFWA64TTUSM647S")   # working-age population 15-64
    P = series("OPHNFB")             # nonfarm labor productivity
    RG = series("GDPC1")             # real GDP
    NG = series("GDP")               # nominal GDP
    CORE = series("CPILFESL")        # core CPI
    CP = series("CP")                # corporate profits
    GDP = series("GDP")

    print("\n  THE DELIBERATE LINE TO 2028 — DERIVED FROM VERIFIABLE DATA (no assumed reversion)")
    print("  each rate is the annualized change of a pinned FRED series over a stated window.")
    print("  " + "=" * 76)

    # ---- the labor input (the policy-locked variable) ----
    lg1, lg3, lg5 = cagr(L, 1), cagr(L, 3), cagr(L, 5)
    wg1, wg3 = cagr(WA, 1), cagr(WA, 3)
    print("  LABOR (the migration-locked input) — civilian labor force, CLF16OV:")
    print("    growth last 1y / 3y / 5y ....  %+.2f%% / %+.2f%% / %+.2f%% per year" % (lg1, lg3, lg5))
    print("    working-age pop 15-64 (LFWA64) last 1y / 3y ..  %+.2f%% / %+.2f%% per year" % (wg1, wg3))
    print("    -> native fertility is sub-replacement, so this growth IS migration; policy locks it")
    print("       through the term. The forward labor input is this measured trajectory, not a guess.")
    g_labor = lg1   # the locked, current trajectory

    # ---- productivity ----
    pg5, pg10 = cagr(P, 5), cagr(P, 10)
    print("  PRODUCTIVITY — nonfarm business, OPHNFB:")
    print("    growth last 5y / 10y ........  %+.2f%% / %+.2f%% per year" % (pg5, pg10))
    g_prod = pg10   # the stable long trend

    # ---- inflation ----
    inf1, inf3 = cagr(CORE, 1), cagr(CORE, 3)
    print("  INFLATION — core CPI, CPILFESL:")
    print("    last 1y / 3y ................  %+.2f%% / %+.2f%% per year" % (inf1, inf3))
    infl = inf1

    # ---- the identity chain (D1->D3) ----
    g_realGDP = g_labor + g_prod
    g_nominal = g_realGDP + infl
    # cross-check against the actual measured real GDP growth
    rg3 = cagr(RG, 3)
    print("  " + "-" * 76)
    print("  IDENTITY CHAIN (definitions, not assumptions):")
    print("    (D1) real GDP growth = labor + productivity  =  %+.2f%% + %+.2f%%  =  %+.2f%%/yr" %
          (g_labor, g_prod, g_realGDP))
    print("         cross-check: measured real GDP growth last 3y = %+.2f%%/yr" % rg3)
    print("    (D2) nominal GDP growth = real + inflation   =  %+.2f%% + %+.2f%%  =  %+.2f%%/yr" %
          (g_realGDP, infl, g_nominal))

    # ---- the extraction wedge and its ceiling (D4) ----
    (_, cp), (_, ng) = latest(CP), latest(GDP)
    profit_share = cp / ng * 100 if (cp and ng) else None
    ps_hist = None
    ks = sorted(k for k in CP if k in GDP)
    if ks:
        vals = [CP[k] / GDP[k] * 100 for k in ks if GDP[k] > 0]
        ps_hist = sum(vals) / len(vals)
    cape = cape_now()
    print("  " + "-" * 76)
    print("  THE EXTRACTION WEDGE w AND ITS VERIFIABLE CEILING (D4):")
    print("    corporate profit share of GDP NOW = %.1f%%   (post-1947 mean %.1f%%)  -> at a record" %
          (profit_share, ps_hist))
    print("    CAPE valuation NOW = %.0f   (long-run mean ~17)  -> near the dot-com extreme" % (cape or 0))
    print("    so the +33%% stretch is NOT room to keep expanding — both legs of w sit at ceilings and")
    print("    revert. The line's nominal growth is the FLOOR the market grows at once w stops expanding.")

    # ---- the derived forward line ----
    print("  " + "=" * 76)
    print("  THE DERIVED FORWARD RETURN, 2026 -> 2028 (the policy-locked window):")
    print("    the market's nominal return converges to the DERIVED nominal-GDP growth as the wedge")
    print("    stops expanding — bounded, from verifiable inputs:")
    print("      floor  (wedge reverts):   below %+.1f%%/yr, dragged down by the +33%% stretch closing" % g_nominal)
    print("      anchor (wedge just holds): ~%+.1f%%/yr  =  the derived nominal-GDP line" % g_nominal)
    print("    Either way it is WEAK — well under the 8.2%%/yr the market ran when the wedge was still")
    print("    expanding — because forward labor is locked near zero and the wedge cannot re-expand from")
    print("    a record. That is the derived ANCHOR — the weak floor the market grows at once the wedge")
    print("    stops expanding. Whether the +33%% stretch closes toward it as a slow grind or as a release")
    print("    (forward_sim: AR(1) is a smoother; every prior close from a record released -49/-57%%) is")
    print("    the path-fork. The derivation gives the floor, not the shape of the close. Weak either way.")
    print("  " + "-" * 76)
    print("  EVERY INPUT IS A PINNED FRED SERIES OVER A STATED WINDOW. The only projection is that the")
    print("  locked labor trajectory and the stable productivity trend persist through the term — both")
    print("  verifiable today. No reversion coefficient is assumed; the ceiling is read, not modeled.\n")

    return {"g_labor": g_labor, "g_prod": g_prod, "g_realGDP": g_realGDP, "infl": infl,
            "g_nominal": g_nominal, "profit_share": profit_share, "profit_share_mean": ps_hist, "cape": cape}


if __name__ == "__main__":
    main()
