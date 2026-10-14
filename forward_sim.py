#!/usr/bin/env python3
r"""forward_sim — the deliberate line carried forward, and the current stretch reverting to it.

Noah, 2026-09-20: the migration/border policy is exogenously locked through the presidential term
(to 2028), so the one variable that gates the timing of the extraction (labor supply) is FIXED for
that window — which makes the near-term deliberate line unusually PREDICTABLE, "a big window to show
the line through the next years."

This is NOT a crash-date claim. The paper already walked that back (FINDINGS #13: the migration cut is
disinflationary slow growth, not a 1970s stagflation replay; there is deliberately no "collapse year").
What is honest and already proven is that the line is a FORWARD-PREDICTABLE function (predict.py:
out-of-sample reversion -0.47 on years the fit never saw). So the forward path here is exactly that
function, run forward: the deterministic deliberate line, plus the current +33% deviation reverting
toward it at the rate the history itself shows. The predictable part is the REVERSION of the stretch;
the exact timing is a window, not a date.

Method (all from the same pinned data as the rest of the paper):
  1. Fit the deliberate line log(price) = a + b*t on the monthly series (the paper's 8.2%/yr line).
  2. Measure how the deviation reverts: an AR(1) coefficient phi on the monthly deviation series
     (dev_{t+1} = phi*dev_t + noise), estimated by OLS. phi < 1 => the stretch decays; its half-life
     is ln(0.5)/ln(phi) months.
  3. Carry the line forward to 2030 (deterministic) and decay the CURRENT deviation by phi each month.
  4. Projected price = exp(line + decayed deviation). Report the path and the implied annual return.

Not advice. A derivation of what the line's own function projects if its measured reversion holds; the
trade, and anything done with it, is Noah's.

    python forward_sim.py
"""
from __future__ import annotations

import math
import statistics as st
import sys

sys.path.insert(0, r"C:\Users\ndavi\Noah Finances\market")
import data as D


def monthly_logp():
    by = {}
    for d, c in D.closes_dated("^GSPC"):
        if c > 0:
            by[d[:7]] = math.log(c)
    ms = sorted(by)
    return ms, [by[m] for m in ms]


def fit_line(y):
    n = len(y)
    xm, ym = (n - 1) / 2, st.mean(y)
    b = sum((i - xm) * (y[i] - ym) for i in range(n)) / (sum((i - xm) ** 2 for i in range(n)) or 1)
    return b, ym - b * xm


def ar1(dev):
    """OLS phi in dev_{t+1} = phi * dev_t (through the origin — the line is the mean)."""
    x = dev[:-1]
    y = dev[1:]
    num = sum(x[i] * y[i] for i in range(len(x)))
    den = sum(v * v for v in x) or 1.0
    return num / den


def _add_month(ym, k):
    y, m = int(ym[:4]), int(ym[5:7])
    t = (y * 12 + (m - 1)) + k
    return "%04d-%02d" % (t // 12, t % 12 + 1)


def main():
    ms, y = monthly_logp()
    n = len(y)
    b, a = fit_line(y)                                  # the deliberate line
    line = [a + b * i for i in range(n)]
    dev = [y[i] - line[i] for i in range(n)]
    ann = math.exp(b * 12) - 1.0                        # the line's annualized growth
    dev_now = dev[-1]
    phi = ar1(dev)
    half = math.log(0.5) / math.log(phi) if 0 < phi < 1 else float("inf")

    print("\n  THE DELIBERATE LINE, CARRIED FORWARD  (S&P 500, monthly, %s .. %s)" % (ms[0], ms[-1]))
    print("  the line is a forward-predictable function (predict.py: out-of-sample reversion -0.47);")
    print("  here it is run forward, with the current stretch reverting at the rate the history shows.")
    print("  " + "-" * 74)
    print("  the line's growth ............ %5.2f%%/yr" % (ann * 100))
    print("  price vs the line NOW (%s) . %+.1f%%   (%s the line)" %
          (ms[-1], (math.exp(dev_now) - 1) * 100, "ABOVE" if dev_now > 0 else "below"))
    print("  reversion of the stretch ..... AR(1) phi = %.3f per month  ->  half-life %.0f months (~%.1f yr)"
          % (phi, half, half / 12))
    print("  " + "-" * 74)
    print("  %-9s %12s %12s %10s %12s" % ("year-end", "line level", "projected", "vs line", "proj. return"))
    # project month by month to 2030; sample year-ends
    targets = ["2026-12", "2027-12", "2028-12", "2029-12", "2030-12"]
    prev_price = math.exp(y[-1])
    prev_ym = ms[-1]
    rows = []
    for tgt in targets:
        k = (int(tgt[:4]) * 12 + int(tgt[5:7]) - 1) - (int(ms[-1][:4]) * 12 + int(ms[-1][5:7]) - 1)
        if k <= 0:
            continue
        ln = a + b * (n - 1 + k)
        d = dev_now * (phi ** k)
        price = math.exp(ln + d)
        yrs = k / 12.0
        ret = (price / math.exp(y[-1])) ** (1 / yrs) - 1 if yrs > 0 else 0.0
        print("  %-9s %12s %12s %+9.1f%% %11.2f%%" %
              (tgt[:4], "%.0f" % math.exp(ln), "%.0f" % price, (math.exp(d) - 1) * 100, ret * 100))
        rows.append((tgt[:4], math.exp(ln), price, d, ret))
    print("  " + "-" * 74)
    if rows:
        r28 = next((r for r in rows if r[0] == "2028"), rows[-1])
        print("  through 2028 (the policy-locked window): the line rises to ~%.0f while the +%.0f%% stretch"
              % (r28[1], (math.exp(dev_now) - 1) * 100))
        print("  reverts toward it, for an implied ~%.1f%%/yr nominal — the 'weak real returns / lost-decade"
              % (r28[4] * 100))
        print("  shape' the migration-as-timing-lever predicts (FINDINGS #12/#13). This is the GRIND path.")
    print("\n  HONEST BOUNDS — the whole story: the reversion (the DESTINATION, the line) is proven")
    print("  (out-of-sample -0.47). The PATH is a fork. This AR(1) is a linear smoother — the expected")
    print("  path over many outcomes — and CANNOT by construction show a release, so it grinds. But every")
    print("  prior close from a record (1929/2000/2008) came as a RELEASE, -49/-57%% (see draw_forward).")
    print("  The +33%% stretch is moderate vs 2000's +105%%, so the central case is a ~-25%% close to the")
    print("  line, the -57%% overshoot the tail. Weak either way; the close is grind OR release; the year")
    print("  is a WINDOW, not a date; the release is the line breathing, not its end. Not advice.\n")
    return rows


if __name__ == "__main__":
    main()
