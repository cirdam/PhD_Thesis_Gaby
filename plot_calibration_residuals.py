#!/usr/bin/env python3
"""Plot SD-433/SD-750 calibration residuals and the coincident-event energy distribution."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binned_statistic


DEFAULT_INPUT = Path(
    "/home/pbrichetto/sd433/icrc-2025_test7/paper_dataset/calibration/input/"
    "calibration_input_with_resolution.csv"
)
DEFAULT_SD433_INPUT = Path(
    "/home/pbrichetto/sd433/icrc-2025_test7/paper_dataset/calibration/output/"
    "sd433_icrc2025-test7_recalibrated.csv"
)
DEFAULT_OUTPUT = Path("figures/chapter_reconstruction/energy_calibration_residuals.pdf")
PLOT_STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")

SIZE0_VEM = 40.0
SIZE_MIN_VEM = 30.0
FULL_EFFICIENCY_SIZE_VEM = 15.0
PAR_A_PEV = 149.48524125
PAR_B = 0.96307844


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--sd433-input", type=Path, default=DEFAULT_SD433_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def calibrated_energy(size: np.ndarray) -> np.ndarray:
    return PAR_A_PEV * (size / SIZE0_VEM) ** PAR_B


def main() -> None:
    args = parse_args()
    events = pd.read_csv(args.input, usecols=["attenuated_size", "energy_pev"])
    events = events[(events["attenuated_size"] > 0) & (events["energy_pev"] > 0)]
    sd433_events = pd.read_csv(args.sd433_input, usecols=["energy_pev"])
    sd433_energy = sd433_events.loc[sd433_events["energy_pev"] > 0, "energy_pev"].to_numpy()
    sd433_log_energy = np.log10(sd433_energy) + 15.0

    size = events["attenuated_size"].to_numpy()
    energy_750 = events["energy_pev"].to_numpy()
    energy_433 = calibrated_energy(size)
    log_energy_433 = np.log10(energy_433) + 15.0
    residual = energy_750 / energy_433 - 1.0
    selected = size >= SIZE_MIN_VEM
    threshold_log_energy = np.log10(calibrated_energy(np.asarray(SIZE_MIN_VEM))) + 15.0
    full_efficiency_log_energy = (
        np.log10(calibrated_energy(np.asarray(FULL_EFFICIENCY_SIZE_VEM))) + 15.0
    )

    bin_edges = np.concatenate(
        (np.linspace(16.0, 18.1, 22), 18.1 + 0.3 * np.arange(1, 7), [20.0])
    )
    means, _, _ = binned_statistic(log_energy_433, residual, statistic="mean", bins=bin_edges)
    stds, _, _ = binned_statistic(log_energy_433, residual, statistic="std", bins=bin_edges)
    counts, _, _ = binned_statistic(log_energy_433, residual, statistic="count", bins=bin_edges)
    centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    valid = counts > 0

    plt.style.use(PLOT_STYLE)
    fig, (ax_res, ax_hist) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

    ax_res.scatter(
        log_energy_433[~selected], residual[~selected],
        s=8, color="gray", alpha=0.25, marker=".", rasterized=True,
    )
    ax_res.scatter(
        log_energy_433[selected], residual[selected],
        s=8, color="C1", alpha=0.30, marker=".", rasterized=True,
    )
    ax_res.errorbar(
        centers[valid], means[valid], yerr=stds[valid] / np.sqrt(counts[valid]),
        fmt="o", color="C0",
    )
    ax_res.axhline(0.0, ls="-.", color="k")
    ax_res.axvline(threshold_log_energy, ls="--", color="k")
    ax_res.set_xlim(16.8, 18.5)
    ax_res.set_ylim(-0.2, 0.2)
    ax_res.set_xlabel(r"$\lg(E^{\mathrm{SD-433}}/\mathrm{eV})$")
    ax_res.set_ylabel(r"$E^{\mathrm{SD-750}}/E^{\mathrm{SD-433}}-1$")

    histogram_edges = np.arange(16.0, 19.61, 0.1)
    ax_hist.hist(
        sd433_log_energy, bins=histogram_edges,
        histtype="stepfilled", color="C1", alpha=0.65,
    )
    ax_hist.axvline(
        full_efficiency_log_energy, ls="--", color="k", label="Full efficiency",
    )
    ax_hist.set_yscale("log")
    ax_hist.set_xlim(16.0, 19.6)
    ax_hist.set_xlabel(r"$\lg(E^{\mathrm{SD-433}}/\mathrm{eV})$")
    ax_hist.set_ylabel("Events")
    ax_hist.legend(frameon=False)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight")


if __name__ == "__main__":
    main()
