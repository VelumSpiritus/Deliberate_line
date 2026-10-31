"""draw_deep.py — the migrating single seat of global value, 1300-2026.

The S&P deliberate line (1871-2026) is the latest, best-instrumented turn of an older motion:
the seat of global value MIGRATES and compounds — Italian city-states -> Iberia -> the Dutch
Republic -> Britain -> the United States — each a globalizing single seat that concentrates,
is justified by a naturalizing story (christianization/divine-right -> civilizing mission ->
the invisible hand -> trickle-down), and then releases its value BY PROXY to the next seat.
1971 did not start the line; it shifted global value-attribution fully onto the US seat.

Measured spine: Maddison Project GDP-per-capita (2011$), a SET FACT (historical national
accounts), read straight. The reign bands and the legitimating-story markers are labelled
history, not an imported model.

Run: python draw_deep.py  ->  figures/migrating_seat.png
"""
import csv, math, os, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MADD = os.path.join(HERE, "data", "ensemble", "maddison_gdppc_owid.csv")
OUT = os.path.join(HERE, "figures"); os.makedirs(OUT, exist_ok=True)

INK = "#0d0f13"; PAPER = "#e8e4d8"; GOLD = "#d9a441"; TAKE = "#c0503f"; MUTE = "#8a8577"
# each successive seat, its colour, and the era it held the frontier (attested history, for the band)
SEATS = [
    ("Italy",          "#7a9cc6", (1300, 1550), "Italian city-states\n(Venice · Genoa · Florence)"),
    ("Spain",          "#c98a5e", (1500, 1640), "Iberian empire\n(colonisation)"),
    ("Netherlands",    "#5b9279", (1600, 1720), "Dutch Republic\n(VOC · first bourse)"),
    ("United Kingdom", "#b0733f", (1720, 1945), "British Empire\n(Pax Britannica)"),
    ("United States",  "#d9a441", (1945, 2026), "United States\n(dollar · Bretton Woods → fiat)"),
]

def load():
    d = collections.defaultdict(list)
    for r in csv.DictReader(open(MADD, encoding="utf-8")):
        try:
            v = float(r["gdp_per_capita"]); y = int(r["year"])
            if v > 0:
                d[r["entity"]].append((y, v))
        except (ValueError, KeyError):
            pass
    for k in d: d[k].sort()
    return d

