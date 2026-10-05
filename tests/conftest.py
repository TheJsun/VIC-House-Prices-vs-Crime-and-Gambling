"""Shared helpers for the parity suite.

The six CSVs in ``tests/reference/`` are the untouched outputs of the original
2024 pipeline, frozen before any refactoring began. They keep their original
filenames, spaces included, because they are historical artefacts rather than
pipeline outputs.

Every comparison here joins on keys rather than comparing row order. The
original scripts wrote rows year-major in first-appearance order; the rebuilt
builders sort by (LGA, Year). That difference is cosmetic and deliberate.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REFERENCE = Path(__file__).parent / "reference"

# The original values are rounded to the cent, so a faithful reimplementation
# can differ only by a float tie at the half-cent. A tolerance alone would let
# a refactor that was wrong everywhere by a cent pass, so the tests also cap
# how many rows may use the slack. Both halves matter.
CENT = 0.01
MAX_SLACK_ROWS = 3


def load_reference(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(REFERENCE / name, **kwargs)


def assert_matches(
    new: pd.DataFrame,
    old: pd.DataFrame,
    keys: list[str],
    columns: list[str],
    expected_rows: int,
) -> None:
    """Assert two tables agree on every value, joined on ``keys``."""
    merged = old.merge(
        new, on=keys, how="outer", suffixes=("_old", "_new"), indicator=True
    )
    unmatched = merged[merged["_merge"] != "both"]
    assert unmatched.empty, (
        str(len(unmatched))
        + " key(s) did not match:\n"
        + unmatched[keys + ["_merge"]].to_string(index=False)
    )
    assert len(merged) == expected_rows, (
        "expected " + str(expected_rows) + " rows, got " + str(len(merged))
    )

    for column in columns:
        old_values = merged[column + "_old"]
        new_values = merged[column + "_new"]

        # Checked before the numeric comparison, because NaN - NaN is NaN and
        # every comparison against NaN is False -- so a missing value on one
        # side would otherwise slip through the tolerance check unnoticed.
        # This caught a real gap: an LGA-year with no offences in one division
        # became NaN here where the original wrote 0.0.
        mismatched_nulls = old_values.isna() != new_values.isna()
        assert not mismatched_nulls.any(), (
            column
            + ": "
            + str(int(mismatched_nulls.sum()))
            + " row(s) null on one side only\n"
            + merged.loc[
                mismatched_nulls, keys + [column + "_old", column + "_new"]
            ].head(10).to_string(index=False)
        )

        diff = (old_values - new_values).abs()
        differing = int((diff > 0).sum())
        offenders = merged.loc[diff > CENT, keys + [column + "_old", column + "_new"]]
        assert diff.max() <= CENT, (
            column
            + ": max difference "
            + str(diff.max())
            + " exceeds one cent\n"
            + offenders.head(10).to_string(index=False)
        )
        assert differing <= MAX_SLACK_ROWS, (
            column
            + ": "
            + str(differing)
            + " rows differ by up to a cent -- too many to be float "
            "tie-breaking, so the arithmetic has changed"
        )


@pytest.fixture(scope="session")
def renames_enabled() -> bool:
    from vichouse import naming

    return naming.RENAMES_ENABLED
