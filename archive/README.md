# Archive

The original 2024 project as it was submitted: seven preprocessing scripts and
thirteen notebooks, flat in the repository root. Everything here is superseded,
and nothing here is run by the current pipeline.

It is kept rather than deleted because the rebuild makes claims about what the
original did — that it dropped a council, that it never scaled its features,
that it split rows at random — and those claims should be checkable against the
code that made them rather than taken on trust.

**Do not run these scripts from the repository root.** Each calls `to_csv()`
with a bare relative filename, so running one drops its output into whatever the
current directory happens to be. That is the hazard that made freezing
`tests/reference/` the first commit of the rebuild. The filenames involved are
listed in `.gitignore` as a second line of defence.

## `original_scripts/`

| File | What it did | Superseded by |
|---|---|---|
| `data.py` | Shared loader. Read all four sources at import time, including the 19.7 MB workbook, so importing it cost ~25 s. Branched on `platform.system()` to choose a path separator. | `src/vichouse/load.py`, `config.py` |
| `houses_by_lga.py` | Population-weighted median house price per LGA. A triple-nested loop with repeated boolean-mask scans, growing a DataFrame one row at a time. | `src/vichouse/build_houses.py` |
| `EGM_by_lga.py` | Split the eleven composite gambling reporting areas. 24 hand-written `DataFrame._append` calls, and two hardcoded row slices (`.loc[:56]`, `.loc[11:]`) that only worked while the source file kept its exact row ordering. | `src/vichouse/build_egm.py` |
| `EGM_by_years.py` | Reshaped the gambling table from wide to long. | `src/vichouse/build_egm.py` |
| `lga_offencesNew.py` | Offence rates and divisional shares per LGA-year. Carried a stale comment claiming all years held identical data, which was no longer true of its own committed output. | `src/vichouse/build_offences.py` |
| `Houses by LGA 2019.csv` | A hand-made file with no script behind it. It disagrees with the pipeline's own house prices for **20 of 34 councils** — the City of Melbourne by 77%, Melton by 38% — because it came from an earlier version of the builder that divided by each council's *full* population while summing only the suburbs that had a recorded price. The K-means notebook read this file, so that strand ran on different numbers from every other model in the project. | `data/processed/houses_by_lga.csv` |
| `Offences By LGA.csv` | Output of `lga_offences.py` (deleted): the same offence figures in a wide, one-row-per-LGA layout, with five copy-pasted per-year blocks behind it. | `data/processed/offences_by_lga.csv` |

Two files from the original were deleted outright rather than archived:
`main.py`, which contained two comments and no code, and `lga_offences.py`,
whose 134 lines of copy-pasted per-year blocks were replaced by the 37-line
looped `lga_offencesNew.py` by the original authors themselves. Both remain in
git history.

## `notebooks/`

Outputs are stripped from these. Their code is largely duplicated from the
canonical notebooks, so the outputs were the bulk of their size, and the
authoritative record of the original results is kept in two better places:
`report/COMP20008_A2-Report.pdf` and `report/ORIGINAL_RESULTS.md`.

| File | What it was | Superseded by |
|---|---|---|
| `Ben_2.ipynb` | Earliest regression draft, working on single-year files | `notebooks/03_regression.ipynb` |
| `Ben_3.ipynb` | Near-duplicate of the canonical regression notebook, plus a year-print cell | `notebooks/03_regression.ipynb` |
| `Ben_4.ipynb` | As above, plus a stacked-model cell whose loop printed the same year five times | `notebooks/03_regression.ipynb` |
| `Ben_RO.ipynb` | The regression refitted with the City of Melbourne removed | Section 3.5 of `notebooks/03_regression.ipynb`, now with Cook's distance behind the decision |
| `Zhengrong2.ipynb` | k-NN with per-year quantile thresholds | Section 2.7 of `notebooks/02_classification_knn_tree.ipynb` |
| `Zhengrong3.ipynb` | k-NN with thresholds derived from the training set only — the most methodologically careful of the originals, and the lowest-scoring at 0.5455 | Section 2.7 of `notebooks/02_classification_knn_tree.ipynb` |
| `pop_est_err.ipynb` | Linear vs exponential population extrapolation | Section 1.5 of `notebooks/01_eda.ipynb` |
| `Report.ipynb` | An unexecuted skeleton of the written report, with the marking rubric in cell 0 | `report/COMP20008_A2-Report.pdf` |
| `log.ipynb` | The team's working log, dated 17 September 2024 | — |

Four original notebooks are not here because they became the canonical four:
`Zhengrong.ipynb` → `01_eda.ipynb`, `knn.ipynb` →
`02_classification_knn_tree.ipynb`, `Ben.ipynb` → `03_regression.ipynb`,
`Jason.ipynb` → `04_kmeans.ipynb`. Their history is reachable with
`git log --follow`.

## Things a reader might go looking for

- **`supervised_test.csv` does not exist and never did.** It is referenced 21
  times across the `Ben_*` notebooks, and every single reference is commented
  out. Nothing is missing.
- **The decision tree scoring 0.7424** lives in `Zhengrong.ipynb`, which is now
  `notebooks/01_eda.ipynb`; the tree itself moved to notebook 02. It was the
  best number anywhere in the original project and did not appear in the report.
  It was an unpruned tree on a single split; under cross-validation grouped by
  council it scores 0.5095.
- **An `OrdinalEncoder` applied to continuous features** appears in the original
  `Zhengrong.ipynb`, converting the two rates into rank indices 0–164 before
  fitting a tree. A later cell fits the same tree on the raw rates; that is the
  one the rebuild keeps.
