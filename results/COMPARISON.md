# 2024 submission vs. 2025 rebuild

Every difference between the published numbers and the rebuilt ones, with a
cause for each. Nothing here is a correction made quietly: the original figures
are preserved in `../report/ORIGINAL_RESULTS.md` and in `../tests/reference/`.

## How to read the two sets of numbers

The submitted report's correlation and RMSE figures are **in-sample fits** — the
models were scored on the data they were trained on. That is normal for an
introductory subject, and the numbers are correct for what they measure; they
measure *fit*, not *prediction*. This rebuild keeps every original number
verbatim for traceability and reports a held-out equivalent beside it. Where the
two disagree, **the held-out number is the one to believe**.

## 1. Differences that are exactly zero

The rebuilt pipeline reproduces the original preprocessing to the cent. This was
established before any analysis changed, with the dropped-council fix disabled,
and is asserted by `pytest` on every run.

| Output | Rows | Differing values |
|---|---|---|
| `Houses by LGA.csv` | 374 | **0** |
| `EGM-rate-2019.csv` | 70 | **0** |
| `EGM-New-Format.csv` | 350 | **0** |
| `Offences By LGA NEW.csv` | 395 | **0** |

The same applies to the regression tables, which are deterministic: all three
blocks of `LinReg.csv` reproduce to within 5 × 10⁻⁵ (`regression_reproduction_check.csv`).

Before that, the *original, unmodified* scripts were run on Python 3.13.7 with
pandas 2.3.3 and produced all four files byte-for-byte identically to the 2024
commits — so the environment itself is not a source of drift.

## 2. Differences with a known cause

### 2.1 The dataset grew by one council

| | 2024 | 2025 |
|---|---|---|
| Rows | 165 | **170** |
| Councils | 33 | **34** |
| Class balance | Low 32 / Medium 72 / High 61 | Low 32 / Medium **77** / High 61 |
| Majority baseline | 0.4364 | **0.4529** |
| 80/20 split | 132 / 33 | 136 / 34 |

**Cause.** Moreland City Council was renamed Merri-bek in September 2022. The
crime extract was downloaded in 2024 and uses the new name; the house-price and
gambling sources use the old one. The three-way inner join matched nothing for
that council and dropped it without warning. Moreland is Medium in all five
years, so it lands entirely in the majority class.

Verified to be a pure relabelling: the recovered rows are value-identical to the
old Merri-bek rows and no other row moves (`tests/test_parity_offences.py`).

### 2.2 The report's three regressions used two different samples

The gambling-only model was fitted on **170 rows / 34 councils**; the offence-only
and combined models on **165 / 33**. The gambling model is built from a
house-price-to-gambling join that never touches the offences table, so it never
encountered the name mismatch.

This is confirmed rather than inferred: the published coefficients reproduce
exactly only when the gambling model is given the 34-council sample
(`regression_reproduction_check.csv`). The practical consequence is that the
report's Table 6 compared three models that were not fitted on the same data.
The rebuild fits all three on the same 170 rows.

### 2.3 k-NN accuracies move by a few points

| Quantity | 2024 | 2025 reproduction |
|---|---|---|
| Best mean accuracy, row-wise | 0.66 (k = 13) | 0.6471 (k = 15) |
| Single-split headline | 0.7273 ("about 72%") | — not reproducible |

**Causes**, in order of size: the original set no seed anywhere, so the published
figures came from one unrepeatable draw; the rebuild stratifies its splits,
which the original did not; and the dataset is five rows larger. The 0.7273 was
the best of many unseeded runs and has no stable counterpart.

Nothing here is a disagreement about method — these are the same protocol, run
reproducibly.

### 2.4 Per-class performance is lower

| Class | 2024 precision / recall | 2025 held-out precision / recall |
|---|---|---|
| Low | 0.50 / 0.40 | 0.57 / 0.50 |
| Medium | 0.67 / 0.77 | 0.58 / 0.68 |
| High | 0.86 / 0.80 | 0.64 / 0.56 |

**Cause.** The 2024 figures come from one row-wise split, where councils appear
on both sides. The 2025 figures come from out-of-fold predictions with folds
grouped by council. The High class falls furthest, which is consistent with it
being the class most identifiable from a council's fixed characteristics.

## 3. Differences of judgement, not arithmetic

These are where the rebuild reaches a different conclusion from the same data.