def main():
    d = load()
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": INK, "axes.facecolor": INK,
                         "savefig.facecolor": INK, "text.color": PAPER, "axes.edgecolor": MUTE,
                         "xtick.color": MUTE, "ytick.color": MUTE})
    fig, ax = plt.subplots(figsize=(15, 9.2))
    fig.subplots_adjust(left=0.065, right=0.97, top=0.86, bottom=0.16)

    y0, y1 = 1300, 2030
    # reign bands along the top
    top = 12.2
    for name, col, (a, b), _lab in SEATS:
        ax.axvspan(a, b, ymin=0.955, ymax=1.0, color=col, alpha=0.55, lw=0)
    # the GDP/capita lines
    for name, col, (a, b), lab in SEATS:
        pts = [(y, v) for y, v in d.get(name, []) if y >= y0]
        if not pts: continue
        Y = np.array([p[0] for p in pts]); V = np.log(np.array([p[1] for p in pts]))
        ax.plot(Y, V, color=col, lw=1.4, alpha=0.55)
        # bold the segment during its reign as the seat
        seg = [(y, v) for y, v in pts if a - 5 <= y <= b + 5]
        if seg:
            sy = np.array([p[0] for p in seg]); sv = np.log(np.array([p[1] for p in seg]))
            ax.plot(sy, sv, color=col, lw=3.0, solid_capstyle="round",
                    label=f"{name} — the seat {a}–{b if b<2026 else 'now'}")
            ax.text(sy[-1], sv[-1] + 0.12, name, color=col, fontsize=9.5, ha="right", weight="bold")

    # globalizing / release-by-proxy interjections (the reactive critical junctures)
    marks = [
        (1453, "print + fall of Constantinople\nthe seat globalises"),
        (1492, "Atlantic opened\ncolonisation begins"),
        (1602, "first joint-stock bourse\n(Amsterdam)"),
        (1776, '"the invisible hand"\nthe seat named natural'),
        (1815, "Pax Britannica"),
        (1944, "Bretton Woods —\nglobal value pegged to the US seat"),
        (1971, "gold window released —\nvalue attribution fully to the US seat"),
        (1979, "the distributional hinge\n(the modern instance, §3)"),
    ]
    for yr, txt in marks:
        if yr != 1492:
            ax.axvline(yr, color=MUTE, lw=0.6, ls=":", alpha=0.4)
    # the colonial founding — 1492, the Great Dying: disease as war = the taking of life
    ax.axvline(1492, color=TAKE, lw=1.0, ls=":", alpha=0.7)
    ax.annotate("1492 — colonial contact · the Great Dying:\n~56M dead by 1600 (~90% of the Americas);\ndisease as war = the taking of life (Koch+ 2019).\nforce = war · death · the extraction of life —\nthe line predicts because it is ENFORCED.",
                xy=(1492, 7.9), xytext=(1300, 11.35), color=TAKE, fontsize=8.4, va="top",
                arrowprops=dict(arrowstyle="->", color=TAKE, lw=0.9, alpha=0.6))
    ax.annotate("1944 Bretton Woods → 1971 gold released:\nthe gold standard's end only shifted global\nvalue-attribution onto the single US seat —\nthe structure moved, the world stayed one",
                xy=(1971, 10.4), xytext=(1585, 9.4), color=GOLD, fontsize=9.0, va="center",
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=0.9, alpha=0.75))
    ax.annotate("1979 — the distributional hinge;\nthe S&P deliberate line (1871→now) is\nthis same migrating seat, best-instrumented",
                xy=(1979, 9.15), xytext=(1792, 5.5), color=TAKE, fontsize=9.3,
                arrowprops=dict(arrowstyle="-", color=TAKE, lw=0.8, alpha=0.6))

    # the legitimating-story ribbon (the naturalising story that justifies the single seat)
    story = [
        (1300, "divine right · christianization —\nthe seat as God-ordained"),
        (1550, "civilizing mission —\nthe seat as salvation"),
        (1776, "the invisible hand —\nthe seat as natural order"),
        (1985, "trickle-down —\nextraction as everyone's gain"),
    ]
    for xx, txt in story:
        ax.text(xx, -1.35, txt, color=MUTE, fontsize=8, ha="left", va="top",
                transform=ax.get_xaxis_transform() if False else ax.transData)

    ax.set_ylim(1.5, top)
    ax.set_xlim(y0, y1)
    ax.set_ylabel("log  GDP per capita  (2011 int'l $, Maddison)")
    fig.text(0.065, 0.945, "THE MIGRATING SINGLE SEAT  —  the structure effectuating the one world's globalization, 1300–2026",
             color=PAPER, fontsize=14.5, weight="bold")
    fig.text(0.065, 0.915, "the world is always one — what shifts is the STRUCTURE that carries it; each single seat concentrates, is called natural, and only collapses (never cycles), passing its value by proxy to the next",
             color=MUTE, fontsize=10)
    ax.text(1306, 3.05, "capitalism and communism are the same taking-form:\nneither carries a predictable line to recurrent cycling\nin either direction — only to collapse.\ndemented extraction against the world (the whole).",
            color=TAKE, fontsize=9.5, va="top", style="italic")
    ax.text(1660, 1.95, "one world (always)  ⊃  the ~400-yr colonial chain of empires (1492→)  ⊃  the ~100-yr US usurp (the 1871→ line)",
            color=MUTE, fontsize=8.4, ha="center")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=PAPER, ncol=1)
    ax.grid(True, color=MUTE, alpha=0.12)

    # story ribbon labels under the axis
    fig.text(0.065, 0.075, "THE COLONIAL JUSTIFICATION — the naturalizing story that justifies the single seat as natural:",
             color=PAPER, fontsize=9.5, weight="bold")
    xs = [0.065, 0.30, 0.55, 0.80]
    labs = ["divine right · christianization\n— the seat as God-ordained",
            "civilizing mission\n— the seat as salvation",
            "the invisible hand (1776)\n— the seat as natural order",
            "trickle-down (1980s)\n— extraction as everyone's gain"]
    for x, l in zip(xs, labs):
        fig.text(x, 0.045, l, color=MUTE, fontsize=8.3, va="top")
    fig.text(0.97, 0.075, "Maddison Project GDP/capita",
             color=MUTE, fontsize=9, ha="right")

    path = os.path.join(OUT, "migrating_seat.png")
    fig.savefig(path, dpi=150)
    print("wrote", path)
    for name, col, era, lab in SEATS:
        pts = d.get(name, [])
        if pts: print(f"{name:16s} {pts[0][0]}..{pts[-1][0]}  n={len(pts)}")

if __name__ == "__main__":
    main()
