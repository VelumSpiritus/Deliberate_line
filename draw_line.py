"""draw_line.py — the deliberate line, drawn, and the tables flipped.

Two faces in one figure, both off the SAME set facts (Shiller nominal S&P, 1871-2026):
  (1) THE TAKING — the deliberate line: the market pulling ahead of the economy at a reactive
      rate, the fractal releases (1929/2000/2008), the current +33% stretch.
  (2) THE FLIP — the same extraction wedge, tables turned: taking concentrates to one seat and
      must fall; receiving distributes to the base and has no seat to fall from (F closed on itself).

Run: python draw_line.py   ->   figures/deliberate_line.png
Plain math, drawn. Nothing here is asserted the fit can't carry; the received face is labelled a
design (the veritocratic inverse), not a measured series.
"""
import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
SHILLER = os.path.join(HERE, "data", "ensemble", "shiller_sp500_monthly.csv")
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

INK = "#0d0f13"; PAPER = "#e8e4d8"; GOLD = "#d9a441"; TAKE = "#c0503f"; GIVE = "#5b9279"; MUTE = "#8a8577"

def toyr(s):
    y, m = s.split("-")[:2]; return int(y) + (int(m) - 1) / 12.0

def load():
    T, P = [], []
    for r in csv.DictReader(open(SHILLER, encoding="utf-8")):
        try:
            v = float(r["SP500"])
            if v > 0:
                T.append(toyr(r["Date"])); P.append(v)
        except (ValueError, KeyError):
            pass
    return np.array(T), np.array(P)

def fit(t, y):
    b, a = np.polyfit(t, y, 1)
    yhat = a + b * t
    r2 = 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)
    return a, b, r2

