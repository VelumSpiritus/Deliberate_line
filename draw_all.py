"""draw_all.py — the whole argument in one image, three panels:

  A · THE MIGRATING SEAT (1300–2026) — the structure effectuating the one world's globalization
      (Maddison GDP/capita frontier), with the within-society EXTRACTION WEDGE overlaid: measured
      income Gini from 1913 (WID) + Alfani's documented pre-1820 wealth-concentration rise (cited).
  B · THE DELIBERATE LINE (1871–2026) — the latest, best-instrumented turn: the reactive-rate line,
      the fractal releases, the critical interjections (the single seat forcing a re-rating), +33% now.
  C · FLIP THE TABLES — same wedge, opposite direction: taking concentrates to one seat and must fall;
      receiving returns to the base, no seat to fall from (F∘F = F).

Measured set facts, content-addressed: Shiller monthly S&P (1871), Maddison GDP/capita (1300),
WID income Gini (1913). The pre-1820 wedge is Alfani (2021 JEL; Alfani & Ammannati 2017), CITED —
its series is not cleanly fetchable, so it is drawn as a labelled cited band, never as fake points.

Run: python draw_all.py  ->  figures/deliberate_line_full.png
"""
import csv, json, math, os, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data", "ensemble")
OUT = os.path.join(HERE, "figures"); os.makedirs(OUT, exist_ok=True)
INK = "#0d0f13"; PAPER = "#e8e4d8"; GOLD = "#d9a441"; TAKE = "#c0503f"; GIVE = "#5b9279"; MUTE = "#8a8577"

def toyr(s):
    y, m = s.split("-")[:2]; return int(y) + (int(m) - 1) / 12.0

def fitline(t, y):
    b, a = np.polyfit(t, y, 1)
    yhat = a + b * t
    return a, b, 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)

def load_shiller():
    T, P = [], []
    for r in csv.DictReader(open(os.path.join(D, "shiller_sp500_monthly.csv"), encoding="utf-8")):
        try:
            v = float(r["SP500"])
            if v > 0: T.append(toyr(r["Date"])); P.append(v)
        except (ValueError, KeyError): pass
    return np.array(T), np.array(P)

def load_maddison():
    d = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(D, "maddison_gdppc_owid.csv"), encoding="utf-8")):
        try:
            v = float(r["gdp_per_capita"]); y = int(r["year"])
            if v > 0: d[r["entity"]].append((y, v))
        except (ValueError, KeyError): pass
    for k in d: d[k].sort()
    return d

def load_gini(entity="United States"):
    out = []
    for r in csv.DictReader(open(os.path.join(D, "wid_gini_owid.csv"), encoding="utf-8")):
        if r["entity"] == entity:
            try: out.append((int(r["year"]), float(r["gini"])))
            except (ValueError, KeyError): pass
    return sorted(out)

def load_alfani():
    import json
    j = json.load(open(os.path.join(D, "alfani_top10_wealth_voxeu.json"), encoding="utf-8"))
    return [(p["year"], p["share"], "exact" in p["basis"]) for p in j["points"]]

SEATS = [
    ("Italy", "#7a9cc6", (1300, 1550)), ("Spain", "#c98a5e", (1500, 1640)),
    ("Netherlands", "#5b9279", (1600, 1720)), ("United Kingdom", "#b0733f", (1720, 1945)),
    ("United States", "#d9a441", (1945, 2026)),
]

