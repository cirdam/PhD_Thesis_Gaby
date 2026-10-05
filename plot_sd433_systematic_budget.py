#!/usr/bin/env python3
"""Plot the SD-433 unfolding and total flux-systematic budgets."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_RESULTS = Path(
    "/home/pbrichetto/phd_thesis/other_systematics_icrc2025_test7_omega005"
)
DEFAULT_OUTPUT = Path(
    "figures/chapter_spectrum/sd433_systematic_budget.pdf"
)
DEFAULT_STYLE = Path(
    "/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--style", type=Path, default=DEFAULT_STYLE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plt.style.use(args.style)

    total = pd.read_csv(args.results / "total_systematic.csv")
    unfolding = pd.read_csv(args.results / "unfolding_systematic_combined.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharex=True)

    ax = axes[0]
    ax.plot(unfolding.lg_energy, unfolding.bias_rms, "--", color="tab:red", label="Bias")
    ax.plot(unfolding.lg_energy, -unfolding.bias_rms, "--", color="tab:red")
    ax.plot(
        unfolding.lg_energy,
        unfolding.resolution_rms,
        "-.",
        color="tab:purple",
        label="Resolution",
    )
    ax.plot(unfolding.lg_energy, -unfolding.resolution_rms, "-.", color="tab:purple")
    ax.plot(
        unfolding.lg_energy,
        unfolding.efficiency_rms,
        ":",
        color="tab:green",
        label="Efficiency",
    )
    ax.plot(unfolding.lg_energy, -unfolding.efficiency_rms, ":", color="tab:green")
    ax.plot(unfolding.lg_energy, unfolding.combined_rms, color="black", label="Combined")
    ax.plot(unfolding.lg_energy, -unfolding.combined_rms, color="black")
    ax.axhline(0, color="0.65", linewidth=0.8)
    ax.set_ylabel(r"$\Delta J/J$")
    ax.set_ylim(-0.06, 0.06)
    ax.set_yticks(np.arange(-0.06, 0.061, 0.02))
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    ax.legend(frameon=False, fontsize=10, ncol=2, loc="upper center")

    ax = axes[1]
    ax.plot(
        total.lg_energy,
        total.energy_scale_plus,
        "--",
        color="tab:red",
        label="FD energy scale",
    )
    ax.plot(total.lg_energy, total.energy_scale_minus, "--", color="tab:red")
    ax.plot(
        total.lg_energy,
        total.calibration_rms,
        "-.",
        color="tab:orange",
        label="Calibration",
    )
    ax.plot(total.lg_energy, -total.calibration_rms, "-.", color="tab:orange")
    ax.plot(
        total.lg_energy,
        total.unfolding_rms,
        ":",
        color="tab:blue",
        label="Unfolding",
    )
    ax.plot(total.lg_energy, -total.unfolding_rms, ":", color="tab:blue")
    ax.plot(
        total.lg_energy,
        total.exposure,
        color="0.5",
        linestyle=(0, (3, 1, 1, 1)),
        label="Exposure",
    )
    ax.plot(
        total.lg_energy,
        -total.exposure,
        color="0.5",
        linestyle=(0, (3, 1, 1, 1)),
    )
    ax.plot(total.lg_energy, total.total_plus, color="black", label="Total")
    ax.plot(total.lg_energy, total.total_minus, color="black")
    ax.axhline(0, color="0.65", linewidth=0.8)
    ax.legend(frameon=False, fontsize=10, ncol=2, loc="upper center")

    for ax in axes:
        ax.set_xlabel(r"$\lg(E/\mathrm{eV})$")
        ax.set_xlim(16.8, 18.5)

    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight", pad_inches=0)
    fig.savefig(args.output.with_suffix(".png"), dpi=250, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


if __name__ == "__main__":
    main()
