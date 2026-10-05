"""Electronic gaming machine (EGM) losses per LGA, converted to spend per head.

Two wrinkles in the source data drive this module.

**Composite reporting areas.** The regulator reports eleven entries that each
cover more than one LGA -- ``CITY OF WHITTLESEA`` is actually Whittlesea plus
Nillumbik, and so on. The footnote rows at the bottom of ``data/raw/EGM.csv``
document all eleven. The original project split each composite's dollars
between its members in proportion to population, and that is preserved here.

It has a consequence worth stating loudly, because it is a limitation of the
*method* rather than a bug: splitting proportionally to population means every
member of a split group receives an **identical loss per head by
construction**. Of the 34 LGAs that survive into the model, Whittlesea and
Nillumbik are such a pair, so 10 of the 170 modelled rows are perfectly
collinear in this feature. ``build_dataset`` flags them.

**Casing as a schema.** The eleven composites are spelled in upper case and
the 46 single LGAs in title case. The original relied on this indirectly, via
hardcoded row slices (``egm.loc[:56]``, ``egm2016_2020.loc[11:]``) that only
worked while the file kept its exact row ordering. Testing the casing directly
is the same rule made explicit, and the assertions below turn a data refresh
that adds or renames a composite into an immediate failure rather than a
quietly wrong 69-LGA table.
"""

from __future__ import annotations

import pandas as pd

from .config import EGM_YEAR_ORDER
from .load import load_egm_raw, load_lga_populations

# The eleven composite reporting areas and the LGAs they cover, transcribed
# from the footnote rows of data/raw/EGM.csv. Order is preserved because it
# determines row order in the generated files.
COMPOSITE_GROUPS: dict[str, list[str]] = {
    "CITY OF WHITTLESEA": ["Whittlesea", "Nillumbik"],
    "SHIRE OF NORTHERN GRAMPIANS": ["Ararat", "Northern Grampians"],
    "CITY OF GREATER GEELONG": ["Queenscliffe", "Greater Geelong"],
    "SHIRE OF COLAC-OTWAY": ["Corangamite", "Colac-Otway"],
    "SHIRE OF MOORABOOL": ["Hepburn", "Moorabool"],
    "SHIRE OF CENTRAL GOLDFIELDS": ["Central Goldfields", "Mount Alexander"],
    "SHIRE OF MITCHELL": ["Mansfield", "Murrindindi", "Mitchell"],
    "SHIRE OF ALPINE": ["Towong", "Alpine"],
    "RURAL CITY OF BENALLA": ["Moira", "Strathbogie", "Benalla"],
    "SHIRE OF CAMPASPE": ["Gannawarra", "Campaspe"],
    "SHIRE OF GLENELG": ["Glenelg", "Southern Grampians"],
}

RATE_COLUMNS = [f"rate {year}" for year in ["2020", "2019", "2018", "2017", "2016"]]


def _population_lookup() -> pd.Series:
    return load_lga_populations().set_index("LGA")["Population"]


def build_egm_wide() -> pd.DataFrame:
    """Return one row per LGA with dollar losses and loss per head by year."""
    populations = _population_lookup()

    egm = load_egm_raw()

    # The file ends with blank rows and twelve footnote rows that document the
    # composite groups and the 2020 venue closures. Those carry prose in the
    # LGA column but no figures, so requiring a numeric value in every year
    # column is what separates data from commentary. The original instead used
    # the hardcoded slice egm.loc[:56].
    for year in EGM_YEAR_ORDER:
        egm[year] = pd.to_numeric(egm[year], errors="coerce")
    egm = egm[egm["LGA"].notna() & egm[EGM_YEAR_ORDER].notna().all(axis=1)].copy()
    assert len(egm) == 57, f"expected 57 LGA rows in EGM.csv, found {len(egm)}"

    is_composite = egm["LGA"].str.isupper()
    assert is_composite.sum() == len(COMPOSITE_GROUPS) == 11, (
        f"expected 11 composite reporting areas, found {is_composite.sum()}"
    )
    assert set(egm.loc[is_composite, "LGA"]) == set(COMPOSITE_GROUPS), (
        "composite reporting areas in EGM.csv do not match COMPOSITE_GROUPS"
    )

    columns = ["LGA", *EGM_YEAR_ORDER]
    singles = egm.loc[~is_composite, columns].copy()
    composites = egm.loc[is_composite, columns].set_index("LGA")

    split_rows = []
    for parent, children in COMPOSITE_GROUPS.items():
        group_population = populations.loc[children].sum()
        for child in children:
            share = populations.loc[child] / group_population
            row = {"LGA": child}
            for year in EGM_YEAR_ORDER:
                # The intermediate round() is required for parity: the
                # original rounded each split dollar figure to the cent
                # before dividing by population. Economically it is nil, but
                # dropping it shifts the 24 split LGAs in the second decimal.
                row[year] = round(composites.loc[parent, year] * share, 2)
            split_rows.append(row)

    assert len(split_rows) == 24, f"expected 24 split LGAs, got {len(split_rows)}"

    wide = pd.concat(
        [singles, pd.DataFrame(split_rows, columns=columns)], ignore_index=True
    )

    # Strip the council-type prefixes the single LGAs carry. Split rows are
    # already bare, so this is a no-op for them.
    for prefix in ("Shire of", "Rural City of", "City of"):
        wide["LGA"] = wide["LGA"].str.removeprefix(prefix).str.strip()

    for year in ["2020", "2019", "2018", "2017", "2016"]:
        wide[f"rate {year}"] = (
            wide[year] / wide["LGA"].map(populations)
        ).round(2)

    assert not wide["LGA"].duplicated().any(), "duplicate LGA after splitting"
    return wide.reset_index(drop=True)


def build_egm_by_lga() -> pd.DataFrame:
    """Long format: one row per LGA-year with total dollars and loss per head."""
    wide = build_egm_wide()

    dollars = wide.melt(
        id_vars="LGA",
        value_vars=EGM_YEAR_ORDER,
        var_name="Year",
        value_name="Total Loss On EGM",
    )
    rates = wide.melt(
        id_vars="LGA",
        value_vars=[f"rate {year}" for year in EGM_YEAR_ORDER],
        var_name="Year",
        value_name="EGM Rate",
    )
    rates["Year"] = rates["Year"].str.removeprefix("rate ")

    out = dollars.merge(rates, on=["LGA", "Year"], how="inner")
    out["Year"] = out["Year"].astype(int)

    expected = len(wide) * len(EGM_YEAR_ORDER)
    assert len(out) == expected, f"expected {expected} rows, got {len(out)}"
    assert out["EGM Rate"].notna().all(), "null EGM rate"
    return out.sort_values(["LGA", "Year"]).reset_index(drop=True)
