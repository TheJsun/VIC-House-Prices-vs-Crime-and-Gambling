"""Properties of the modelling dataset that every notebook relies on.

These are fast and version-independent: they do not compare against the
reference files, they just state what the joined table must look like. If one
of these fails, every result in the README is suspect.

The expected shape depends on whether the Moreland/Merri-bek fix is enabled,
and both cases are spelled out, which documents the effect of the fix as a
test rather than as a claim in prose.
"""

from __future__ import annotations

from vichouse.build_dataset import FEATURES, build_modelling_dataset
from vichouse.config import PRICE_HIGH, PRICE_LOW, YEARS_MODEL

# (rows, LGAs, class balance) with and without the dropped-LGA fix.
WITH_FIX = (170, 34, {"Medium": 77, "High": 61, "Low": 32})
WITHOUT_FIX = (165, 33, {"Medium": 72, "High": 61, "Low": 32})


def test_shape_and_class_balance(renames_enabled):
    expected_rows, expected_lgas, expected_balance = (
        WITH_FIX if renames_enabled else WITHOUT_FIX
    )
    df = build_modelling_dataset()

    assert len(df) == expected_rows
    assert df["LGA"].nunique() == expected_lgas
    assert df["Year"].nunique() == len(YEARS_MODEL)
    assert df["Price Level"].value_counts().to_dict() == expected_balance


def test_every_lga_appears_in_every_year():
    """Panel completeness.

    The grouped cross-validation in the notebooks splits by LGA, so an LGA
    missing a year would silently unbalance the folds.
    """
    df = build_modelling_dataset()
    counts = df["LGA"].value_counts()
    assert (counts == len(YEARS_MODEL)).all(), counts[counts != len(YEARS_MODEL)]


def test_no_missing_model_inputs():
    df = build_modelling_dataset()
    assert df[FEATURES + ["Weighted House Price"]].notna().all().all()
    assert df["Price Level"].notna().all()


def test_price_bands_follow_the_reported_boundaries():
    df = build_modelling_dataset()
    price = df["Weighted House Price"]
    assert (price[df["Price Level"] == "Low"] < PRICE_LOW).all()
    medium = df["Price Level"] == "Medium"
    assert (price[medium] >= PRICE_LOW).all()
    assert (price[medium] < PRICE_HIGH).all()
    assert (price[df["Price Level"] == "High"] >= PRICE_HIGH).all()


def test_composite_gambling_rows_are_flagged():
    """The collinear-by-construction rows must be identifiable, not hidden.

    Of the modelled LGAs, Whittlesea and Nillumbik share a gambling figure
    because they share a reporting area, and Greater Geelong was split against
    Queenscliffe, which does not reach the dataset.
    """
    df = build_modelling_dataset()
    flagged = set(df.loc[df["EGM Split"], "LGA"])
    assert {"Whittlesea", "Nillumbik", "Greater Geelong"} <= flagged
    assert df["EGM Split"].sum() == len(flagged) * len(YEARS_MODEL)
