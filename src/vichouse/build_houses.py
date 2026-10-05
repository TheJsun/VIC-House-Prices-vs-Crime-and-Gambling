"""Population-weighted median house price per LGA per year.

The source file gives a median price per *locality*; the analysis needs one
figure per *LGA*. The original project weighted each suburb's median by its
share of the LGA's population::

    price(LGA, year) = sum over suburbs s of  (pop_s / total_pop) * price_s

with the important detail that a suburb whose price is missing for that year
is excluded from both the numerator *and* the denominator, so the weights
always sum to one over the suburbs that actually contributed.

This module computes the algebraically identical ``sum(pop_s * price_s) /
sum(pop_s)``, which lets the whole thing be one groupby instead of the
original's triple-nested loop with repeated boolean-mask scans. Dividing once
rather than per term changes the floating-point result by ~1e-10 relative,
four orders of magnitude below the half-cent rounding applied at the end, so
the output is identical at 2dp. The parity suite asserts exactly that.

Caveat worth stating plainly: weighting by share of *population* is a proxy
for share of *housing stock*. The two diverge in newly built outer-suburban
areas, which is noted as a limitation in the README.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import YEARS_HOUSES
from .load import load_houses_by_suburb, load_suburbs


def build_houses_by_lga() -> pd.DataFrame:
    """Return LGA, Year, Weighted House Price for 2013-2023."""
    suburbs = load_suburbs()[["Community Name", "LGA", "Population"]].copy()
    suburbs["Community Name"] = suburbs["Community Name"].str.title().str.strip()

    prices = load_houses_by_suburb().copy()
    prices["Locality"] = prices["Locality"].str.title().str.strip()

    # Missing prices are encoded as '-'. The original replaced that token
    # across the whole frame; scoping it to the year columns is the correct
    # behaviour and is equivalent here (no locality is literally named '-').
    prices[YEARS_HOUSES] = (
        prices[YEARS_HOUSES].astype(str).replace("-", np.nan).astype(float)
    )

    # A merge cannot fan out and a global population lookup cannot pick the
    # wrong row only while these hold. They do hold for this data; asserting
    # means a future data refresh fails loudly instead of quietly skewing.
    assert not suburbs["Community Name"].duplicated().any(), "duplicate suburb name"
    assert not prices["Locality"].duplicated().any(), "duplicate locality"

    long = prices.melt(
        id_vars="Locality",
        value_vars=YEARS_HOUSES,
        var_name="Year",
        value_name="Median Price",
    )

    # inner merge == the original's `if s in all_suburbs`
    merged = suburbs.merge(
        long, left_on="Community Name", right_on="Locality", how="inner"
    )
    # dropna == the original's `and not math.isnan(...)`: drops the suburb
    # from the numerator and the denominator together.
    merged = merged.dropna(subset=["Median Price"])

    merged["weighted"] = merged["Population"] * merged["Median Price"]
    grouped = merged.groupby(["LGA", "Year"], as_index=False).agg(
        weighted=("weighted", "sum"), population=("Population", "sum")
    )

    assert (grouped["population"] > 0).all(), "LGA-year with no priced suburb"

    grouped["Weighted House Price"] = (
        grouped["weighted"] / grouped["population"]
    ).round(2)
    out = grouped[["LGA", "Year", "Weighted House Price"]].copy()

    expected = suburbs["LGA"].nunique() * len(YEARS_HOUSES)
    assert len(out) == expected, f"expected {expected} rows, got {len(out)}"
    return out.sort_values(["LGA", "Year"]).reset_index(drop=True)
