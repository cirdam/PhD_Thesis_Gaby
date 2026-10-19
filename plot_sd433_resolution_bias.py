#!/usr/bin/env python3
"""Plot the SD-433 GSF-mix energy-bias and resolution parameterizations."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT = Path("figures/chapter_reconstruction/sd433_resolution_bias.pdf")
PLOT_STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")

LOG_ENERGY_MIN = 16.5
LOG_ENERGY_MAX = 18.5
LOG_FULL_EFFICIENCY = 16.8

BIAS_0 = 0.30
BIAS_1 = 10.0
BIAS_2 = 0.005
RESOLUTION_SHOWER = 0.103
RESOLUTION_DETECTOR = 0.096


def bias(log_energy: np.ndarray) -> np.ndarray:
    return BIAS_0 * np.exp(-BIAS_1 * (log_energy - 16.0)) + BIAS_2


def resolution(log_energy: np.ndarray) -> np.ndarray:
    energy_over_reference = 10.0 ** (log_energy - 17.0)
    return np.sqrt(
        RESOLUTION_SHOWER**2
        + RESOLUTION_DETECTOR**2 / energy_over_reference
    )


def main() -> None:
    log_energy = np.linspace(LOG_ENERGY_MIN, LOG_ENERGY_MAX, 500)

    plt.style.use(PLOT_STYLE)
    fig, (ax_bias, ax_resolution) = plt.subplots(
        1,
        2,
        figsize=(12, 5),
        sharex=True,
        constrained_layout=True,
    )
    ax_bias.plot(log_energy, 100.0 * bias(log_energy))
    ax_resolution.plot(log_energy, 100.0 * resolution(log_energy))
    ax_resolution.axhline(
        100.0 * RESOLUTION_SHOWER,
        color="0.6",
        linestyle="-",
    )

    for axis in (ax_bias, ax_resolution):
        axis.axvline(
            LOG_FULL_EFFICIENCY,
            color="k",
            linestyle="--",
        )
        axis.set_xlim(LOG_ENERGY_MIN, LOG_ENERGY_MAX)
        axis.set_xlabel(r"$\lg(E^{\mathrm{SD-433}}/\mathrm{eV})$")

    ax_bias.set_ylabel(r"Bias / \%")
    ax_resolution.set_ylabel(r"Resolution / \%")
    ax_resolution.plot([], [], color="k", linestyle="--", label="Full efficiency")
    ax_resolution.legend(frameon=False)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, bbox_inches="tight")


if __name__ == "__main__":
    main()
