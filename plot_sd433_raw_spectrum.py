"""Build the updated SD-433 raw spectrum in two complementary scalings."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

sys.path.insert(0, "/home/pbrichetto/sdana/sdana")
from tools.geo_tools import isHottest433


STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")
DATASET = Path(
    "/home/pbrichetto/sd433/icrc-2025_test7/paper_dataset/calibration/output/"
    "sd433_icrc2025-test7_recalibrated.csv"
)
OUTPUT = Path(__file__).resolve().parent / "figures" / "chapter_spectrum"
EXPOSURE = 2.847
LG_MIN = 16.8
LG_TRANSITION = 18.1
LG_MAX = 18.7


def selected_events() -> pd.DataFrame:
    data = pd.read_csv(DATASET, dtype={"auger_id": "string"})
    gps_start = pd.Timestamp("2018-07-01", tz="UTC").timestamp() - 315964800 + 18
    gps_end = pd.Timestamp("2021-12-21", tz="UTC").timestamp() - 315964800 + 18
    mask = (
        data.gps_second.between(gps_start, gps_end)
        & data["6T5"].eq(1)
        & data.T4_type.ne(0)
        & ~data.bad_period.astype(bool)
        & np.asarray(isHottest433(data.abs_hottest), dtype=bool)
        & data.zenith_deg.between(0.0, 40.0, inclusive="left")
        & data.log_energy.ge(LG_MIN)
    )
    return data.loc[mask].copy()


def bin_edges() -> np.ndarray:
    low = np.arange(LG_MIN, LG_TRANSITION + 0.05, 0.1)
    high = np.arange(LG_TRANSITION + 0.3, LG_MAX + 0.05, 0.3)
    return np.round(np.concatenate([low, high]), 10)


def poisson_interval(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    alpha = 2 * norm.cdf(-1)
    lower = 0.5 * chi2.ppf(alpha / 2, 2 * counts)
    upper = 0.5 * chi2.ppf(1 - alpha / 2, 2 * (counts + 1))
    return lower, upper


def main() -> None:
    plt.style.use(STYLE)
    data = selected_events()
    edges_lg = bin_edges()
    counts, _ = np.histogram(data.log_energy, bins=edges_lg)
    centers_lg = 0.5 * (edges_lg[:-1] + edges_lg[1:])
    centers = 10**centers_lg
    widths = np.diff(10**edges_lg)
    lower, upper = poisson_interval(counts)
    flux = counts / (EXPOSURE * widths)
    flux_lower = lower / (EXPOSURE * widths)
    flux_upper = upper / (EXPOSURE * widths)
    errors = np.vstack((flux - flux_lower, flux_upper - flux))

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.4), sharex=True)
    for ax, scale, ylabel in (
        (
            axes[0],
            np.ones_like(centers),
            r"$J_{\mathrm{raw}}(E)\,/\,(\mathrm{km}^{-2}\,\mathrm{sr}^{-1}\,"
            r"\mathrm{yr}^{-1}\,\mathrm{eV}^{-1})$",
        ),
        (
            axes[1],
            centers**3,
            r"$E^3 J_{\mathrm{raw}}(E)\,/\,(\mathrm{eV}^{2}\,\mathrm{km}^{-2}\,"
            r"\mathrm{sr}^{-1}\,\mathrm{yr}^{-1})$",
        ),
    ):
        ax.errorbar(
            centers,
            flux * scale,
            yerr=errors * scale,
            fmt="o",
            linestyle="none",
            color="C3",
            capsize=2,
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(10**LG_MIN, 10**LG_MAX)
        ax.set_xlabel(r"$E\,/\,\mathrm{eV}$", fontsize=22)
        ax.set_ylabel(ylabel, fontsize=22)
        ax.grid(False)

        top = ax.twiny()
        top.set_xlim(LG_MIN, LG_MAX)
        top.set_xticks([17.0, 17.5, 18.0, 18.5])
        top.set_xlabel(r"$\lg(E/\mathrm{eV})$", fontsize=22, labelpad=18)
        top.grid(False)

    axes[0].set_ylim(1e-19, 3e-12)
    axes[1].set_ylim(4e37, 1.15e38)

    for x, y, count in zip(centers, flux, counts, strict=True):
        axes[0].annotate(
            f"{count}",
            (x, y),
            xytext=(3, 6),
            textcoords="offset points",
            rotation=45,
            ha="left",
            va="bottom",
            color="black",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(OUTPUT / "sd433_raw_spectrum.pdf", bbox_inches="tight", pad_inches=0)
    fig.savefig(
        OUTPUT / "sd433_raw_spectrum.png",
        dpi=220,
        bbox_inches="tight",
        pad_inches=0,
    )

    table = pd.DataFrame(
        {
            "lg_energy_low": edges_lg[:-1],
            "lg_energy_high": edges_lg[1:],
            "lg_energy_center": centers_lg,
            "counts": counts,
            "raw_flux": flux,
            "raw_flux_low": flux_lower,
            "raw_flux_high": flux_upper,
        }
    )
    table.to_csv(OUTPUT / "sd433_raw_spectrum.csv", index=False)
    print(f"Selected events above threshold: {len(data)}")
    print(f"Events displayed through lg(E/eV)={LG_MAX}: {counts.sum()}")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
