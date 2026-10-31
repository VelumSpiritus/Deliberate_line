"""Fixed-split historical reversion check.
Fit on the first 60% of monthly observations; extend the fit untouched
and correlate deviations with subsequent 12-month log returns.
Overlapping returns and one historical split are not independent replications.
"""
from __future__ import annotations

import math
import statistics as st
import sys

import data as D

H = 12          # forward horizon, months
SPLIT = 0.60    # fit the line on the first 60% only


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


def corr(a, b):
    am, bm = st.mean(a), st.mean(b)
    cov = sum((a[i] - am) * (b[i] - bm) for i in range(len(a)))
    d = math.sqrt(sum((x - am) ** 2 for x in a) * sum((x - bm) ** 2 for x in b))
    return cov / d if d else 0.0


if __name__ == "__main__":
    ms, y = monthly_logp()
    n = len(y)
    cut = int(n * SPLIT)

    # fit the line on the IN-SAMPLE portion ONLY; extend its slope/intercept across the whole series
    b, a = fit_line(y[:cut])
    line = [a + b * i for i in range(n)]
    dev = [y[i] - line[i] for i in range(n)]

    def reversion(lo, hi):
        d0, fr = [], []
        for i in range(lo, min(hi, n - H)):
            d0.append(dev[i])
            fr.append(y[i + H] - y[i])          # actual next-12mo return
        return corr(d0, fr), len(d0)

    ins, n_in = reversion(0, cut)
    oos, n_oos = reversion(cut, n)

    print(f"\n  the line as a forward function — fit on {ms[0][:4]}..{ms[cut][:4]}, tested BEYOND it\n")
    print(f"    in-sample  reversion corr(deviation, next-12mo return): {ins:+.3f}  (n={n_in})")
    print(f"    OUT-OF-SAMPLE (years the fit never saw) .............. {oos:+.3f}  (n={n_oos})")
    print("    This is one fixed-split descriptive result; compare string_correlates.py for")
    print("    expanding fits and the resampled-increment comparison. It does not establish a timing edge.")

    now_dev = dev[-1]
    ann = math.exp(b * 12) - 1
    print(f"\n  the function at NOW ({ms[-1]}):")
    print(f"    line's growth ............... {ann*100:5.2f}%/yr")
    print(f"    price vs the line ........... {math.expm1(now_dev)*100:+.1f}%   ({'ABOVE' if now_dev>0 else 'below'} the line)")
    print(f"    (historically a deviation of that sign mean-reverts; the reading is the function's, "
          f"not a forecast to act on.)\n")
