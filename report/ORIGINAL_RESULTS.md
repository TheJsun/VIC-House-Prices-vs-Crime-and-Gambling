# The 2024 submission, transcribed

Every number the submitted report published, in machine-readable form, so the
rebuild's claims can be checked without opening the PDF.

**Source:** `COMP20008_A2-Report.pdf`, "On The Predictive Relationship of House
Prices from Criminal Offences and Gambling", COMP20008 Assignment 2, University
of Melbourne, 2024. Group W05G1: Emerson Leishman, Jason Jiang, Benedict Yong,
Zhengrong Yan.

Nothing here is corrected or re-expressed. Where a figure is wrong or
incomparable, it is transcribed as published and the problem is noted beneath.

## Setup as reported

- Python 3.12.6 (Anaconda); pandas, scikit-learn, matplotlib, seaborn, NumPy, SciPy.
- 165 rows: 33 LGAs × 5 years, 2016–2020.
- Price bands: Low < $600,000; Medium $600,000–$1,000,000; High > $1,000,000.
- Class balance: Low 32, Medium 72, High 61.
- Population: the 2012 estimate used for all years.

## k-nearest neighbours

Cross-validation described as five equal partitions giving 132 training and 33
test rows; for each k, 100 repeated random splits, averaged.

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| mean accuracy | 0.59 | 0.56 | 0.61 | 0.61 | 0.62 | 0.62 | 0.61 | 0.61 | 0.63 | 0.63 |

| k | 11 | 12 | **13** | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| mean accuracy | 0.65 | 0.64 | **0.66** | 0.63 | 0.64 | 0.65 | 0.64 | 0.62 | 0.64 | 0.63 |

Best mean **0.66 at k = 13**. A single split at k = 13 gave **0.7273**, quoted in
the report as "about 72%".

> No seed was set, so neither figure is reproducible. The splits were row-wise
> on panel data, so both are inflated — see the README.

### Per-class performance (report Table 2)

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Low | 0.50 | 0.40 | 0.44 |
| Medium | 0.67 | 0.77 | 0.72 |
| High | 0.86 | 0.80 | 0.83 |

> Computed by hand from a confusion matrix on one row-wise split. The rebuild's
> equivalent, from out-of-fold predictions under council-grouped folds, is in
> `results/classification_report.csv`.

### Feature ablations and alternative splits

Reported across the project's notebooks rather than in the report body.

| Variant | Accuracy |
|---|---|
| k = 3, train 2016–18, test 2019–20, both features | 0.6818 |
| k = 3, gambling rate only | 0.4848 |
| k = 3, offence rate only | 0.6515 |
| k = 3, train 2016/18/19, test 2017/20 | 0.6970 |
| k = 3, thresholds derived from the training set only | 0.5455 |
| Decision tree (entropy), train 2016–18, test 2019–20 | **0.7424** |

> Two things stand out. Gambling alone scores near the majority baseline while
> offences alone nearly matches both features together — the signature of
> unscaled features in a distance-based model. And the decision tree was the
> best model in the project but does not appear in the report.

## Linear regression

Per-year ordinary least squares, fitted and scored on the same rows. The
"Pearson Correlation" column is `pearsonr(y_true, y_pred)` on that in-sample
fit. Transcribed from `tests/reference/LinReg.csv`, which matches the report's
Tables 3–5.

### House price ~ gambling loss per head

| Year | Intercept | Coefficient | RMSE | Pearson r |
|---|---|---|---|---|
| 2016 | 1,465,002.44 | −1,229.5951 | 443,205.63 | 0.3990 |
| 2017 | 1,644,587.99 | −1,374.5316 | 471,807.64 | 0.4096 |
| 2018 | 1,626,196.60 | −1,309.0945 | 434,346.58 | 0.4338 |
| 2019 | 1,593,236.36 | −1,329.1603 | 408,780.71 | 0.4650 |
| 2020 | 1,764,659.13 | −2,116.5355 | 432,004.39 | 0.5015 |

### House price ~ offence rate

