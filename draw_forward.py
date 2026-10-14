#!/usr/bin/env python3
r"""draw_forward.py — the deliberate line carried to 2030: the record stretch, the release (the crash
moment), the three convergent confirmations, and the deliberate flip given as what it is.

Noah, 2026-09-20: the line BREATHES — it stretches, releases, re-extracts; the release is the crash
moment and it is predictable. And the table flip must be given to the reader as the honest flip it is,
a DELIBERATE flip. Both faces off the SAME Shiller set facts; the forward line is the post-1971 fit
extended; the release band is the verifiable scale of prior releases; the flip is the veritocratic
inverse, labelled a design, not a measured series.

  python draw_forward.py   ->   figures/forward_line.png
"""
import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
SHILLER = os.path.join(HERE, "data", "ensemble", "shiller_sp500_monthly.csv")
OUT = os.path.join(HERE, "figures"); os.makedirs(OUT, exist_ok=True)
INK = "#0d0f13"; PAPER = "#e8e4d8"; GOLD = "#d9a441"; TAKE = "#c0503f"; GIVE = "#5b9279"; MUTE = "#8a8577"


def toyr(s):
    y, m = s.split("-")[:2]; return int(y) + (int(m) - 1) / 12.0


def load():
    T, P = [], []
    for r in csv.DictReader(open(SHILLER, encoding="utf-8")):
        try:
            v = float(r["SP500"])
            if v > 0: T.append(toyr(r["Date"])); P.append(v)
        except (ValueError, KeyError): pass
    return np.array(T), np.array(P)


def fit(t, y):
    b, a = np.polyfit(t, y, 1)
    r2 = 1 - np.sum((y - (a + b * t)) ** 2) / np.sum((y - y.mean()) ** 2)
    return a, b, r2