def main():
    T, P = load()
    L = np.log(P)
    pre, post = T < 1971, T >= 1971
    a0, b0, r0 = fit(T[pre], L[pre])
    a1, b1, r1 = fit(T[post], L[post])
    dev = L - (a1 + b1 * T)                      # deviation from the post-1971 line
    stretch_now = math.exp(dev[-1]) - 1.0        # current fraction above the line
    two_yr = P[-1] / P[np.argmin(np.abs(T - (T[-1] - 2)))] - 1.0

    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": INK,
                         "axes.facecolor": INK, "savefig.facecolor": INK, "text.color": PAPER,
                         "axes.edgecolor": MUTE, "xtick.color": MUTE, "ytick.color": MUTE})
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.35, 1.0], hspace=0.22,
                          left=0.07, right=0.965, top=0.9, bottom=0.06)

    # ---- PANEL 1 : THE TAKING — the deliberate line ----
    ax = fig.add_subplot(gs[0])
    ax.plot(T, L, color=PAPER, lw=1.1, alpha=0.92, zorder=3)
    tt = np.linspace(1971, T[-1] + 1, 50)
    ax.plot(tt, a1 + b1 * tt, color=GOLD, lw=2.4, zorder=4,
            label=f"the deliberate line  ·  {b1*100:.1f}%/yr  ·  R²={r1:.3f}  (1971→now)")
    tb = np.linspace(T[0], 1971, 50)
    ax.plot(tb, a1 + b1 * tb, color=GOLD, lw=1.1, ls=(0, (2, 3)), alpha=0.5, zorder=4)
    tp = np.linspace(T[0], 1971, 50)
    ax.plot(tp, a0 + b0 * tp, color=MUTE, lw=1.8, zorder=4,
            label=f"pre-1971 (gold standard) · {b0*100:.1f}%/yr · R²={r0:.2f} — a shallower, looser rate")
    ax.fill_between(T[post], (a1 + b1 * T)[post], L[post],
                    where=L[post] > (a1 + b1 * T)[post], color=TAKE, alpha=0.16, zorder=2)

    for yr, name in [(1929, "1929"), (2000, "2000"), (2008, "2008")]:
        i = np.argmin(np.abs(T - yr))
        ax.scatter([T[i]], [L[i]], s=26, color=TAKE, zorder=6)
    ax.annotate("fractal releases — a market crash and a\nstate collapse are one shape, two scales",
                xy=(2000, L[np.argmin(np.abs(T - 2000))]), xytext=(1936, 9.05),
                color=TAKE, fontsize=10.5, va="center",
                arrowprops=dict(arrowstyle="-", color=TAKE, lw=0.8, alpha=0.6))

    # the critical interjections — the single seat forcing a re-rating (trickle-UP); 1979 is one in a chain
    interj = [(1913, "Fed chartered"), (1933, "New Deal · gold call-in"), (1944, "Bretton Woods"),
              (1971, "gold released"), (1979, "Volcker · the hinge"), (2008, "QE"), (2020, "COVID liquidity")]
    for n, (yr, lab) in enumerate(interj, 1):
        yl = L[np.argmin(np.abs(T - yr))]          # sit on the ACTUAL price where the reaction happened
        ax.plot([yr, yr], [yl - 0.22, yl + 0.22], color=GOLD, lw=1.3, alpha=0.9, zorder=5)
        ax.scatter([yr], [yl], s=14, color=GOLD, zorder=6)
        ax.text(yr, yl + 0.32, str(n), color=GOLD, fontsize=8.5, ha="center", va="bottom", weight="bold")
    items = [f"{n} {yr} {lab}" for n, (yr, lab) in enumerate(interj, 1)]
    key = ("critical interjections — the single seat forcing a re-rating (trickle-UP):\n"
           + "    ".join(items[:4]) + "\n" + "    ".join(items[4:]))
    ax.text(1873, -2.5, key, color=GOLD, fontsize=8.8, va="top", ha="left", alpha=0.95)
    ax.axvline(1971, color=GOLD, lw=0.8, ls=":", alpha=0.7)
    ax.annotate("1971 — gold window unbolts;\nthe rate steps up\n(it reacts, it doesn't break)",
                xy=(1971, 4.35), xytext=(1893, 0.4), color=GOLD, fontsize=10.5, va="bottom",
                arrowprops=dict(arrowstyle="-", color=GOLD, lw=0.8, alpha=0.5))
    i_now = -1
    ax.annotate(f"now: +{stretch_now*100:.0f}% above the line\n(+{two_yr*100:.0f}% in two years — the rented future,\nstretched and accelerating)",
                xy=(T[i_now], L[i_now]), xytext=(1988, 9.35), color=PAPER, fontsize=11,
                arrowprops=dict(arrowstyle="->", color=PAPER, lw=1.0, alpha=0.8))

    ax.set_title("THE TAKING  —  the market pulls ahead of the economy at a rate that reacts",
                 color=PAPER, fontsize=14, loc="left", pad=10, weight="bold")
    ax.set_ylabel("log  S&P 500  (nominal)")
    ax.legend(loc="upper left", frameon=False, fontsize=10.5, labelcolor=PAPER)
    ax.set_xlim(T[0] - 2, T[-1] + 6); ax.grid(True, color=MUTE, alpha=0.12)

    # ---- PANEL 2 : FLIP THE TABLES — taking concentrates to a seat; receiving returns to the base ----
    ax2 = fig.add_subplot(gs[1]); ax2.axis("off")
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10)
    ax2.text(0.05, 9.6, "FLIP THE TABLES", color=PAPER, fontsize=14, weight="bold")
    ax2.text(0.05, 9.0, "same wedge, opposite direction", color=MUTE, fontsize=10.5)

    # taking pyramid: base -> single seat at apex (the wedge concentrates upward, must fall)
    take = Polygon([(0.4, 1.0), (4.2, 1.0), (2.3, 8.4)], closed=True, facecolor=TAKE, alpha=0.85, edgecolor=PAPER, lw=1.0)
    ax2.add_patch(take)
    for x in (0.9, 1.6, 2.3, 3.0, 3.7):
        ax2.annotate("", xy=(2.3, 8.0), xytext=(x, 1.2), arrowprops=dict(arrowstyle="-|>", color=PAPER, lw=1.0, alpha=0.6))
    ax2.scatter([2.3], [8.4], s=90, color=GOLD, zorder=6, edgecolor=INK)
    ax2.text(2.3, 9.3, "the single seat", color=GOLD, fontsize=11, ha="center", weight="bold")
    ax2.text(2.3, 8.85, "one yes / no over the whole", color=PAPER, fontsize=8.5, ha="center", alpha=0.8)
    ax2.text(2.3, 0.55, "TAKING  ·  the wedge concentrates to one seat  ·  forces a majority  ·  freezes  ·  must fall",
             color=TAKE, fontsize=9.5, ha="center")
    ax2.text(0.1, 6.7, "death → permanence → death\n— the frozen loop\nthat won't release —",
             color=MUTE, fontsize=8.5, ha="left", va="center", style="italic")

    # the flip arrow
    ax2.add_patch(FancyArrowPatch((4.7, 4.7), (5.7, 4.7), arrowstyle="-|>", mutation_scale=26, color=GOLD, lw=2.2))
    ax2.text(5.2, 5.15, "flip", color=GOLD, fontsize=11, ha="center", weight="bold")

    # receiving: inverted — the wedge distributes back to the base (no apex to fall from)
    give = Polygon([(7.7, 8.4), (5.8, 1.0), (9.6, 1.0)], closed=True, facecolor=GIVE, alpha=0.85, edgecolor=PAPER, lw=1.0)
    ax2.add_patch(give)
    for x in (6.3, 7.1, 7.7, 8.3, 9.1):
        ax2.annotate("", xy=(x, 1.2), xytext=(7.7, 7.9), arrowprops=dict(arrowstyle="-|>", color=PAPER, lw=1.0, alpha=0.7))
    ax2.text(7.7, 9.0, "no seat to fall from", color=GIVE, fontsize=11, ha="center", weight="bold")
    ax2.text(7.7, 0.55, "RECEIVING  ·  the wedge returns to the base  ·  lineage persists, percentage doesn't",
             color=GIVE, fontsize=9.5, ha="center")
    ax2.text(9.9, 6.7, "the seed received —\nnothing evicted,\neverything read",
             color=MUTE, fontsize=8.5, ha="right", va="center", style="italic")

    fig.suptitle("THE DELIBERATE LINE", color=PAPER, fontsize=20, weight="bold", x=0.07, ha="left", y=0.975)
    fig.text(0.965, 0.975, "Shiller S&P 1871–2026",
             color=MUTE, fontsize=9.5, ha="right", va="top")

    path = os.path.join(OUT, "deliberate_line.png")
    fig.savefig(path, dpi=150)
    print("wrote", path)
    print(f"post-1971 slope {b1*100:.2f}%/yr R2={r1:.3f} | pre-1971 {b0*100:.2f}%/yr R2={r0:.3f}")
    print(f"current stretch above line: +{stretch_now*100:.1f}% | two-year nominal: +{two_yr*100:.1f}%")

if __name__ == "__main__":
    main()
