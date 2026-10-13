#!/usr/bin/env python3
"""Build the SD-433 active-hexagon and accumulated-exposure figure."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")
INPUT_DIR = Path("/home/pbrichetto/hexagon_counting")
OUTPUT = Path(__file__).with_name("acumulated_exposure.pdf")

DATE_START = datetime(2018, 7, 1, tzinfo=timezone.utc)
DATE_STOP = datetime(2021, 12, 21, tzinfo=timezone.utc)
GPS_EPOCH = datetime(1980, 1, 6, tzinfo=timezone.utc)
SECONDS_PER_YEAR = 365.25 * 24 * 3600
OFFICIAL_EXPOSURE = 2.847  # km^2 sr yr; collaboration exposure calculator
HEXAGON_FILES = {
    "Tina Turner": "6T5_time_1764_Tina_Turner.dat",
    "Rosella": "6T5_time_11_Rosella.dat",
    "Pipi Jr.": "6T5_time_99_Pipi_Jr.dat",
    "Guili Jr.": "6T5_time_47_Guili_Jr.dat",
    "Lety Jr.": "6T5_time_97_Lety_Jr.dat",
    "Catherina": "6T5_time_12_Catherina.dat",
    "Chichino Jr.": "6T5_time_30_Chichino_Jr.dat",
}


def utc_to_gps(value):
    return (value - GPS_EPOCH).total_seconds()


def gps_to_datetime(values):
    return np.array(
        [GPS_EPOCH + timedelta(seconds=float(value)) for value in values],
        dtype=object,
    )


def load_minute_hexagons():
    files = sorted(
        (INPUT_DIR / "hexagons_milano").glob("SD433_HexagonsMn_UB_*.out")
    )
    if not files:
        raise FileNotFoundError("No minute-based SD-433 hexagon files found")
    data = np.vstack([np.atleast_2d(np.loadtxt(path))[:, :2] for path in files])
    start = utc_to_gps(DATE_START)
    stop = utc_to_gps(DATE_STOP)
    selected = (data[:, 0] >= start) & (data[:, 0] < stop)
    return data[selected, 0], data[selected, 1]


def load_bad_periods():
    data = np.atleast_2d(
        np.loadtxt(INPUT_DIR / "BadPeriods_SD433_UB_010718_311221.dat")
    )
    # Columns 1 and 9 contain the GPS start and stop of each bad period.
    starts = np.maximum(data[:, 1], utc_to_gps(DATE_START))
    stops = np.minimum(data[:, 9], utc_to_gps(DATE_STOP))
    selected = stops > starts
    return starts[selected], stops[selected]


def good_minute_mask(minute_starts, bad_starts, bad_stops):
    # Classify each minute by its midpoint; this reproduces the earlier
    # minute-based calculation to much better than the quoted precision.
    midpoints = minute_starts + 30.0
    indices = np.searchsorted(bad_starts, midpoints, side="right") - 1
    safe_indices = np.maximum(indices, 0)
    return ~((indices >= 0) & (midpoints < bad_stops[safe_indices]))


def daily_mean_series(minute_starts, values):
    day_number = ((minute_starts - minute_starts[0]) // 86400).astype(int)
    counts = np.bincount(day_number)
    means = np.bincount(day_number, weights=values) / counts
    dates = np.array(
        [DATE_START + timedelta(days=int(day)) for day in range(len(means))],
        dtype=object,
    )
    return dates, means


def cumulative_interval_seconds(grid, starts, stops):
    """Return the accumulated overlap of intervals up to each grid point."""
    starts = np.asarray(starts, dtype=float)
    stops = np.asarray(stops, dtype=float)

    def ramp_sum(points):
        points = np.sort(points)
        cumulative_points = np.r_[0.0, np.cumsum(points)]
        indices = np.searchsorted(points, grid, side="right")
        return grid * indices - cumulative_points[indices]

    return ramp_sum(starts) - ramp_sum(stops)


def load_individual_exposure_curves(plot_gps, aperture):
    curves = {}
    start = utc_to_gps(DATE_START)
    stop = utc_to_gps(DATE_STOP)
    for name, filename in HEXAGON_FILES.items():
        intervals = np.atleast_2d(np.loadtxt(INPUT_DIR / filename))
        starts = intervals[:, 0]
        stops = intervals[:, 1]
        selected = (stops > start) & (starts < stop)
        starts = np.maximum(starts[selected], start)
        stops = np.minimum(stops[selected], stop)
        curves[name] = (
            cumulative_interval_seconds(plot_gps, starts, stops)
            / SECONDS_PER_YEAR
            * aperture
        )
    scale = OFFICIAL_EXPOSURE / sum(curve[-1] for curve in curves.values())
    return {name: curve * scale for name, curve in curves.items()}


def main():
    plt.style.use(STYLE)
    minute_starts, active_hexagons = load_minute_hexagons()
    bad_starts, bad_stops = load_bad_periods()
    good = good_minute_mask(minute_starts, bad_starts, bad_stops)

    aperture = (
        np.sqrt(3) / 2
        * 0.433**2
        * np.pi
        * np.sin(np.deg2rad(40.0)) ** 2
    )
    minute_exposure = active_hexagons * 60.0 / SECONDS_PER_YEAR * aperture
    cumulative = np.cumsum(np.where(good, minute_exposure, 0.0))
    # The local bad-period masking is minute based. Anchor its sub-per-mille
    # normalization difference to the accepted collaboration exposure.
    cumulative *= OFFICIAL_EXPOSURE / cumulative[-1]

    times = gps_to_datetime(minute_starts)
    plot_gps = np.arange(
        utc_to_gps(DATE_START), utc_to_gps(DATE_STOP) + 86400, 86400
    )
    plot_dates = gps_to_datetime(plot_gps)
    exposure_curves = load_individual_exposure_curves(plot_gps, aperture)
    daily_times, daily_active_hexagons = daily_mean_series(
        minute_starts, active_hexagons
    )

    fig, (ax_hex, ax_exp) = plt.subplots(
        2,
        1,
        figsize=(11, 8),
        sharex=True,
        layout="constrained",
        gridspec_kw={"height_ratios": (0.85, 1.15)},
    )

    ax_hex.plot(daily_times, daily_active_hexagons, color="black", linewidth=0.8)
    ax_hex.set_ylabel(r"$N_{\mathrm{hex}}^{\mathrm{act}}$")
    ax_hex.set_ylim(-0.25, 7.55)
    ax_hex.set_yticks(np.arange(0, 8))
    ax_hex.text(
        0.02,
        0.95,
        r"$\theta < 40^\circ$",
        transform=ax_hex.transAxes,
        ha="left",
        va="top",
    )

    for name, curve in exposure_curves.items():
        positive = curve > 0
        ax_exp.plot(plot_dates[positive], curve[positive], linewidth=1.2, label=name)
    ax_exp.plot(
        times,
        cumulative,
        color="black",
        linewidth=2.4,
    )
    ax_exp.axhline(
        OFFICIAL_EXPOSURE,
        color="black",
        linestyle="--",
        linewidth=1.0,
    )
    label_date = datetime(2021, 11, 1, tzinfo=timezone.utc)
    ax_exp.text(
        label_date,
        OFFICIAL_EXPOSURE + 0.035,
        r"$2.85$ km$^2$ sr yr",
        ha="right",
        va="bottom",
        fontsize=11,
    )
    ax_exp.set(
        xlabel="Date",
        ylabel=r"$\mathcal{E}$ / km$^2$ sr yr",
        xlim=(DATE_START, DATE_STOP),
        ylim=(0, 3.08),
    )
    ax_exp.legend(
        loc="upper left",
        bbox_to_anchor=(0.01, 0.90),
        ncol=2,
        fontsize=10,
    )
    ax_exp.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax_exp.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax_exp.get_xticklabels(), rotation=30, ha="right")

    fig.align_ylabels((ax_hex, ax_exp))
    fig.savefig(OUTPUT, dpi=300)
    print(f"Saved {OUTPUT}")
    print(f"Final exposure: {cumulative[-1]:.6f} km^2 sr yr")


if __name__ == "__main__":
    main()
