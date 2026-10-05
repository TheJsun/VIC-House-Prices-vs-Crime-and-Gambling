# Results

Every number quoted in the top-level README traces to a file here, and every
file here is written by a notebook that runs top to bottom. Nothing is typed in
by hand.

`COMPARISON.md` is the reconciliation between these figures and the 2024
submission.

## Where each claim comes from

| Claim in the README | File | Column |
|---|---|---|
| 170 rows, 34 councils, class balance | `eda_summary.csv` | `rows`, `lgas`, `class_*` |
| Majority baseline 0.4529 | `eda_summary.csv` | `majority_class_share` |
| 97% / 89% of variance is between councils | `eda_summary.csv` | `between_lga_variance_*` |
| 25 of 34 councils never change band | `eda_summary.csv` | `lgas_with_constant_label` |
| k-NN 0.6471 row-wise, 0.5162 grouped | `model_comparison.csv` | `Row-wise CV (leaky)`, `Grouped CV (honest)` |
| Confidence intervals contain the baseline | `model_comparison.csv` | `Grouped CV CI low` / `CI high` |
| Accuracy by k, all three protocols | `knn_k_sweep.csv` | `rowwise_cv_mean`, `grouped_cv_mean` |
| Per-class precision / recall / F1 | `classification_report.csv` | all |
| The report's ablations, reproduced | `knn_variants.csv` | `Accuracy` |
| In-sample vs held-out R², RMSE, MAE | `regression_summary.csv` | all |
| Gambling significant 5/5, offences 0/5 | `regression_coefficients.csv` | `p-value` |
| Gambling coefficient −1,435 → −2,456 | `regression_coefficients.csv` | `Coefficient`, `CI low`, `CI high` |
| The report's regressions reproduce exactly | `regression_reproduction_check.csv` | `Max * difference` |
| Melbourne flips the offence coefficient | `regression_outlier_sensitivity.csv` | `Offence coefficient` |
| K-means ARI 1.00 vs price-only | `kmeans_agreement.csv` | `ARI vs price-only clustering` |
| Silhouette by k, scaled and unscaled | `kmeans_selection.csv` | `silhouette` |

## Which notebook writes what

| Notebook | Writes |
|---|---|
| `01_eda.ipynb` | `eda_summary.csv` |
| `02_classification_knn_tree.ipynb` | `knn_k_sweep.csv`, `model_comparison.csv`, `classification_report.csv`, `knn_variants.csv` |
| `03_regression.ipynb` | `regression_reproduction_check.csv`, `regression_summary.csv`, `regression_coefficients.csv`, `regression_outlier_sensitivity.csv` |
| `04_kmeans.ipynb` | `kmeans_selection.csv`, `kmeans_agreement.csv` |

## Reading the three evaluation protocols

Three numbers appear for most models, and they are not interchangeable.

**Resample** — repeated random row-wise splits. What the original project did,
reproduced here with a seed. Leaks by council.

**Row-wise CV** — repeated stratified k-fold. The standard form of the same
idea: every row is tested once per repeat, class balance preserved in each fold.
Still leaks by council.

**Grouped CV** — folds grouped by council, so a council is in training or in
testing but never both, with the hyperparameter chosen inside each outer fold so
model selection cannot inflate the score. **This is the one to believe.**

The gap between the second and third is the cost of the leak. For k-NN it is
about 13 accuracy points.

## A note on the standard deviations

The grouped figures carry a standard deviation around 0.10–0.17 across five
outer folds. That is not noise to be averaged away — it is the honest precision
available from 34 independent units. It is why the README says the models are
not distinguishable from the baseline rather than that they are worse than it.
