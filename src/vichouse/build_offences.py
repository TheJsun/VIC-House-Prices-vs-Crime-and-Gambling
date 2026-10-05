"""Criminal offence rates per LGA per year, from the Crime Statistics Agency.

Two definitions here are not self-evident and are worth stating, because both
look like mistakes until explained.

**Offence Rate is a sum of rates.** The source gives one row per offence
subdivision with its own ``LGA Rate per 100,000 population``. Adding those
rates is valid because the CSA publishes every subdivision's rate against the
same LGA population denominator, so the sum reconstructs the LGA's total
offence rate per 100,000 residents. It is not an average of averages.

**Offence type is the first character of the subdivision code.** CSA
subdivision codes are of the form ``A20``, ``B30`` and so on, where the letter
is the offence *division*: A crimes against the person, B property and deception
offences, C drug offences, D public order and security offences, E justice
procedures offences. Taking ``[0]`` recovers the division.

The divisional percentage breakdown is computed and kept because the original
project computed it, but the submitted report found it carried no useful signal
and excluded it from the modelling. It is retained for completeness, not used.
"""

from __future__ import annotations

import pandas as pd

from .load import load_offences_table02
from .naming import normalise_lga

TYPE_CODES = ["A", "B", "C", "D", "E"]
TYPE_COLUMNS = [f"Type {code} Percentage" for code in TYPE_CODES]


def build_offences_by_lga(refresh: bool = False) -> pd.DataFrame:
    """Return LGA, Year, the five divisional percentages, and Offence Rate."""
    offences = load_offences_table02(refresh=refresh).copy()

    # The only place the Moreland / Merri-bek rename is applied. The other two
    # sources already use the 2016-2020-era name.
    offences["LGA"] = normalise_lga(offences["Local Government Area"])
    offences["Code"] = offences["Offence Subdivision"].str[0]

    by_lga_year = offences.groupby(["LGA", "Year"])
    rate = (
        by_lga_year["LGA Rate per 100,000 population"]
        .sum()
        .round(2)
        .rename("Offence Rate")
    )
    total_count = by_lga_year["Offence Count"].sum()

    share = (
        offences.groupby(["LGA", "Year", "Code"])["Offence Count"]
        .sum()
        .unstack("Code")
        .reindex(columns=TYPE_CODES)
        .div(total_count, axis=0)
        .mul(100)
        .round(2)
    )
    share.columns = TYPE_COLUMNS

    out = share.join(rate).reset_index()
    assert out["Offence Rate"].notna().all(), "null offence rate"
    return out.sort_values(["LGA", "Year"]).reset_index(drop=True)
