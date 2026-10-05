"""Build every processed table from the raw sources.

Usage::

    python -m vichouse.pipeline
    python -m vichouse.pipeline --refresh-offence-cache
"""

from __future__ import annotations

import argparse

from . import config
from .build_dataset import build_modelling_dataset
from .build_egm import build_egm_by_lga, build_egm_wide
from .build_houses import build_houses_by_lga
from .build_offences import build_offences_by_lga


def run(refresh_offence_cache: bool = False) -> None:
    config.PROCESSED.mkdir(parents=True, exist_ok=True)

    tables = [
        ("houses", build_houses_by_lga(), config.HOUSES_BY_LGA_CSV),
        ("gambling (wide)", build_egm_wide(), config.EGM_BY_LGA_WIDE_CSV),
        ("gambling", build_egm_by_lga(), config.EGM_BY_LGA_CSV),
        (
            "offences",
            build_offences_by_lga(refresh=refresh_offence_cache),
            config.OFFENCES_BY_LGA_CSV,
        ),
    ]
    for label, frame, path in tables:
        frame.to_csv(path, index=False)
        print(f"  {label:16s} {len(frame):5d} rows -> {path.relative_to(config.ROOT)}")

    dataset = build_modelling_dataset()
    dataset.to_csv(config.MODELLING_DATASET_CSV, index=False)
    print(
        f"  {'modelling set':16s} {len(dataset):5d} rows -> "
        f"{config.MODELLING_DATASET_CSV.relative_to(config.ROOT)}"
    )
    print(
        f"\n{len(dataset)} rows: {dataset['LGA'].nunique()} LGAs x "
        f"{dataset['Year'].nunique()} years"
    )
    print("class balance:", dataset["Price Level"].value_counts().to_dict())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-offence-cache",
        action="store_true",
        help="rebuild the offences CSV cache from the 19.7 MB source workbook",
    )
    args = parser.parse_args()
    print("Building processed tables...")
    run(refresh_offence_cache=args.refresh_offence_cache)


if __name__ == "__main__":
    main()
