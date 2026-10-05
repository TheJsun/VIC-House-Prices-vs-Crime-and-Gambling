"""The weighted house price refactor must reproduce the original to the cent.

This is the acid test of the whole rebuild. The original computed the
population-weighted median price with a triple-nested loop; the rebuild does it
with one groupby. The missing-data semantics are subtle -- a suburb with no
price in a given year leaves both the numerator and the denominator -- so an
exact match across all 374 rows is strong evidence they were preserved.

The Moreland/Merri-bek rename does not reach this table: the house-price source
already uses the 2016-2020-era council name.
"""

from __future__ import annotations

from conftest import assert_matches, load_reference

from vichouse.build_houses import build_houses_by_lga

COLUMN = "Weighted House Price"


def test_matches_original_exactly():
    new = build_houses_by_lga()
    old = load_reference("Houses by LGA.csv", dtype={"Year": str})
    assert_matches(new, old, ["LGA", "Year"], [COLUMN], expected_rows=374)


def test_shape_and_coverage():
    new = build_houses_by_lga()
    assert len(new) == 374, "34 LGAs x 11 years"
    assert new["LGA"].nunique() == 34
    assert new["Year"].nunique() == 11
    assert new[COLUMN].gt(0).all(), "a weighted price of zero means no priced suburb"
