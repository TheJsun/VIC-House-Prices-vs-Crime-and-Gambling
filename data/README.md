# Data

Three directories, three different jobs.

| Directory | What it holds | Written by |
|---|---|---|
| `raw/` | The four source datasets, byte-for-byte as supplied | Nothing — read only |
| `interim/` | A CSV cache of the one workbook sheet the pipeline uses | `vichouse.load` |
| `processed/` | The tables the notebooks model | `vichouse.pipeline` |

`processed/` is committed deliberately, so the outputs can be read on GitHub without running anything, and because regenerating them from the 19.7 MB workbook is slow.

## Sources and provenance

These four files were supplied as the dataset for COMP20008 Assignment 2 at the University of Melbourne in 2024. They are derived from Victorian Government open data; the publishers' own documentation is preserved verbatim alongside each file.

| File | Description | Documentation |
|---|---|---|
| `raw/Houses-by-suburb.csv` | Median house price per locality, 2013–2023. 786 localities. Missing values are encoded `-`. | `raw/README_Houses.txt` |
| `raw/EGM.csv` | Total annual electronic gaming machine losses in AUD per reporting area, 2011–2020. | `raw/README_EGM.txt` |
| `raw/LGA Offences.xlsx` | Offence counts and rates for Victorian Local Government Areas. Eight sheets; this project uses **Table 02** only. Compiled by the **Crime Statistics Agency (CSA) of Victoria**. | `raw/README_LGA Offences.txt` |
| `raw/communities.csv` | Community profiles for 1,080 Victorian communities, 226 columns. Supplies the suburb→LGA mapping and the only population figures available to the project. | `raw/README_Communities.txt` |

Because these were distributed as teaching materials rather than downloaded directly from a portal, this repository does not restate a licence for them. **They remain subject to their original publishers' terms.** If you intend to reuse the data rather than read this analysis, obtain it from the publishing agency. The MIT licence in this repository covers the code only.

### A note on the crime workbook

An earlier vintage of `LGA Offences.xlsx` (18.7 MB, dated 2024-09-06) was previously committed inside a `Data.zip` archive, which was removed during the 2025 rebuild. The two vintages are equivalent over the 2016–2020 study period — both give 26,594 rows and a total offence count of 2,635,567 — and differ only by one blank trailing row outside it. The copy in `raw/` is authoritative because it is the one that reproduces the original committed outputs byte-for-byte. The archive remains in git history.

## Known data limitations

These shape every result in the project and are discussed in the README.

- **Population is a 2012 estimate.** `communities.csv` provides estimated resident population for 2007 and 2012 only. The 2012 figure is used for every year from 2016 to 2020. The error is systematic rather than random, which is why it was preferred to imputation.
- **Population is derived, not given.** There is no population column; it is computed as `Population Density × Area (km²)`.
- **Two different population bases are in use.** LGA population totals — the denominator for gambling loss per head — sum over every community type. The house-price weighting uses only the 452 communities marked `(Suburb)`, because those are the ones with a counterpart in the house-price file. This asymmetry is inherited from the original project and preserved.
- **Eleven gambling reporting areas cover more than one council.** They are split in proportion to population, which gives every member of a group an identical loss *per head* by construction. Affected rows are flagged `EGM Split` in `processed/modelling_dataset.csv`.
- **Council names differ between sources.** The crime extract uses present-day names; the other two use the names of the study period. `vichouse.naming` normalises them. One such mismatch — Moreland, renamed Merri-bek in 2022 — silently removed a council from the original project's analysis.
- **Offence divisions A–E only.** The source has six divisions; the original project enumerated five, omitting F ("other offences", 1.70% of offences). Reproduced for parity. Those columns feed no model.

## Generated files

| File | Rows | Contents |
|---|---|---|
| `processed/houses_by_lga.csv` | 374 | Population-weighted median price, 34 LGAs × 2013–2023 |
| `processed/egm_by_lga.csv` | 350 | Total losses and loss per head, 70 LGAs × 2016–2020 |
| `processed/egm_by_lga_wide.csv` | 70 | The same, one row per LGA (matches the original layout) |
| `processed/offences_by_lga.csv` | 395 | Offence rate and divisional shares, 79 LGAs × 2016–2020 |
| `processed/modelling_dataset.csv` | **170** | The three-way inner join, 34 LGAs × 2016–2020, with price bands |
| `interim/offences_table02_2016_2020.csv` | 26,594 | Cached slice of the workbook, so a clone need never open it |

Rebuild all of them with `python -m vichouse.pipeline`.
