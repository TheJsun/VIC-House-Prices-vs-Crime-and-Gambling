"""Paths, constants and the single random seed.

Everything resolves from the repository root, which is derived from this
file's own location. The original scripts instead branched on
``platform.system()`` to choose between a Windows-style and a POSIX-style
spelling of every data path, and they used bare relative paths, so they only
worked when the interpreter happened to be launched from the repo root. A
``pathlib.Path`` works on both platforms unchanged, so the branch is gone.
"""

from pathlib import Path

# src/vichouse/config.py -> src/vichouse -> src -> repo root, hence parents[2].
ROOT = Path(__file__).resolve().parents[2]
assert (ROOT / "pyproject.toml").exists(), (
    f"Repository root misresolved to {ROOT}. If this file moved, the number "
    "of .parents[] levels above needs updating."
)

# --- directories -----------------------------------------------------------
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
REFERENCE = ROOT / "tests" / "reference"

# --- source files ----------------------------------------------------------
COMMUNITIES_CSV = RAW / "communities.csv"
EGM_CSV = RAW / "EGM.csv"
HOUSES_BY_SUBURB_CSV = RAW / "Houses-by-suburb.csv"
OFFENCES_XLSX = RAW / "LGA Offences.xlsx"

# Only one of the workbook's eight sheets is used. Table 02 is offences by
# type, LGA and Police Service Area: 53k rows, the finest grain that still
# carries an LGA-level rate per 100,000 population.
OFFENCES_SHEET = "Table 02"

# Reading the 19.7 MB workbook takes ~25 s, so the 2016-2020 slice is cached
# as CSV. The cache is committed, which means a fresh clone can run the whole
# pipeline without opening the workbook at all.
OFFENCES_CACHE = INTERIM / "offences_table02_2016_2020.csv"

# --- generated files -------------------------------------------------------
HOUSES_BY_LGA_CSV = PROCESSED / "houses_by_lga.csv"
EGM_BY_LGA_CSV = PROCESSED / "egm_by_lga.csv"
EGM_BY_LGA_WIDE_CSV = PROCESSED / "egm_by_lga_wide.csv"
OFFENCES_BY_LGA_CSV = PROCESSED / "offences_by_lga.csv"
MODELLING_DATASET_CSV = PROCESSED / "modelling_dataset.csv"

# --- analysis constants ----------------------------------------------------
SEED = 20008  # the subject code, so it is obviously arbitrary

# House-price columns in the raw file are strings; the join key in the
# generated tables is an int. Conflating the two yields a silently empty
# inner join, so the two lists are kept deliberately distinct.
YEARS_HOUSES = [str(y) for y in range(2013, 2024)]
YEARS_MODEL = list(range(2016, 2021))

# The year ordering the original EGM scripts used. It is not sorted, and it
# determines column and row order in the generated files, so it is preserved
# verbatim for parity.
EGM_YEAR_ORDER = ["2019", "2018", "2017", "2016", "2020"]

# Price bands from the submitted report: chosen on domain grounds (the
# Victorian market of the period) rather than from quantiles, and kept
# because the report's results are stated against them.
PRICE_LOW = 600_000
PRICE_HIGH = 1_000_000
PRICE_LABELS = ["Low", "Medium", "High"]

# Cross-validation / resampling settings.
K_RANGE = range(1, 21)
N_RESAMPLES = 100
CV_SPLITS = 5
CV_REPEATS = 20
TEST_FRACTION = 0.2
