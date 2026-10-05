"""Offence-rate parity, and the isolation of the Moreland/Merri-bek fix.

The offences extract is the only table the rename touches, which is itself
worth asserting: the fix changes a label in one source and no arithmetic
anywhere.
"""

from __future__ import annotations

import pandas as pd
from conftest import assert_matches, load_reference

from vichouse import naming
from vichouse.build_offences import TYPE_COLUMNS, build_offences_by_lga

VALUE_COLUMNS = TYPE_COLUMNS + ["Offence Rate"]
REFERENCE_FILE = "Offences By LGA NEW.csv"
YEARS = range(2016, 2021)


def _reference(renames_enabled: bool) -> pd.DataFrame:
    old = load_reference(REFERENCE_FILE)
    if renames_enabled:
        # The original output carries the post-2022 council name.
        old["LGA"] = old["LGA"].replace(naming.LGA_RENAMES)
    return old


def test_matches_original_exactly(renames_enabled):
    new = build_offences_by_lga()
    assert_matches(
        new,
        _reference(renames_enabled),
        ["LGA", "Year"],
        VALUE_COLUMNS,
        expected_rows=395,
    )


def test_rename_changes_a_label_and_nothing_else():
    """Build the table both ways and diff.

    If the fix were anything more than a rename, the affected rows' values
    would move. They must be identical.
    """
    original = naming.RENAMES_ENABLED
    try:
        naming.RENAMES_ENABLED = False
        before = build_offences_by_lga()
        naming.RENAMES_ENABLED = True
        after = build_offences_by_lga()
    finally:
        naming.RENAMES_ENABLED = original

    assert len(before) == len(after) == 395

    before_keys = set(map(tuple, before[["LGA", "Year"]].to_numpy()))
    after_keys = set(map(tuple, after[["LGA", "Year"]].to_numpy()))
    assert before_keys - after_keys == {("Merri-bek", y) for y in YEARS}
    assert after_keys - before_keys == {("Moreland", y) for y in YEARS}

    def values(df: pd.DataFrame, lga_filter) -> pd.DataFrame:
        subset = df[lga_filter(df["LGA"])].sort_values(["LGA", "Year"])
        return subset[["Year"] + VALUE_COLUMNS].reset_index(drop=True)

    # .equals() rather than a list comparison, because it treats NaN as equal
    # to NaN; a plain == would report a spurious difference.
    assert values(before, lambda s: s == "Merri-bek").equals(
        values(after, lambda s: s == "Moreland")
    ), "the renamed rows' values changed, so this is not purely a rename"

    assert values(before, lambda s: s != "Merri-bek").equals(
        values(after, lambda s: s != "Moreland")
    ), "rows unrelated to the rename changed"


def test_divisional_percentages_fall_short_of_100_by_division_f():
    """The five divisional shares deliberately do not sum to 100%.

    The Crime Statistics Agency publishes six offence divisions, A to F. The
    original project enumerated only A to E, omitting F ("other offences",
    1.70% of offences over this period), so the shares sum to less than 100%.

    That is reproduced rather than corrected, because these columns feed no
    model -- the submitted report found no signal in them and excluded them --
    and changing them would break parity with the published tables for no
    analytical gain. The test exists so the shortfall is a documented property
    rather than a surprise.
    """
    new = build_offences_by_lga()
    totals = new[TYPE_COLUMNS].sum(axis=1)
    assert totals.max() <= 100.1, "divisional shares exceed 100%"
    assert totals.min() > 80, "divisional shares fall implausibly short"
    assert (totals < 99.9).any(), (
        "every row sums to 100%, so division F is no longer being dropped -- "
        "the docstring above is now wrong"
    )
