"""Join the three processed tables into the modelling dataset.

The join is an inner join on (LGA, Year), so the result is limited to the LGAs
and years all three sources cover: 2016-2020, and the 34 LGAs whose suburbs
appear in the house-price file. The house-price table is the binding
constraint -- the offences table covers 79 LGAs and the gambling table 70.

This is where the original project lost an LGA. See :mod:`vichouse.naming`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .build_egm import COMPOSITE_GROUPS, build_egm_by_lga
from .build_houses import build_houses_by_lga
from .build_offences import build_offences_by_lga
from .config import PRICE_HIGH, PRICE_LABELS, PRICE_LOW, YEARS_MODEL

FEATURES = ["Offence Rate", "EGM Rate"]
TARGET = "Price Level"

# LGAs whose gambling figures came from splitting a composite reporting area.
# Within a group every member gets the same loss per head by construction, so
# these rows carry a known artefact rather than an independent measurement.
SPLIT_LGAS = {lga for members in COMPOSITE_GROUPS.values() for lga in members}


def add_price_level(df: pd.DataFrame) -> pd.DataFrame:
    """Band the weighted house price into Low / Medium / High.

    Boundaries are the report's: Low below $600k, Medium $600k to under $1M,
    High $1M and above. ``right=False`` reproduces the original's ``<`` /
    ``>= and <`` / ``>=`` comparisons exactly.
    """
    out = df.copy()
    out[TARGET] = pd.cut(
        out["Weighted House Price"],
        bins=[-np.inf, PRICE_LOW, PRICE_HIGH, np.inf],
        labels=PRICE_LABELS,
        right=False,
    )
    return out


def build_modelling_dataset() -> pd.DataFrame:
    """Return the joined, labelled dataset used by every model."""
    houses = build_houses_by_lga().copy()
    houses["Year"] = houses["Year"].astype(int)
    houses = houses[houses["Year"].isin(YEARS_MODEL)]

    offences = build_offences_by_lga()
    egm = build_egm_by_lga()

    df = houses.merge(offences, on=["LGA", "Year"], how="inner").merge(
        egm, on=["LGA", "Year"], how="inner"
    )
    df = add_price_level(df)
    df["EGM Split"] = df["LGA"].isin(SPLIT_LGAS)

    assert df["Year"].nunique() == len(YEARS_MODEL)
    assert df[FEATURES + ["Weighted House Price"]].notna().all().all()
    # Every LGA must appear in every year, or the grouped cross-validation
    # folds in the notebooks would be unbalanced without it being obvious.
    counts = df["LGA"].value_counts()
    assert (counts == len(YEARS_MODEL)).all(), "an LGA is missing a year"

    return df.sort_values(["LGA", "Year"]).reset_index(drop=True)