def main():
    T, P = load_shiller(); L = np.log(P)
    mad = load_maddison(); alf = load_alfani()
    pre, post = T < 1971, T >= 1971
    a0, b0, r0 = fitline(T[pre], L[pre]); a1, b1, r1 = fitline(T[post], L[post])
    dev_now = math.exp(L[-1] - (a1 + b1 * T[-1])) - 1
    two_yr = P[-1] / P[np.argmin(np.abs(T - (T[-1] - 2)))] - 1

    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": INK, "axes.facecolor": INK,
                         "savefig.facecolor": INK, "text.color": PAPER, "axes.edgecolor": MUTE,
                         "xtick.color": MUTE, "ytick.color": MUTE})
    fig = plt.figure(figsize=(15, 20))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.1, 1.1, 0.72], hspace=0.28,
                          left=0.075, right=0.9, top=0.945, bottom=0.04)

    # ================= PANEL A — THE MIGRATING SEAT + THE WEDGE =================
    axA = fig.add_subplot(gs[0])
    for name, col, (a, b) in SEATS:
        axA.axvspan(a, b, ymin=0.955, ymax=1.0, color=col, alpha=0.55, lw=0)
        pts = [(y, v) for y, v in mad.get(name, []) if y >= 1300]
        if not pts: continue
        Y = np.array([p[0] for p in pts]); V = np.log(np.array([p[1] for p in pts]))
        axA.plot(Y, V, color=col, lw=1.2, alpha=0.5)
        seg = [(y, v) for y, v in pts if a - 5 <= y <= b + 5]
        sy = np.array([p[0] for p in seg]); sv = np.log(np.array([p[1] for p in seg]))
        axA.plot(sy, sv, color=col, lw=2.8, solid_capstyle="round", label=f"{name} — the seat {a}–{b if b<2026 else 'now'}")
        axA.text(sy[-1], sv[-1] + 0.13, name, color=col, fontsize=9, ha="right", weight="bold")
    axA.annotate("1944 Bretton Woods → 1971 gold released:\nglobal value-attribution shifts onto the single US seat —\nthe structure moved, the world stayed one",
                 xy=(1971, 10.3), xytext=(1560, 9.3), color=GOLD, fontsize=8.5, va="center",
                 arrowprops=dict(arrowstyle="->", color=GOLD, lw=0.9, alpha=0.7))
    # the colonial founding — 1492, the Great Dying: disease as war = the taking of life
    axA.axvline(1492, color=TAKE, lw=0.9, ls=":", alpha=0.6)
    axA.annotate("1492 — colonial contact · the Great Dying:\n~56M dead by 1600 (~90% of the Americas);\ndisease as war = the taking of life (Koch+ 2019)",
                 xy=(1492, 8.05), xytext=(1300, 10.95), color=TAKE, fontsize=8, va="top",
                 arrowprops=dict(arrowstyle="->", color=TAKE, lw=0.8, alpha=0.6))
    axA.text(1300, 6.4, "force = war · death · the extraction of life —\nthe line is ENFORCED, which is why it predicts",
             color=GOLD, fontsize=8.3, va="top", style="italic")
    axA.axvline(1913, color=MUTE, lw=0.6, ls="--", alpha=0.35)
    axA.text(1650, 1.75, "one world (always)  ⊃  the ~400-yr colonial chain of empires (1492→)  ⊃  the ~100-yr US usurp (panel B)",
             color=MUTE, fontsize=8.2, ha="center")
    axA.set_ylim(1.5, 12.2); axA.set_xlim(1300, 2030)
    axA.set_ylabel("log GDP/capita (2011$, Maddison)", color=PAPER, fontsize=9)
    axA.grid(True, color=MUTE, alpha=0.10)
    axA.legend(loc="lower right", frameon=False, fontsize=8, labelcolor=PAPER)
    axA.set_title("A · THE MIGRATING SINGLE SEAT — the structure effectuating the one world's globalization, and the extraction wedge within",
                  color=PAPER, fontsize=12.5, loc="left", weight="bold", pad=8)

    # the within-society EXTRACTION WEDGE — Alfani top-10% wealth share, Europe, 1300–2010 (gathered)
    axW = axA.twinx()
    axW.set_ylim(38, 96); axW.set_ylabel("top-10% wealth share, Europe % (Alfani/Piketty)", color=TAKE, fontsize=9)
    axW.tick_params(axis="y", colors=TAKE)
    ay = [p[0] for p in alf]; av = [p[1] for p in alf]
    axW.plot(ay, av, color=TAKE, lw=2.0, alpha=0.9, zorder=5)
    for y, v, ex in alf:
        axW.scatter([y], [v], s=36 if ex else 26, color=(TAKE if ex else INK), edgecolor=TAKE, lw=1.2, zorder=6)
        axW.text(y, v + 1.8, f"{v}%", color=TAKE, fontsize=7.6, ha="center")
    axW.text(1912, 90, "  peak 90% (1910)", color=TAKE, fontsize=7.8, ha="left", va="center")
    # the PRIMARY-TABLE grain of the same wedge: Alfani & Sardone 2024 Table 3, Apulia 1550-1750 (one of the
    # four states averaged into the composite) -- propertyless excluded (filled) / included (hollow)
    try:
        ap = json.load(open(os.path.join(D, "alfani_sardone_2024_apulia_wealth_table3.json"), encoding="utf-8"))
        ex = [(r["year"], r["top10_share"]) for r in ap.get("propertyless_excluded", [])]
        inc = [(r["year"], r["top10_share"]) for r in ap.get("propertyless_included", [])]
        if ex:
            axW.plot([y for y, _ in ex], [v for _, v in ex], color=GOLD, lw=1.3, ls="--", alpha=0.85, zorder=5)
            axW.scatter([y for y, _ in ex], [v for _, v in ex], s=22, marker="s", color=GOLD, zorder=6)
        if inc:
            axW.scatter([y for y, _ in inc], [v for _, v in inc], s=22, marker="s", facecolor=INK, edgecolor=GOLD, lw=1.1, zorder=6)
        axW.text(1760, 46.0, "Apulia, primary table (Alfani & Sardone 2024): 57→73% excl. / 69→78% incl., 1550–1750\n■ excluded  □ propertyless included",
                 color=GOLD, fontsize=7.0, ha="left", va="top", style="italic")
    except Exception as exc:
        print("apulia overlay skipped:", exc)
    axA.text(1305, 4.5, "the within-society EXTRACTION WEDGE = top-10% wealth share, Europe\n(Alfani 2017 VoxEU · EINITE + Piketty 2014; gathered via reach_web→Wayback)\nBlack-Death dip → rise to the 1910 peak → fall → rising again since ~1950.  ● exact-stated  ○ derived",
             color=TAKE, fontsize=7.6, va="top", style="italic")

    # ================= PANEL B — THE DELIBERATE LINE =================
    axB = fig.add_subplot(gs[1])
    axB.plot(T, L, color=PAPER, lw=1.0, alpha=0.92, zorder=3)
    tt = np.linspace(1971, T[-1] + 1, 40); axB.plot(tt, a1 + b1 * tt, color=GOLD, lw=2.3, zorder=4,
             label=f"the deliberate line · {b1*100:.1f}%/yr · R²={r1:.3f} (1971→now)")
    tb = np.linspace(T[0], 1971, 40); axB.plot(tb, a1 + b1 * tb, color=GOLD, lw=1.0, ls=(0, (2, 3)), alpha=0.5, zorder=4)
    tp = np.linspace(T[0], 1971, 40); axB.plot(tp, a0 + b0 * tp, color=MUTE, lw=1.7, zorder=4,
             label=f"pre-1971 · {b0*100:.1f}%/yr · R²={r0:.2f} — shallower, looser (the rate steps up, it doesn't break)")
    axB.fill_between(T[post], (a1 + b1 * T)[post], L[post], where=L[post] > (a1 + b1 * T)[post], color=TAKE, alpha=0.16, zorder=2)
    for yr in (1929, 2000, 2008):
        i = np.argmin(np.abs(T - yr)); axB.scatter([T[i]], [L[i]], s=22, color=TAKE, zorder=6)
    interj = [(1913, "Fed"), (1933, "New Deal·gold call-in"), (1944, "Bretton Woods"), (1971, "gold released"),
              (1979, "Volcker·the hinge"), (2008, "QE"), (2020, "COVID liquidity")]
    for n, (yr, lab) in enumerate(interj, 1):
        yl = L[np.argmin(np.abs(T - yr))]
        axB.plot([yr, yr], [yl - 0.22, yl + 0.22], color=GOLD, lw=1.2, alpha=0.9, zorder=5)
        axB.scatter([yr], [yl], s=12, color=GOLD, zorder=6)
        axB.text(yr, yl + 0.30, str(n), color=GOLD, fontsize=8, ha="center", va="bottom", weight="bold")
    items = [f"{n} {yr} {lab}" for n, (yr, lab) in enumerate(interj, 1)]
    axB.text(1873, -2.6, "critical interjections — the single seat forcing a re-rating (trickle-UP):\n"
             + "    ".join(items[:4]) + "\n" + "    ".join(items[4:]), color=GOLD, fontsize=8.3, va="top")
    axB.annotate(f"now: +{dev_now*100:.0f}% above the line\n(+{two_yr*100:.0f}% in two years — the rented future)",
                 xy=(T[-1], L[-1]), xytext=(1975, 5.9), color=PAPER, fontsize=9.5,
                 arrowprops=dict(arrowstyle="->", color=PAPER, lw=1.0, alpha=0.8))
    axB.set_ylabel("log S&P 500 (nominal)", fontsize=9); axB.set_xlim(T[0] - 2, T[-1] + 6)
    axB.grid(True, color=MUTE, alpha=0.12); axB.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=PAPER)
    axB.set_title("B · THE DELIBERATE LINE (1871–2026) — the latest, best-instrumented turn: the market pulls ahead of the economy at a rate that reacts",
                  color=PAPER, fontsize=12.5, loc="left", weight="bold", pad=8)

    # ================= PANEL C — FLIP THE TABLES =================
    axC = fig.add_subplot(gs[2]); axC.axis("off"); axC.set_xlim(0, 10); axC.set_ylim(0, 10)
    axC.text(0.02, 9.6, "C · FLIP THE TABLES", color=PAPER, fontsize=12.5, weight="bold")
    axC.text(0.02, 8.9, "same wedge, opposite direction", color=MUTE, fontsize=10)
    take = Polygon([(0.5, 0.8), (4.3, 0.8), (2.4, 8.0)], closed=True, facecolor=TAKE, alpha=0.85, edgecolor=PAPER, lw=1.0)
    axC.add_patch(take)
    for x in (1.0, 1.7, 2.4, 3.1, 3.8):
        axC.annotate("", xy=(2.4, 7.6), xytext=(x, 1.0), arrowprops=dict(arrowstyle="-|>", color=PAPER, lw=1.0, alpha=0.6))
    axC.scatter([2.4], [8.0], s=80, color=GOLD, zorder=6, edgecolor=INK)
    axC.text(2.4, 8.55, "the single seat", color=GOLD, fontsize=10.5, ha="center", weight="bold")
    axC.text(2.4, 0.2, "TAKING · concentrates to one seat · forces a majority · freezes · must fall", color=TAKE, fontsize=9, ha="center")
    axC.add_patch(FancyArrowPatch((4.8, 4.2), (5.8, 4.2), arrowstyle="-|>", mutation_scale=24, color=GOLD, lw=2.0))
    axC.text(5.3, 4.65, "flip", color=GOLD, fontsize=10.5, ha="center", weight="bold")
    give = Polygon([(7.8, 8.0), (5.9, 0.8), (9.7, 0.8)], closed=True, facecolor=GIVE, alpha=0.85, edgecolor=PAPER, lw=1.0)
    axC.add_patch(give)
    for x in (6.4, 7.1, 7.8, 8.5, 9.2):
        axC.annotate("", xy=(x, 1.0), xytext=(7.8, 7.6), arrowprops=dict(arrowstyle="-|>", color=PAPER, lw=1.0, alpha=0.7))
    axC.text(7.8, 8.55, "no seat to fall from", color=GIVE, fontsize=10.5, ha="center", weight="bold")
    axC.text(7.8, 0.2, "RECEIVING · returns to the base · lineage persists, percentage doesn't · F∘F = F", color=GIVE, fontsize=9, ha="center")

    fig.suptitle("THE DELIBERATE LINE", color=PAPER, fontsize=21, weight="bold", x=0.075, ha="left", y=0.982)
    fig.text(0.9, 0.982, "Noah Davidson · ARK market engine · Shiller · Maddison · Alfani 2017/Piketty · Alfani & Sardone 2024 · WID",
             color=MUTE, fontsize=9, ha="right", va="top")
    path = os.path.join(OUT, "deliberate_line_full.png")
    fig.savefig(path, dpi=140); print("wrote", path)
    print(f"line post-1971 {b1*100:.2f}%/yr R2={r1:.3f} | now +{dev_now*100:.1f}% | 2yr +{two_yr*100:.1f}%")

if __name__ == "__main__":
    main()
