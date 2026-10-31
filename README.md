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

Over the measured 56-year window, the S&P 500 follows a fitted log-linear trend of about **8% annual compounded price growth**. Larger deviations above that trend are associated with weaker subsequent returns in the historical comparisons. The broader expanding-fit and resampling checks do not establish a reliable price-timing advantage.

That line isn't the Federal Reserve — its levers, tested honestly, don't draw it — and it isn't just
the economy growing. Roughly **2% a year is the market outrunning the economy**: the same output
priced higher, a transfer from workers to owners that breaks across every measure at once, starting
**around 1979**.

The paper connects that premium to ownership claims, policy decisions, and public enforcement. Owners, executives, and officials act within those arrangements; the premium is the financial result of the operation they sustain. The historical comparisons and proposed alternative examine how the rules of collection persist and how they could change.

**The real choice was never left versus right. It's taking versus receiving.**

---

## Read it

- **[`deliberate_line.html`](deliberate_line.html)** — the full paper as a single self-contained page
  (figures embedded; opens in any browser, on any device, no internet required). **Start here.**
- **[`THE_DELIBERATE_LINE_PUBLIC.md`](THE_DELIBERATE_LINE_PUBLIC.md)** — the same paper in plain
  Markdown, for reading on GitHub or re-hosting anywhere.

## The economic theory

[The Veritocratic Economy](VERITOCRATIC_ECONOMY.md) carries the consolidated theory of common and attributable returns, with an exact accounting example. The [original publication snapshot](history/veritocratic-economy-700040f.zip) preserves the former repository's seven files. [Source consolidation](SOURCE_CONSOLIDATION.json) identifies what moved and which older documents remain historical research.

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

### Supporting calculations

Run `python -X utf8 reproduce_support.py` to reproduce the supporting calculations offline.
[SUPPORTING_METHODS.md](SUPPORTING_METHODS.md) maps the paper’s numbers to their computations;
[SUPPORTING_RESULTS.json](SUPPORTING_RESULTS.json) contains the output and input hashes.

### CAPE reproduction

The dated CAPE input and retained historical check are included. Run `python -X utf8 capetest.py`
for the retained log-CAPE/real-price correlations, overlap check and block-bootstrap comparison.
Run `python cape_method_reconstruction.py` for an explicit ten-year real-price OLS reconstruction.
[CAPE_METHODS.json](CAPE_METHODS.json) records the data hash, dates, transformation, coefficients,
return convention and interpretation of the rough range. At CAPE 41 the reconstruction gives
about **−2.29%/yr real price return**, within the paper's retained rough range. Dividend-reinvested
total return is a separate measurement. The dated input is printed with its observation date;
missing observations produce an error rather than a measured zero.

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