| Year | Intercept | Coefficient | RMSE | Pearson r |
|---|---|---|---|---|
| 2016 | 900,374.75 | 0.4475 | 490,366.47 | 0.0037 |
| 2017 | 999,089.02 | 2.5567 | 524,759.86 | 0.0177 |
| 2018 | 976,502.06 | 4.7228 | 488,827.22 | 0.0347 |
| 2019 | 947,774.90 | 3.1560 | 468,318.72 | 0.0227 |
| 2020 | 977,778.44 | 7.4824 | 506,083.48 | 0.0503 |

### House price ~ both

| Year | Intercept | Gambling coef. | Offence coef. | RMSE | Pearson r |
|---|---|---|---|---|---|
| 2016 | 1,373,109.46 | −1,445.1124 | 21.8800 | 441,674.48 | 0.4344 |
| 2017 | 1,542,513.80 | −1,606.4953 | 26.8747 | 469,376.52 | 0.4474 |
| 2018 | 1,516,451.02 | −1,533.0064 | 28.2049 | 429,582.18 | 0.4782 |
| 2019 | 1,468,316.46 | −1,536.4651 | 28.2069 | 404,053.22 | 0.5060 |
| 2020 | 1,599,430.11 | −2,475.3336 | 36.1605 | 421,706.66 | 0.5544 |

### Summary (report Table 6)

| Model | Average RMSE | Average Pearson r |
|---|---|---|
| House price ~ gambling | 438,028.9899 | 0.44178 |
| House price ~ offences | 495,671.1484 | 0.02582 |
| House price ~ both | 433,278.6118 | 0.48408 |

> **These three rows are not like-for-like.** The rebuild established, by
> reproducing each block exactly, that the gambling model was fitted on 170 rows
> across 34 councils while the other two used 165 across 33. The gambling model
> never touched the offences table, so it never hit the council-name mismatch
> that removed Moreland from the others. See `results/regression_reproduction_check.csv`.
>
> No R², standard errors, p-values or baseline were reported, so there was no
> way to judge whether a coefficient was distinguishable from zero. The report
> interpreted the correlations against a scale from lecture material: 0.5 large,
> 0.3–0.5 moderate, 0.1–0.3 small, below 0.1 trivial.

### Outlier sensitivity

The report refits with the City of Melbourne removed and concludes the change
"did not appear to significantly alter the regression models or the Pearson
Correlation enough to change the discussion". With Melbourne removed the
gambling correlation rises to 0.454–0.553 by year, and the **offence coefficient
changes sign** to negative.

> The sign change is the more interesting result, and the rebuild reads it
> differently: the weak positive crime–price association in the full sample is
> produced entirely by the central business district.

## Conclusions as written

> "Our report has identified a moderate correlation between the EGM data and
> that of house prices, while little to no correlation has been identified
> between house prices and Criminal Offences. From this, we have managed to
> generate a predictive relationship by using the K-nn algorithm with the highest
> accuracy of 72%. […] This data suggests that gambling as a problem is most
> prevalent in areas with lower house prices, and so government interventions
> such as anti-gambling messages and gambling support groups will be put to best
> use if established in these areas."

The report is careful to add that correlation is not causation and that income
may be a common cause.

> The descriptive half of this conclusion survives the rebuild and is now
> supported by significance testing it lacked. The predictive half does not: the
> 72% was obtained from a row-wise split of panel data, and under
> council-grouped cross-validation the models are not distinguishable from the
> majority-class baseline.

## Limitations the report itself raised

Transcribed because they were largely correct, and several are retained in the
rebuild's own limitations section.

1. Crime per resident misstates areas with large commuter inflows (City of Melbourne).
2. Population is a 2012 estimate applied to later years; imputation was rejected as introducing random error.
3. Only 165 rows, vulnerable to outliers; small rural LGAs distort crime rates.
4. Gambling covers electronic gaming machines only, excluding casinos and racing.
5. Only total crime was analysed, not severity or division.
6. Population share is a proxy for housing-stock share, biased in newly built areas.
7. The $600k/$1M boundaries are approximate, and the skewed distribution compresses the Low/Medium gap — offered as the explanation for poor Low-class performance.

> Limitation 3 understates the problem: the binding constraint is not 165 rows
> but 33 independent councils. That distinction is what the rebuild acts on.
