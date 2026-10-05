"""Local Government Area name normalisation.

The three sources spell LGA names three different ways:

* ``communities.csv``  -- suffixed with a council type, e.g. ``Alpine (S)``
* ``EGM.csv``          -- prefixed, e.g. ``Shire of Alpine``
* ``LGA Offences.xlsx`` -- bare, but using *present-day* council names

The third is the one that caused a silent data loss in the original project.
Moreland City Council was renamed Merri-bek in September 2022. The Crime
Statistics Agency extract was downloaded in 2024 and so uses ``Merri-bek``,
while the house-price and gambling sources both still say ``Moreland``. The
three-way inner join therefore dropped that LGA entirely, giving 165 rows
across 33 LGAs instead of 170 across 34.

Normalisation goes *backwards* to the 2016-2020-era name, because that is the
period under study and the name two of the three sources already use.
"""

from __future__ import annotations

import pandas as pd

LGA_SUFFIXES = ("(RC)", "(C)", "(S)", "(B)")
LGA_PREFIXES = ("Shire of", "Rural City of", "City of")

LGA_RENAMES = {
    "Merri-bek": "Moreland",  # renamed 2022-09; the sole mismatch in this data
}

# Set to False to reproduce the original project's output exactly, including
# the dropped LGA. The parity suite uses this to prove the rebuilt pipeline is
# faithful *before* the fix is applied, so that the fix's effect is isolated.
RENAMES_ENABLED = False


def normalise_lga(names: pd.Series) -> pd.Series:
    """Strip council-type prefixes and suffixes, then apply known renames.

    Idempotent, so it is safe to apply at every source boundary.
    """
    out = names.str.strip()
    for suffix in LGA_SUFFIXES:
        out = out.str.removesuffix(suffix).str.strip()
    for prefix in LGA_PREFIXES:
        out = out.str.removeprefix(prefix).str.strip()
    if RENAMES_ENABLED:
        out = out.replace(LGA_RENAMES)
    return out
