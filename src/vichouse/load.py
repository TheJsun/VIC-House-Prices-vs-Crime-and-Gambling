"""Readers for the four raw sources.

These are cached *functions*, not module-level DataFrames. The original
``data.py`` read all four files -- including the 19.7 MB Excel workbook -- at
import time, so merely importing it cost ~25 seconds even if the caller only
wanted the house prices.
"""

from __future__ import annotations

import functools

import pandas as pd

from .config import (
    COMMUNITIES_CSV,
    EGM_CSV,
    HOUSES_BY_SUBURB_CSV,
    OFFENCES_CACHE,
    OFFENCES_SHEET,
    OFFENCES_XLSX,
)
from .naming import normalise_lga

# Columns kept from the offences workbook. Narrowing here is what makes the
# CSV cache ~1 MB instead of ~20 MB.
OFFENCE_COLUMNS = [
    "Year",
    "Local Government Area",
    "Offence Subdivision",
    "LGA Rate per 100,000 population",
    "Offence Count",
]


@functools.lru_cache(maxsize=1)
def load_egm_raw() -> pd.DataFrame:
    """Annual electronic gaming machine losses per LGA, 2011-2020, in AUD.

    The file carries footnote rows after the data, so callers must filter.
    """
    egm = pd.read_csv(EGM_CSV)
    return egm.rename(columns={"LGA Name": "LGA"})


@functools.lru_cache(maxsize=1)
def load_houses_by_suburb() -> pd.DataFrame:
    """Median house price per locality per year, 2013-2023. Missing = '-'."""
    return pd.read_csv(HOUSES_BY_SUBURB_CSV)


@functools.lru_cache(maxsize=1)
def load_communities() -> pd.DataFrame:
    """The 226-column community profile table (1,080 rows)."""
    return pd.read_csv(COMMUNITIES_CSV)


def _with_population(df: pd.DataFrame) -> pd.DataFrame:
    """Derive population and normalise the LGA column.

    ``communities.csv`` carries no population column. It has population
    density and area, so population is their product. This is the only
    population figure available anywhere in the project, and it is a 2012
    estimate -- see the limitations section of the README.
    """
    out = df[["Community Name", "LGA", "Population Density", "Area (km^2)"]].copy()
    out["Population"] = out["Population Density"] * out["Area (km^2)"]
    out["LGA"] = normalise_lga(out["LGA"])
    return out


@functools.lru_cache(maxsize=1)
def load_suburbs() -> pd.DataFrame:
    """The 452 communities that are suburbs, used to weight house prices.

    ``communities.csv`` mixes suburbs, towns and catchments. Only rows whose
    name ends in ``(Suburb)`` have a counterpart in the house-price file.
    """
    communities = load_communities()
    suburbs = communities.loc[
        communities["Community Name"].str.contains(r"\(Suburb\)$")
    ]
    suburbs = _with_population(suburbs)
    suburbs["Community Name"] = (
        suburbs["Community Name"].str.removesuffix("(Suburb)").str.strip()
    )
    return suburbs


@functools.lru_cache(maxsize=1)
def load_communities_summary() -> pd.DataFrame:
    """All 1,080 communities with population, for LGA population totals.

    Note the asymmetry with :func:`load_suburbs`, which is inherited from the
    original project and preserved deliberately: LGA *population totals* (used
    as the denominator for gambling spend per head) sum over every community
    type, whereas the house-price weighting uses suburbs alone. The two
    therefore rest on different population bases.
    """
    return _with_population(load_communities())


@functools.lru_cache(maxsize=1)
def load_lga_populations() -> pd.DataFrame:
    """Total population per LGA, summed over all community types."""
    return (
        load_communities_summary()
        .groupby("LGA", as_index=False)["Population"]
        .sum()
    )


@functools.lru_cache(maxsize=1)
def load_offences_table02(refresh: bool = False) -> pd.DataFrame:
    """Offence counts and rates by LGA, year and subdivision, 2016-2020.

    Reads the committed CSV cache when present. Pass ``refresh=True`` (or run
    the pipeline with ``--refresh-offence-cache``) to rebuild it from the
    workbook and prove the chain from the raw source.
    """
    if OFFENCES_CACHE.exists() and not refresh:
        return pd.read_csv(OFFENCES_CACHE)

    raw = pd.read_excel(OFFENCES_XLSX, sheet_name=OFFENCES_SHEET)
    sliced = raw.loc[raw["Year"].between(2016, 2020), OFFENCE_COLUMNS].copy()
    # The workbook's Year column reads as float because one trailing row has a
    # blank year. The slice above drops it; cast so the cache round-trips as int.
    sliced["Year"] = sliced["Year"].astype(int)
    OFFENCES_CACHE.parent.mkdir(parents=True, exist_ok=True)
    sliced.to_csv(OFFENCES_CACHE, index=False)
    return sliced
