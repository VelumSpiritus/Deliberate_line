# The Deliberate Line: Taking a Goodhart

### What actually moves the market — a sourced, reproducible account, in plain terms

> *The deliberate line takes a Goodhart;*
> *a Goodhart takes a deliberate line.*

**Noah Davidson.** Public domain (CC0 1.0). Every claim is either computed from public data (with
the code to reproduce it) or cited to a public source. The math is written in ordinary terms so
every step can be checked. *Not investment advice; a description of what the record shows.*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23355671.svg)](https://doi.org/10.5281/zenodo.23355671)

---

## In one minute

Everyone knows the stock market "goes up." Almost no one knows how *exactly*. Over the last 56 years
the S&P 500 has followed one straight line — about **8% a year** — so closely that when price runs
too far above it, the next year is reliably weaker: a pull back toward the line that holds even in
stretches the line was never fit to.

That line isn't the Federal Reserve — its levers, tested honestly, don't draw it — and it isn't just
the economy growing. Roughly **2% a year is the market outrunning the economy**: the same output
priced higher, a transfer from workers to owners that breaks across every measure at once, starting
**around 1979**.

And it isn't only about markets. The same shape — a single seat that concentrates, calls itself
natural, and eventually falls — runs through history, which is why "capitalism vs communism" turns
out to be two names for one taking. This is what makes the line *deliberate*: the market doesn't draw
it — a single seat does, from the top of a structure imposed on the whole world. The market is only
the screen the line is projected onto. The pattern even names its own way out.

**The real choice was never left versus right. It's taking versus receiving.**

---

## Read it

- **[`deliberate_line.html`](deliberate_line.html)** — the full paper as a single self-contained page
  (figures embedded; opens in any browser, on any device, no internet required). **Start here.**
- **[`THE_DELIBERATE_LINE_PUBLIC.md`](THE_DELIBERATE_LINE_PUBLIC.md)** — the same paper in plain
  Markdown, for reading on GitHub or re-hosting anywhere.

## Reproduce it

The whole argument is built from public data (FRED, Yahoo Finance, and the sourced series named in
the paper). The exact inputs are **pinned** in `data/raw/` and content-addressed with sha256, so a
fresh clone reproduces **offline** — same bytes, same read.

```bash
python -m pip install -r requirements.txt   # numpy, matplotlib (that's all)
python data.py          # prints the cached-close count and verify -> True (no network needed)
python draw_line.py     # regenerates the line + flip figure from the pinned data
```

`draw_deep.py`, `draw_all.py`, and `draw_forward.py` regenerate the other figures the same way, each
printing its fitted numbers so they can be checked against the text. See the paper's **"Reproduce
it"** section for the full step-by-step. If a figure in the paper is wrong, the code will say so.

## What's here

| File | What it is |
|------|------------|
| `deliberate_line.html` | Self-contained reader — the paper plus embedded figures |
| `THE_DELIBERATE_LINE_PUBLIC.md` | The paper, plain Markdown |
| `data.py` | Pulls the public series and computes the line, slope, and reversion |
| `requirements.txt` | Python dependencies |
| `LICENSE` | CC0 1.0 Universal — public domain dedication |
| `CITATION.cff` | How to cite this work |

## License

Released under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — all
copyright and related or neighboring rights to *The Deliberate Line: Taking a Goodhart* are waived
and the work is dedicated to the public domain.

You may copy, modify, distribute, and perform the work — including for commercial purposes — all
without asking permission. The reading is handed to the whole.

## Where it lives

This repository is the canonical home. Permanent and citable mirrors:

- **Archive / DOI:** [10.5281/zenodo.23355671](https://doi.org/10.5281/zenodo.23355671) (Zenodo — always resolves to the latest version)
- **Reader:** arkrising — _(link added once hosted)_
- **Announcement:** Substack — _(link added at publish)_