### 3.1 The predictive claim does not survive grouped validation

| Model | Row-wise CV | Nested CV, grouped by council |
|---|---|---|
| Majority baseline | 0.4529 | 0.4529 |
| k-NN (unscaled) | 0.6471 | **0.5162** (95% CI 0.367–0.665) |
| k-NN (scaled) | 0.7621 | **0.4095** |
| Decision tree (pruned) | 0.6868 | **0.5095** |

The dataset is a panel: 34 councils × 5 years, in which 97% of the offence
rate's variance and 89% of the gambling rate's is *between* councils rather than
within one over time, and 25 of 34 councils never change price band. A row-wise
split therefore places about four near-copies of each test row into training.

Every grouped confidence interval contains the baseline. The report's conclusion
that "we have managed to generate a predictive relationship" is not supported
once councils are confined to one side of the split.

### 3.2 Scaling helps under the leaky protocol and hurts under the honest one

Not a correction of the report — it never tried scaling — but it explains the
report's own ablation table, which showed gambling alone at 0.4848 (near
baseline) while offences alone reached 0.6515. The two features differ roughly
20-fold in magnitude, so unscaled k-NN was close to a one-feature model.

That scaling *lowers* grouped accuracy (0.5162 → 0.4095) is further evidence of
the leak: a sharper two-feature fingerprint identifies a council more precisely,
which only helps when that council is also in the training set.

### 3.3 R² reframes the regression

| Model | Report | In-sample R² | Held-out R² |
|---|---|---|---|
| Gambling | r = 0.44178 | 0.1823 | 0.0128 |
| Offences | r = 0.02582 | 0.0002 | **−0.1929** |
| Both | r = 0.48408 | 0.2095 | 0.0281 |

A correlation of 0.484 and an R² of 0.21 describe the same fit. The second makes
plain that four fifths of the variation is unexplained. A negative held-out R²
means the model is worse than predicting the mean.

### 3.4 Significance, which the report could not report

The gambling coefficient is significant at p < 0.05 in **5 of 5 years**; the
offence coefficient in **0 of 5** (`regression_coefficients.csv`). This supports
the report's qualitative conclusion with the evidence it lacked.

### 3.5 The 2020 steepening is suggestive, not established

The report attributes a steeper 2020 gambling coefficient to COVID-19 venue
closures from 16 March 2020, which the source data's own footnote documents. The
rebuild agrees with the direction — the coefficient moves from −1,435 to −2,456,
a 71% change — but the 95% confidence intervals for 2016 and 2020 overlap at
n = 34 councils per year, so the steepening cannot be called established.

### 3.6 The Melbourne outlier is more informative than the report allowed

The report removed the City of Melbourne, observed that results "did not appear
to significantly alter", and moved on. Cook's distance shows Melbourne's five
observations are by far the most influential in the pooled fit, and removing it
flips the sign of the offence coefficient. The rebuild reads that as the finding:
the weak positive crime–price association in the full sample is a central
business district artefact, driven by counting offences against a daytime
population and dividing by residents.

### 3.7 K-means was abandoned for the right reason, stated wrongly

The original note read: *"Doesn't really make sense to apply K-means clustering,
as the y-axis is dependent on x."* The conclusion was correct. The mechanism was
not: house price and gambling loss differ in variance by about seven orders of
magnitude, so unscaled K-means clustered on price alone — the unscaled
clustering agrees with a price-only clustering at **ARI = 1.00**. Scaling fixes
that and does not rescue the method (silhouette 0.37), because the councils lie
along a continuum rather than in natural groups.

That strand also ran on a stale hand-made house-price file that disagreed with
the pipeline for 20 of 34 councils; it has been rebuilt on the real data.

## 4. Reproduced deliberately, including the flaw

- **Offence divisions A–E only.** The source has six; the original enumerated
  five, omitting F ("other offences", 1.70%). The divisional shares therefore sum
  to 86–100%, not 100%. Kept for parity; those columns feed no model.
- **The $600k / $1M price bands.** Domain-chosen rather than data-driven, and
  the $600k boundary falls where the price distribution is densest. Kept because
  the report's results are stated against them.
- **The 2012 population estimate for all years.** A systematic error, preferred
  by the original authors to an imputed one, and the rebuild agrees.
- **Composite gambling areas split by population.** Preserved, and now flagged in
  the data as `EGM Split` rather than left implicit.