def main():
    T, P = load()
    L = np.log(P)
    post = T >= 1971
    a1, b1, r1 = fit(T[post], L[post])
    dev_now = L[-1] - (a1 + b1 * T[-1])
    stretch = math.exp(dev_now) - 1.0
    t_now = T[-1]

    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": INK, "axes.facecolor": INK,
                         "savefig.facecolor": INK, "text.color": PAPER, "axes.edgecolor": MUTE,
                         "xtick.color": MUTE, "ytick.color": MUTE})
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.35, 0.5], hspace=0.22, left=0.07, right=0.955,
                          top=0.9, bottom=0.06)

    # ============ PANEL A — the line carried forward, and the release ============
    ax = fig.add_subplot(gs[0])
    m = T >= 1971
    ax.plot(T[m], L[m], color=PAPER, lw=1.0, alpha=0.9, zorder=3)
    tt = np.linspace(1971, 2030.5, 60)
    lf = a1 + b1 * tt
    ax.plot(tt[tt <= t_now], lf[tt <= t_now], color=GOLD, lw=2.3, zorder=4,
            label="the deliberate line — %.1f%%/yr (R²=%.2f)" % ((math.exp(b1) - 1) * 100, r1))
    ax.plot(tt[tt >= t_now], lf[tt >= t_now], color=GOLD, lw=2.3, ls=(0, (5, 3)), alpha=0.85, zorder=4,
            label="the line, carried forward (the locked window)")

    # prior releases — the verifiable breathing (drawdowns off the line)
    for yr, txt in [(1929, "1929\n−86%"), (2000, "2000\n−49%"), (2008, "2008\n−57%")]:
        i = np.argmin(np.abs(T - yr))
        ax.scatter([T[i]], [L[i]], s=42, color=TAKE, zorder=6)
        ax.annotate(txt, xy=(T[i], L[i]), xytext=(T[i] - 3, L[i] - 0.85), color=TAKE, fontsize=8.5,
                    ha="center", va="top", arrowprops=dict(arrowstyle="->", color=TAKE, lw=0.8, alpha=0.7))

    # the current record stretch
    ax.scatter([t_now], [L[-1]], s=60, color=PAPER, zorder=7, edgecolor=GOLD, lw=1.4)
    ax.annotate("now: +%.0f%% above the line — a RECORD stretch\n(CAPE 41 ≈ dot-com; profit share 12.2%%, at its 12.4%% record)"
                % (stretch * 100), xy=(t_now, L[-1]), xytext=(2001, 8.45), color=PAPER, fontsize=8.8,
                va="center", arrowprops=dict(arrowstyle="->", color=PAPER, lw=0.9, alpha=0.7))

    # the RELEASE band — the crash moment: price returns to the line, releases overshoot below
    line_2028 = a1 + b1 * 2028.0
    rel_top = L[-1]
    rel_lo = line_2028 - 0.30                       # ~overshoot below the line, as 2000/2008 did
    poly = Polygon([(t_now, rel_top), (2028.6, line_2028 + 0.02), (2028.6, rel_lo), (t_now, rel_lo)],
                   closed=True, facecolor=TAKE, alpha=0.13, edgecolor="none", zorder=2)
    ax.add_patch(poly)
    ax.annotate("THE CLOSE — a fork, one destination (the line)\ngrind: dead-money years, still above the "
                "line a while\nrelease: −25% to the line, −49%/−57% tail (1929/2000/2008)",
                xy=(2027.4, (rel_top + rel_lo) / 2 + 0.1), xytext=(2007.0, 4.35),
                color=TAKE, fontsize=8.8, ha="left", va="top",
                arrowprops=dict(arrowstyle="->", color=TAKE, lw=0.9, alpha=0.75))

    ax.axvspan(2026.7, 2029.0, color=GOLD, alpha=0.06, zorder=1)
    ax.text(2027.8, ax.get_ylim()[0] if False else (a1 + b1 * 1975), "policy-locked\nwindow → 2028",
            color=GOLD, fontsize=8, ha="center", va="bottom", alpha=0.9)

    ax.set_xlim(1971, 2030.5)
    ax.set_ylabel("log  S&P 500 (nominal)", color=PAPER, fontsize=9)
    ax.grid(True, color=MUTE, alpha=0.10)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=PAPER)
    ax.set_title("THE DELIBERATE LINE, CARRIED TO 2030 — weak either way; the release is the breath, not the end",
                 color=PAPER, fontsize=12.5, loc="left", weight="bold", pad=10)

    # the three convergent confirmations — true many ways
    ax.text(1972.2, 6.75, "the same weak window, read three independent ways (no shared assumption):",
            color=GOLD, fontsize=8.7, va="top", style="italic")
    conf = ("  1 · growth accounting on locked labor:  real GDP = −0.6% labor + 2.0% productivity;\n"
            "        + 2.5% inflation  =  ~3.9%/yr nominal  (~1% real)\n"
            "  2 · the deviation's own reversion (out-of-sample −0.47):  ~3.8%/yr nominal to 2028\n"
            "  3 · Shiller CAPE→return, 1871→now (r=−0.35):  CAPE 41 → ~−1 to −2.5%/yr REAL\n"
            "        over the next decade  (CAPE 30+ historically → −3.0%/yr)")
    ax.text(1972.2, 6.45, conf, color=PAPER, fontsize=8.2, va="top", linespacing=1.55)

    # ============ PANEL B — the deliberate flip, given honestly ============
    axB = fig.add_subplot(gs[1]); axB.axis("off"); axB.set_xlim(0, 10); axB.set_ylim(0, 10)
    axB.text(0.05, 9.4, "THE DELIBERATE FLIP — the release is the choice", color=PAPER, fontsize=12,
             weight="bold")
    axB.text(0.05, 8.0, "The line is deliberate — extraction enforced. The flip is deliberate too: at the "
             "release, the tables can be turned, on purpose.", color=MUTE, fontsize=9.2)
    # taking pyramid
    axB.add_patch(Polygon([(1.5, 1.0), (0.2, 1.0), (0.85, 6.2)], closed=True, facecolor=TAKE, alpha=0.9))
    axB.text(0.85, 0.4, "TAKING — one seat, concentrate, freeze, must fall", color=TAKE, fontsize=8.5, ha="center")
    axB.add_patch(FancyArrowPatch((2.1, 3.3), (3.4, 3.3), arrowstyle="-|>", mutation_scale=18, color=GOLD, lw=2))
    axB.text(2.75, 4.0, "flip", color=GOLD, fontsize=9.5, ha="center", weight="bold")
    # receiving pyramid (inverted)
    axB.add_patch(Polygon([(3.9, 6.2), (5.2, 6.2), (4.55, 1.0)], closed=True, facecolor=GIVE, alpha=0.9))
    axB.text(4.55, 0.4, "RECEIVING — returns to the base, no seat to fall from (F∘F=F)", color=GIVE,
             fontsize=8.5, ha="center")
    axB.text(6.1, 5.6, "Not a wish bolted on — the same wedge the line measures, run with no external term "
             "to extract from:\ntax the outran surplus, never the person; return it, recomputed each period so "
             "no share hardens into rent.\nThe reader is handed the flip, not told it — a deliberate choice, "
             "the honest inverse of the taking.", color=PAPER, fontsize=8.6, va="top", linespacing=1.5)
    axB.text(6.1, 1.5, "taking vs receiving — the real axis, not left vs right", color=GOLD, fontsize=8.6,
             style="italic")

    fig.text(0.955, 0.965, "Noah Davidson · ARK market engine · Shiller · FRED · derived, not assumed",
             color=MUTE, fontsize=8, ha="right")
    path = os.path.join(OUT, "forward_line.png")
    fig.savefig(path, dpi=140); print("wrote", path)
    print("line %.2f%%/yr | now +%.0f%% | release closes to the line; -49/-57%% prior overshoots"
          % ((math.exp(b1) - 1) * 100, stretch * 100))


if __name__ == "__main__":
    main()
