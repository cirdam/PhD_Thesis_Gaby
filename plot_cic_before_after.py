#!/usr/bin/env python3
"""Plot the SD-433 shower-size distribution before and after the CIC correction."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd


DEFAULT_INPUT = Path(
    "/home/pbrichetto/sd433/icrc-2025_test7/paper_dataset/cic/output/"
    "sd433_icrc2025-test7_hottest_cic_corrected.csv"
)
DEFAULT_OUTPUT = Path("figures/chapter_reconstruction/cic_before_after.pdf")
PLOT_STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")

ZENITH_MAX_DEG = 45.0
ZENITH_REF_DEG = 30.0
SIN2_ZENITH_REF = np.sin(np.deg2rad(ZENITH_REF_DEG)) ** 2
SIZE_REFERENCE = 40.0
FULL_EFFICIENCY_SIZE = 15.0
CIC_PARAMETERS = (-1.62941888, 0.26234832, -1.46224784, -0.44610276, 0.89544311)


def attenuation(zenith_deg: np.ndarray, corrected_size: float) -> np.ndarray:
    """Return the fitted SD-433 attenuation factor."""
    a0, a1, b0, b1, c0 = CIC_PARAMETERS
    x = np.sin(np.deg2rad(zenith_deg)) ** 2 - SIN2_ZENITH_REF
    y = np.log10(corrected_size / SIZE_REFERENCE)
    return 1.0 + (a0 + a1 * y) * x + (b0 + b1 * y) * x**2 + c0 * x**3


def reduced_sin2_to_deg(value):
    value = np.asarray(value)
    return np.rad2deg(np.arcsin(np.sqrt(np.clip(value + SIN2_ZENITH_REF, 0.0, 1.0))))


def deg_to_reduced_sin2(value):
    return np.sin(np.deg2rad(value)) ** 2 - SIN2_ZENITH_REF


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = pd.read_csv(
        args.input,
        usecols=["zenith_deg", "shower_size", "attenuated_size"],
    )
    events = events[
        (events["zenith_deg"] >= 0.0)
        & (events["zenith_deg"] < ZENITH_MAX_DEG)
        & (events["shower_size"] > 0.0)
        & (events["attenuated_size"] > 0.0)
    ]

    reduced_sin2_zenith = (
        np.sin(np.deg2rad(events["zenith_deg"].to_numpy())) ** 2 - SIN2_ZENITH_REF
    )
    log_size = np.log10(events["shower_size"].to_numpy())
    log_corrected_size = np.log10(events["attenuated_size"].to_numpy())

    x_edges = np.linspace(-SIN2_ZENITH_REF, deg_to_reduced_sin2(ZENITH_MAX_DEG), 31)
    y_edges = np.linspace(0.0, 2.3, 93)
    before, _, _ = np.histogram2d(reduced_sin2_zenith, log_size, bins=(x_edges, y_edges))
    after, _, _ = np.histogram2d(
        reduced_sin2_zenith,
        log_corrected_size,
        bins=(x_edges, y_edges),
    )
    maximum = max(before.max(), after.max())

    plt.style.use(PLOT_STYLE)
    figure, axes = plt.subplots(2, 1, figsize=(9.8, 10.0), sharex=True)
    figure.subplots_adjust(left=0.15, right=0.80, bottom=0.11, top=0.93, hspace=0.30)
    norm = LogNorm(vmin=1.0, vmax=maximum)
    mesh = None

    for axis, histogram, ylabel in (
        (axes[0], before, r"$\lg(S(300)/\mathrm{VEM})$"),
        (axes[1], after, r"$\lg(S_{30}/\mathrm{VEM})$"),
    ):
        mesh = axis.pcolormesh(
            x_edges,
            y_edges,
            np.ma.masked_where(histogram.T == 0, histogram.T),
            cmap="viridis_r",
            norm=norm,
            shading="flat",
            rasterized=True,
        )
        axis.set_ylabel(ylabel)
        axis.set_xlim(x_edges[0], x_edges[-1])
        axis.set_ylim(y_edges[0], y_edges[-1])
        secondary = axis.secondary_xaxis(
            "top",
            functions=(reduced_sin2_to_deg, deg_to_reduced_sin2),
        )
        secondary.set_xticks([0, 10, 20, 30, 40, 45])
        secondary.set_xlabel(r"$\theta/{}^\circ$")

    zenith_grid = np.linspace(0.0, ZENITH_MAX_DEG, 500)
    x_grid = deg_to_reduced_sin2(zenith_grid)
    observed_cut = FULL_EFFICIENCY_SIZE * attenuation(
        zenith_grid, FULL_EFFICIENCY_SIZE
    )
    axes[0].plot(x_grid, np.log10(observed_cut), color="black", linewidth=1.4)
    axes[1].axhline(
        np.log10(FULL_EFFICIENCY_SIZE),
        color="black",
        linestyle="--",
        linewidth=1.4,
    )
    axes[1].set_xlabel(r"$\sin^2\theta-\sin^2\theta_{\mathrm{ref}}$")

    colorbar_axis = figure.add_axes((0.84, 0.11, 0.035, 0.82))
    colorbar = figure.colorbar(mesh, cax=colorbar_axis)
    colorbar.set_label("Events per bin")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(figure)


if __name__ == "__main__":
    main()
