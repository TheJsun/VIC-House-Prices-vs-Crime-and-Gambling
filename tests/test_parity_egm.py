"""Gambling-loss parity, in both the wide and long layouts.

The sensitive part is the eleven composite reporting areas, whose dollars are
split between member LGAs in proportion to population. The original rounded
each split figure to the cent *before* dividing by population; dropping that
intermediate rounding shifts the 24 split LGAs in the second decimal, so this
test is what pins the behaviour down.
"""

from __future__ import annotations

from conftest import assert_matches, load_reference

from vichouse.build_egm import COMPOSITE_GROUPS, build_egm_by_lga, build_egm_wide

YEAR_COLUMNS = ["2019", "2018", "2017", "2016", "2020"]
RATE_COLUMNS = ["rate " + y for y in ["2020", "2019", "2018", "2017", "2016"]]


def test_wide_matches_original_exactly():
    new = build_egm_wide()
    old = load_reference("EGM-rate-2019.csv")
    assert_matches(new, old, ["LGA"], YEAR_COLUMNS + RATE_COLUMNS, expected_rows=70)


def test_long_matches_original_exactly():
    new = build_egm_by_lga()
    old = load_reference("EGM-New-Format.csv").rename(
        columns={"total dollars": "Total Loss On EGM", "rate": "EGM Rate"}
    )
    assert_matches(
        new,
        old,
        ["LGA", "Year"],
        ["Total Loss On EGM", "EGM Rate"],
        expected_rows=350,
    )


def test_composite_groups_cover_24_lgas():
    members = [lga for group in COMPOSITE_GROUPS.values() for lga in group]
    assert len(COMPOSITE_GROUPS) == 11
    assert len(members) == 24
    assert len(set(members)) == 24, "an LGA appears in two composite groups"


def test_split_group_members_share_a_rate_by_construction():
    """Document the artefact rather than let someone discover it later.

    Splitting a composite's dollars in proportion to population necessarily
    gives every member of that group the same loss per head. Whittlesea and
    Nillumbik are the pair that reaches the modelling dataset.
    """
    rates = build_egm_by_lga().set_index(["LGA", "Year"])["EGM Rate"]
    for year in range(2016, 2021):
        assert rates[("Whittlesea", year)] == rates[("Nillumbik", year)]
