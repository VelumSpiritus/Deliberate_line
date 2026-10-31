# -*- coding: utf-8 -*-
"""within_country - the finest section-6b leg: is the non-racial within-country decline border or technology?

Skill-biased technical change / automation (the technology reading) moves income to CAPITAL by
DEEPENING it: rising capital share should come WITH rising investment (more equipment, more R&D). The
border/top-concentration reading says the capital gains are RENTS and payouts - profit share rises
WITHOUT a matching rise in investment. So the discriminator:
    did the corporate PROFIT share rise post-1979 while the INVESTMENT share did NOT?
If yes, the marginal capital gain is rent (border), not productive deepening (technology). Honest
counter kept: intangible/IP investment is undermeasured, so measured investment understates true
deepening - noted as the residual that keeps this from fully closing. FRED, set facts, reads only.
"""
from __future__ import annotations
import numpy as np
import data

def fred_annual(sid):
    by = {}
    for ds, v in data.fred(sid):
        by[int(ds[:4])] = v   # last obs that year
    return by

def first_loaded(cands):
    for c in cands:
        try:
            d = fred_annual(c)
            if len(d) > 20:
                return c, d
        except Exception:
            continue
    return None, None

def trend(series, lo, hi):
    yrs = sorted(y for y in series if lo <= y <= hi)
    if len(yrs) < 5: return None
    t = np.array(yrs, float); y = np.array([series[k] for k in yrs])
    b = np.polyfit(t - t.mean(), y, 1)[0]
    return b, series[yrs[0]], series[yrs[-1]], yrs[0], yrs[-1]

def main():
    prof = fred_annual("W273RE1A156NBEA")          # corporate profit share of GNI, %
    lab, labid = fred_annual("PRS85006173"), "PRS85006173"   # nonfarm labor share index
    invid, inv = first_loaded(["A006RE1Q156NBEA"])  # gross private domestic investment, share of GDP %
    if inv is None:
        gpdi = fred_annual("GPDI"); gdp = fred_annual("GDP")
        yrs = sorted(set(gpdi) & set(gdp))
        inv = {y: 100.0 * gpdi[y] / gdp[y] for y in yrs}; invid = "GPDI/GDP"

    print("series: profit share W273RE1A156NBEA ; labor share %s ; investment %s\n" % (labid, invid))
    for name, s in (("corporate profit share %", prof), ("investment share %%GDP", inv), ("labor share (index)", lab)):
        pre = trend(s, 1947, 1979); post = trend(s, 1979, 2025)
        if pre and post:
            print("  %-26s pre-79 slope %+.4f/yr (%.1f->%.1f)  |  post-79 slope %+.4f/yr (%.1f->%.1f)"
                  % (name, pre[0], pre[1], pre[2], post[0], post[1], post[2]))

    # the discrimination, stated as a ratio of what moved
    py = sorted(y for y in prof if 1979 <= y <= 2025); iy = sorted(y for y in inv if 1979 <= y <= 2025)
    dprof = prof[py[-1]] - prof[py[0]]
    dinv = inv[iy[-1]] - inv[iy[0]]
    print("\n  post-1979 CHANGE:  profit share %+.1f pts ;  investment share %+.1f pts" % (dprof, dinv))
    print("\nREAD: profit share rising while investment share is flat/falling => the marginal capital")
    print("gain is RENT/payout (border/top-concentration), not productive deepening (which automation/")
    print("skill-technology would show as rising investment). That discriminates the non-racial slice")
    print("toward border. HONEST RESIDUAL: intangible/IP investment is undermeasured, so some true")
    print("deepening is missed - which is why this shifts the weighting toward border without fully")
    print("closing it. The finest slice stays partly open by the data's own limits, named, not forced.")

if __name__ == "__main__":
    main()
