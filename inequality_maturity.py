# -*- coding: utf-8 -*-
"""Historical inequality transcriptions used in the public paper.
Read the source tables for pre-industrial societies and pre-1913 US observations.
These descriptive tables are separate from the market's fixed-split correlation
and expanding-fit/resampling checks. Geographic and frontier-estimation bounds
are printed with the results.
"""
from __future__ import annotations
import json, os, statistics as st

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data", "ensemble")
_MLW = os.path.join(_DATA, "mlw_pre_industrial_inequality.json")
_LW  = os.path.join(_DATA, "lindert_williamson_us_preindustrial.json")


def pre_industrial():
    d = json.load(open(_MLW, encoding="utf-8"))
    return d["societies"], d["provenance"]


def us_pre1913():
    d = json.load(open(_LW, encoding="utf-8"))
    return d["observations"], d["provenance"], d.get("bridge_to_wid", "")


def main():
    soc, prov = pre_industrial()
    print("\n=== HISTORICAL TABLE (1): pre-industrial extraction-at-maturity — MLW, read straight ===")
    print("source:", prov["source"])
    print("pdf sha256:", prov["pdf_sha256"][:16], "| extraction = actual Gini / max-feasible Gini (IPF)\n")
    print("  %-26s %5s %6s %7s %6s" % ("society/year", "Gini", "IPF", "extr%", "top1%"))
    anc = [s for s in soc if s["year"] <= 1500]           # the ancient/medieval core, before Europe-1300 series
    for s in sorted(soc, key=lambda x: x["year"]):
        t1 = ("%.1f" % s["top1_share"]) if s["top1_share"] is not None else "  -"
        print("  %-26s %5.1f %6.1f %6d%% %6s"
              % ("%s %d" % (s["society"], s["year"]), s["gini"], s["ipf_max"],
                 s["extraction_pct_s400"], t1))
    ex = [s["extraction_pct_s400"] for s in soc]
    ex.sort()
    q = [ex[int(len(ex)*p)] for p in (.25, .5, .75)]
    at_or_above = sum(1 for x in ex if x >= 90)
    print("\n  n = %d pre-industrial societies (Rome 14AD -> British India 1947)" % len(soc))
    print("  extraction ratio (actual/feasible): median %d%%, IQR %d-%d%%, range %d-%d%%"
          % (q[1], q[0], q[2], ex[0], ex[-1]))
    print("  at or above ~90%% of the feasible maximum: %d of %d" % (at_or_above, len(soc)))
    print("  => read straight (no imported null): pre-industrial elites sat AT or NEAR their inequality-")
    print("     possibility frontier — the taking pressed to the feasible limit, maturity after maturity.")
    print("     Rome 14AD: Gini 39.4, extraction 75%, top-1% 16.1% — the single-seat empire at zenith.")
    print("     (Values >100%% = estimation beyond the frontier, authors flag: Moghul India, Nueva Espana,")
    print("      Bihar, British India. The central tendency, not any one row, carries it.)")

    obs, provb, bridge = us_pre1913()
    print("\n=== HISTORICAL TABLE (2): pre-1913 US pyramid behind the WID floor — Lindert & Williamson ===")
    print("source:", provb["source"])
    print("pdf sha256:", provb["pdf_sha256"][:16], "\n")
    print("  %-38s %5s %6s" % ("geography / year", "Gini", "top1%"))
    for o in obs:
        print("  %-38s %5.3f %5.1f%%" % ("%s %d" % (o["geography"], o["year"]), o["gini"], o["top1_share"]))
    print("\n  =>", bridge)

    print("\nBOUNDS: antiquity Ginis rest on social tables (sparse, estimated; some beyond-frontier);")
    print("  LW US pre-1913 is seaboard/regional, slaves-in/out labelled. Both are SET FACTS read")
    print("  straight and placed beside the existing readings — NOT scored against a chosen null, and")
    print("  No out-of-sample forecast is inferred from these historical tables.")
    print("  Market correlation checks are reported separately in predict.py and string_correlates.py.\n")


if __name__ == "__main__":
    main()
