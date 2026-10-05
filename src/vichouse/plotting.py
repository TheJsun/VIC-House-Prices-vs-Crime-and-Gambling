"""One place for figure styling, so every chart in the project matches.

The original notebooks each set their own figure size and left the matplotlib
defaults otherwise, so the seven report figures ranged from 400x300 to
1200x1200 with three different font scales. Styling here rather than per
notebook is what makes the figure set look like one system.

Colour choices, and why they are not arbitrary:

* **Price bands use one hue, light to dark.** Low / Medium / High is ordered
  data, so three unrelated hues would throw away the ordering and imply the
  categories are merely different rather than ranked. A single-hue ordinal
  ramp encodes the order in the ink.
* **Genuinely categorical series use a fixed slot order**, never a cycled
  colour. The same entity keeps the same colour across every figure.
* **Baselines and reference lines are grey**, never a palette colour, so a
  reference can never be mistaken for a result.

Both ramps were checked with a palette validator rather than by eye: the
ordinal ramp passes monotone lightness, adjacent-lightness gaps and light-end
contrast against the surface; the categorical trio passes the lightness band,
chroma floor, colour-vision-deficiency separation and normal-vision floor on
all pairs. The aqua slot sits below 3:1 contrast on this surface, so figures
that use it carry direct labels rather than relying on the legend alone.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from .config import FIGURES

# --- surfaces and ink -----------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#8a8980"
GRID = "#e6e5e1"

# --- ordinal ramp: Low -> Medium -> High (one hue, light to dark) ---------
PRICE_COLOURS = {
    "Low": "#86b6ef",
    "Medium": "#2a78d6",
    "High": "#104281",
}

# --- categorical slots, assigned in this fixed order ----------------------
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
BLUE, ORANGE, AQUA = SERIES

# Reference lines, baselines and anything that is not a result.
REFERENCE = "#8a8980"

DPI = 150


def apply_style() -> None:
    """Set the project's matplotlib defaults. Call once per notebook."""
    mpl.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.dpi": 110,
            "savefig.dpi": DPI,
            "savefig.bbox": "tight",
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            # Recessive frame: keep the data, lose the box.
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": INK_MUTED,
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
            "axes.titlelocation": "left",
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
            "axes.titlecolor": INK,
            "axes.titlepad": 12,
            "axes.labelsize": 11,
            "axes.labelcolor": INK_SECONDARY,
            "text.color": INK,
            "xtick.color": INK_SECONDARY,
            "ytick.color": INK_SECONDARY,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "legend.frameon": False,
            "legend.fontsize": 10,
            "lines.linewidth": 2.0,
            "lines.markersize": 8,
            "font.size": 11,
            "axes.prop_cycle": mpl.cycler(color=SERIES),
        }
    )


def save_fig(fig: plt.Figure, name: str, directory: Path | None = None) -> Path:
    """Write a figure to ``figures/<name>.png`` and return the path."""
    target_dir = FIGURES if directory is None else directory
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / (name + ".png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
    return path


def price_palette(labels) -> list[str]:
    """Colours for a sequence of price-band labels, in the given order."""
    return [PRICE_COLOURS[label] for label in labels]


def annotate_baseline(ax, value: float, label: str, *, x: float = 0.99) -> None:
    """Draw a horizontal reference line with its own label.

    Used for the majority-class accuracy and the mean-predictor error, so that
    every accuracy chart shows what beating nothing looks like.
    """
    ax.axhline(value, color=REFERENCE, linestyle="--", linewidth=1.4, zorder=1)
    ax.text(
        x,
        value,
        " " + label,
        transform=ax.get_yaxis_transform(),
        ha="right",
        va="bottom",
        fontsize=9,
        color=INK_SECONDARY,
    )


def caption(fig: plt.Figure, text: str, *, y: float = -0.03, width: int = 104) -> None:
    """Place a wrapped caption under a figure.

    Wrapping is not cosmetic. ``savefig(bbox_inches="tight")`` expands the
    saved canvas to contain every artist, so a single long line of caption
    text stretches the image and leaves the plot stranded in one corner.
    """
    import textwrap

    wrapped = textwrap.fill(" ".join(text.split()), width=width)
    fig.text(0.0, y, wrapped, fontsize=9, color=INK_SECONDARY, va="top", ha="left")


def thousands(value: float, _pos=None) -> str:
    """Axis formatter: 1250000 -> '$1.25M'."""
    if abs(value) >= 1_000_000:
        return "$" + format(value / 1_000_000, ".2f").rstrip("0").rstrip(".") + "M"
    if abs(value) >= 1_000:
        return "$" + format(value / 1_000, ".0f") + "k"
    return "$" + format(value, ".0f")
