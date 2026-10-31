# The Veritocratic Economy

## Theory, accounting, and its relation to the Deliberate Line

Noah Davidson. Consolidated from the separate Veritocratic Economy publication,
October 2026. The theoretical rules are stated here; implementation and observed
economic performance are separate matters. This document does not report a
deployed tax, currency, or distribution service.

**Tax produced surplus and innovation rather than the person; return the pool as
a universal payment plus a payment for attributable contributions.**

The Deliberate Line describes the premium collected through maintained ownership
claims. This theory changes the entitlement to collection: receipts follow common
provision and contributions to realized growth, rather than a permanent ownership
percentage. The premium and its sustaining arrangements remain one operation;
the proposed alternative changes the rules of that operation.

## 1. What is measured

The tax base is new capacity received into shared use: produced surplus or
innovation with a recorded contribution to the commons. A person's existence,
hours, home, or human worth is not that base. Records must distinguish possession,
use, stewardship, productive contribution, and rights to payment.

Future claims and realized resources are different accounting objects. In the
source notation, `C_t` records claims against future growth, `G_t` realized growth,
and `q_t = max(0, C_t − G_t)` the uncovered amount. That subtraction requires
compatible units, valuation conventions, and settlement periods. A market index,
GDP, a dollar liability, and a contribution receipt cannot be substituted for one
another merely because each has a numerical value.

The three public constructions in `veritocratic_rate.py` compare:

- Growth of market claims with growth of realized output.
- Valuation-multiple expansion with corporate-margin expansion.
- Historical changes in the concentration of wealth.

Their periods, inputs, and disagreements are reported separately. They are
distinct constructions with shared inputs, not three statistically independent
estimates of an identical quantity. A growth-rate comparison is also distinct
from the amount of an uncovered claim or a measured dollar transfer.

## 2. The common-return pool

For one stated accounting interval, let:

- `S` be admitted produced surplus, valued under the published convention.
- `r` be the residual-growth reading for that interval, as a fraction.
- `tau = max(0, r)` be the collection rate under the proposed rule.
- `T = tau × S` be the common-return pool.

The source calls `r` residual inflation. It refers to claims outrunning realized
growth under the stated construction, not automatically the CPI inflation rate.
The interval and rate convention must accompany every calculation. The example
below uses a one-year interval and the paper's rounded annual log-growth premium
as the numerical rate specified by the rule.

The administrators publish the input reading, admitted surplus, rate, collected
amount, and recipients. Returning `T` reallocates that pool. If a proposal also
settles or retires future claims, its records must identify which obligations are
discharged. The distribution identity alone does not establish the cancellation
of `q`, a contraction of the money supply, or a particular inflation response.

## 3. One pool, two forms of return

Some receipts arise from inherited or indivisible common provision. Others have
attributable contributions. Let `T_common` and `T_attributed` be the portions of
the same pool assigned under those records:

```
T_common + T_attributed = T
B = T_common / N
A_i = w_i × T_attributed
sum_i w_i = 1                 when T_attributed > 0
U_i = B + A_i
sum_i U_i = T
```

`N` is the number of eligible people. Everyone receives the universal component
`B`; contribution payments do not determine anyone's universal standing. The
weights allocate the attributable portion, not the entire pool a second time.
No fixed universal/contribution percentage is inserted. The split follows the
recorded treatment of common and attributable receipts for that interval.

**Worked arithmetic:** with annual surplus `S = 1,000` and rate `tau = 0.023`,
the pool is `23`. If the recorded common portion is `9` for three people, each
receives `3` universally. The attributable portion is `14`. Weights `1/2, 1/2, 0`
produce total receipts `10, 10, 3`, summing to `23`. These are example inputs,
not prescribed economic shares. `common_return_accounting.py` reproduces the
example with exact rational arithmetic, before any currency-unit rounding.

## 4. Attribution without permanent ownership

Records preserve which contributions participated in realized growth. Payment
weights apply to the current interval and are reviewed when the contributing
relations or realized receipts change. A past attribution supplies provenance;
it does not confer a permanent percentage of later formations.

Joint contributions remain joint. Common or indivisible contributions feed the
common portion. Disputed or incomplete attribution stays explicitly identified;
administrators cannot silently turn it into an exclusive claim or an invented
contribution score. The public procedure must specify who verifies receipts,
how joint contributions are treated, and how disputes are resolved. Recorded
lineage supplies evidence for those decisions, not an automatic guarantee
against error or manipulation.

The accounting example accepts already supplied portions and weights. It checks
their conservation and validity; it does not infer causal contribution from data
or decide a dispute.

## 5. Administration without ownership of the pool

The people administering the arrangement can receive collectively authorized
claims, commission independent measurements, collect under the stated rule,
preserve records, and distribute the pool. They cannot retain the pool as their
property or certify all stages of their own decisions.

Claim authorization, measurement, allocation, payment, and review are separately
attributable operations. Public records expose disagreement and corrections.
The protections depend on those procedures and their actual operation; naming
them does not make capture or mistakes impossible.

## 6. What this adds to the economic argument

The theory distinguishes a return for a contribution to realized growth from a
continuing return based on ownership. It specifies the pool from which the
proposed payments come and keeps universal standing separate from contribution.
It also separates a buyer's benefit in an exchange from a later common-return
collection on admitted surplus; the latter is not an undisclosed sales markup.

The original diagnostic question and the proposed allocation rule remain
distinct. The institutional arrangements make claims collectible; identifying
how much of the measured above-output growth is a transfer additionally requires
the relevant income, ownership, valuation, and payment records. The allocation
rule does not retroactively turn every price increase into a measured transfer.

Changes in who receives income can affect consumption, investment, and demand.
Their direction and size depend on behavior, production constraints, policy,
and the settlement arrangements. The arithmetic here specifies the proposed
distribution; it does not estimate those macroeconomic responses.

## Source and consolidation

The source is Part II of *The Question and Its Answer* at former-repository
commit `700040f7d2d95fef4cb24ab82b9e82028ed4ca02`. The [original publication
snapshot](history/veritocratic-economy-700040f.zip) preserves that document and
the other six original files byte-for-byte. Its recorded DOI is retained as
source metadata in `SOURCE_CONSOLIDATION.json`. This repository is the
continuing home of the theory and the current Deliberate Line.

This consolidation replaces internal recurrence terminology with the operations
it described, distinguishes theory from deployment, and makes the common and
attributable subpools explicit. The source's expression `A_i = w_i × T` allocated
the entire pool to attribution while also adding universal payments. The form
above preserves both intended payments within `T`.

The older property/deed essay and project-governance draft are preserved in the
downloadable historical snapshot. Their legal and operational claims are not
assumptions of this accounting model. `SOURCE_CONSOLIDATION.json` identifies the
source documents, their original hashes, and their treatment.
