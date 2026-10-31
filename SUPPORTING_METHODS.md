# Supporting calculations

Run `python -X utf8 reproduce_support.py` after installing `requirements.txt`.
The runner disables network connections and records stdout, input hashes and
script hashes in `SUPPORTING_RESULTS.json`. Inputs are historical snapshots,
not live observations. Code and generated text use LF endings; data snapshots preserve their published bytes, so hashes agree across platforms.

| Published quantity | Calculation | Inputs and convention |
|---|---|---|
| Common and attributable payments from one pool | `common_return_accounting.py` | Supplied illustrative interval rate, surplus, common portion, and attributable weights. Exact fractions conserve the pool without adding universal payments a second time; this does not infer contribution or a macroeconomic response. |
| Premium rate, fraction of growth, and indexed gap share | `premium_accounting.py` | Stated rounded annual log-growth inputs: 7.9% and 5.6%. Their difference is 2.3%/yr; dividing by 7.9%/yr gives about 29% of growth. The level-share conversion explicitly includes elapsed years. This is an arithmetic illustration, not a new empirical estimate. |
| Fixed-split correlation near −0.47 | `predict.py` | Monthly final available S&P closes; fit first 60%, extend untouched; 12-month overlapping log returns. One historical split, compared with the broader check below. |
| Full correlation sequence, −0.02 through −0.27 | `string_correlates.py` | Expanding monthly fits and moving-block resampling of observed increments; 1,000 draws, seed 7. |
| 13 economies; median turn 1981; median rise 4.9 points | `ensemble.py` | WID top-1% before-tax income share; selected country list; minimum in 1960–1990. |
| 212 historical lifespans; median 175, IQR 104–320 years | `ensemble.py` | Pinned Wikidata query response; empire/dynasty classes with inception and dissolution, durations 5–1,500 years. Coverage and classification vary. |
| Nominal/real slopes before and after 1971 | `ensemble.py` | Shiller mirror; positive observations only, separately available nominal and real spans. Slopes are continuous log growth. |
| Party slopes 7.86% / 8.03%; slope-difference t near 0.35 | `party_invariance.py` | Last available price per calendar year; explicit party-year assignments; OLS interaction, conventional OLS standard errors. |
| Profit/investment changes +4.1 / −2.3 points | `within_country.py` | FRED W273RE1A156NBEA (profit share of GNI) and A006RE1Q156NBEA (investment share of GDP), last available observation per year, 1979–2025. |
| Three residual-growth readings | `veritocratic_rate.py` | Shiller/CAPE, FRED GDP/CPI/profits and Alfani wealth shares; log growth over printed windows. Each reading and disagreement is printed separately. |
| Umbrella comparison: 11/14 within five years, median gap +2 years | `reach_umbrella.py` | Same WID top-1% input; explicit historical entry-year overlay; onset detector and coverage filter. The overlay is an input, not inferred from the series. |
| Labor correlation near −0.84 and roughly six-point difference | `labor_cost.py` | WID top-1% and FRED PRS85006173. The latter is an **index**: the difference is index points, using pre/post-1979 averages of last-available annual observations. |
| Defense-spending comparisons | `war_funds.py` | Pinned FRED defense/GDP and price series; reported lead/lag correlations and own-increment bootstrap comparisons. |
| Roughly four-year half-life, 25% price fraction, threefold compounding | `window_math.py`, `two_regimes.py` | Price-fit/AR(1) calculations; compounding uses the paper's explicit rounded 2% annual wedge assumption. Price impact from scaling or publishing is not fitted here. |
| $10,000 → about $15,800 / $21,600 / $39,000; roughly 70% split | `took_the_gross.py` | January 2024 to the pinned endpoint, selected retrospectively; simple 1x/2x/5x gearing excluding costs. The split uses a stated 6.2% continuous economy-growth assumption. These are not option valuations. |
| Correlated breadth illustration; log-level variance decomposition | `breadth_law.py`, `deflation.py` | Breadth/IC inputs are scenarios. R² and its complement describe historical log-price levels, not a probability of investment loss. |
| Ancient inequality and pre-1913 US tables | `inequality_maturity.py` | Two restored source-attributed transcriptions; their JSON files retain table/PDF references and the stated geographic/measurement limits. |

The four restored input snapshots are identified in
`data/ensemble/supporting_provenance.json`. Original retrieval times are not
invented where the retained files did not record them. Table transcriptions retain
their original source citations; the cited papers themselves are not bundled.

The retained numerical methods were made portable by removing machine-specific
imports and using pinned local inputs. Public labels replace internal working
notation. `reading_B` reports an unavailable combined reading when either required
component is missing, instead of treating that missing component as zero.

The retained `two_regimes.py`, `breadth_law.py` and `deflation.py` included broader
working commentary. Their public versions expose the relevant arithmetic and
its explicit inputs. In particular, the superseded inference from a high level-fit
R² to low investment risk is excluded, consistent with the paper's correction.
These scripts reproduce quantities; the paper carries their interpretation.
