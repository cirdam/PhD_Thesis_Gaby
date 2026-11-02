"""Render the SD-433 appendix from frozen, accepted analysis products.

No fits are rerun. Run with the sdana virtual environment's Python.
Input snapshots and SHA256 provenance accompany the resulting figures.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

ANALYSIS = Path("/home/pbrichetto/phd_thesis")
ENERGY = ANALYSIS / "energy_systematic_icrc2025_test7_omega005"
RESPONSE = ANALYSIS / "other_systematics_icrc2025_test7_omega005"
STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")
DEST = None
plt.style.use(STYLE)



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model(log_energy, row):
    energy = 10.0 ** np.asarray(log_energy)
    return (row.J_0 * 1e-13 * (energy / 1e17) ** (-row.gamma_0)
            * (1 + (energy / 10.0 ** row.lg_e01) ** (1 / row.w_01))
            ** ((row.gamma_0 - row.gamma_1) * row.w_01))


def saved_count_errors(counts, correction, flux):
    """Exactly reproduce the archived spectrum_tools.unfold convention.

    The original implementation applies the chi-square interval to corrected
    (possibly fractional) counts. This renderer preserves that convention.
    """
    n = np.asarray(counts) * np.asarray(correction)
    alpha = 2 * norm.cdf(-1)
    low = chi2.ppf(alpha / 2, 2 * n) / 2
    high = chi2.ppf(1 - alpha / 2, 2 * (n + 1)) / 2
    assert np.all(n > 0), "Only occupied in-range bins are rendered."
    scale = np.asarray(flux) / n
    return np.array([n - low, high - n]) * scale


def save(fig, name):
    for ax in fig.axes:
        ax.grid(False)
    for ext in ("pdf", "png"):
        path = HERE / f"{name}.{ext}"
        fig.savefig(path, dpi=220, bbox_inches="tight")
        if ext == "pdf" and DEST is not None:
            shutil.copy2(path, DEST / path.name)
    plt.close(fig)


def main():
    global DEST
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure-dir", type=Path,
                        help="Optionally install PDF figures into this chapter figure folder.")
    args = parser.parse_args()
    DEST = args.figure_dir
    if DEST is not None:
        DEST.mkdir(parents=True, exist_ok=True)
    inputs = {"energy_spectra.csv": ENERGY / "spectra.csv",
              "energy_fit_parameters.csv": ENERGY / "fit_parameters.csv",
              "energy_run_manifest.json": ENERGY / "run_manifest.json",
              "resolution_spectra.csv": RESPONSE / "resolution_spectra.csv",
              "resolution_fit_parameters.csv": RESPONSE / "resolution_fit_parameters.csv",
              "resolution_systematic_curves.csv": RESPONSE / "resolution_systematic_curves.csv",
              "nominal_spectrum.csv": RESPONSE / "nominal_spectrum.csv",
              "response_run_manifest.json": RESPONSE / "run_manifest.json"}
    for name, source in inputs.items():
        shutil.copy2(source, HERE / name)
    efits = pd.read_csv(HERE / "energy_fit_parameters.csv").set_index("shift")
    rfits = pd.read_csv(HERE / "resolution_fit_parameters.csv").set_index("model")
    edata = pd.read_csv(HERE / "energy_spectra.csv")
    rdata = pd.read_csv(HERE / "resolution_spectra.csv")
    nominal = pd.read_csv(HERE / "nominal_spectrum.csv")
    for parameter in ("J_0", "lg_e01", "gamma_0", "gamma_1", "w_01"):
        assert efits.loc["nominal", parameter] == rfits.loc["nominal", parameter]
    assert efits.valid.all() and rfits.valid.all()
    assert np.allclose(edata.nominal_unfolded_flux, rdata.nominal_unfolded_flux)
    assert np.allclose(edata.log_energy, rdata.lg_energy)
    mask = (edata.log_energy > 16.8) & (edata.log_energy < 18.5)
    x = np.linspace(16.8, 18.5, 500)
    scale = 10.0 ** (3 * edata.log_energy[mask]) / 1e38
    ylabel = r"$E^3J(E)\;[10^{38}\,\mathrm{km}^{-2}\,\mathrm{sr}^{-1}\,\mathrm{yr}^{-1}\,\mathrm{eV}^{2}]$"
    colors = {"minus": "C0", "nominal": "C1", "plus": "C2"}
    markers = {"minus": "v", "nominal": "o", "plus": "^"}

    fig, ax = plt.subplots(figsize=(8.6, 6.2), layout="constrained")
    for key, label in (("minus", r"Energy scale $-14\%$"),
                       ("nominal", "Nominal"), ("plus", r"Energy scale $+14\%$")):
        flux = edata[f"{key}_unfolded_flux"][mask]
        errors = saved_count_errors(edata[f"{key}_counts"][mask],
                                    edata[f"{key}_correction"][mask], flux)
        if key == "nominal":
            assert np.allclose(errors[0], nominal.unfolded_flux_error_low[mask], rtol=1e-10, atol=0)
            assert np.allclose(errors[1], nominal.unfolded_flux_error_high[mask], rtol=1e-10, atol=0)
        ax.errorbar(edata.log_energy[mask], flux * scale, yerr=errors * scale.to_numpy(),
                    fmt=markers[key], linestyle="none", color=colors[key],
                    markersize=5, capsize=2, label=label)
        ax.plot(x, model(x, efits.loc[key]) * 10.0 ** (3 * x) / 1e38, color=colors[key])
    ax.set(xlim=(16.8, 18.5), ylim=(0.15, 1.4), yscale="log", xlabel=r"$\lg(E/\mathrm{eV})$", ylabel=ylabel)
    ax.set_yticks([0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.4], labels=["0.2", "0.3", "0.4", "0.6", "0.8", "1.0", "1.4"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.legend(loc="lower left", frameon=False)
    save(fig, "sd433_energy_scale_unfolded_spectra")

    fig, (ax, ratio) = plt.subplots(2, 1, figsize=(9.8, 10.0), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]}, layout="constrained")
    for key, label in (("nominal", "Nominal"), ("minus", r"Resolution $-1\sigma$"),
                       ("plus", r"Resolution $+1\sigma$")):
        ax.plot(x, model(x, rfits.loc[key]) * 10.0 ** (3 * x) / 1e38,
                color=colors[key], linewidth=1.5)
        ax.plot(rdata.lg_energy[mask], rdata[f"{key}_unfolded_flux"][mask] * scale,
                marker=markers[key], linestyle="none", color=colors[key],
                markerfacecolor="none", markersize=6, label=label)
        if key != "nominal":
            ratio.plot(rdata.lg_energy[mask],
                       100 * rdata[f"{key}_relative_flux_change"][mask],
                       marker=markers[key], linestyle="none", color=colors[key], markersize=5)
            ratio.plot(x, 100 * (model(x, rfits.loc[key]) / model(x, rfits.loc["nominal"]) - 1),
                       color=colors[key])
    ax.set(ylabel=ylabel, ylim=(0.3, 1.02), yscale="log")
    ax.set_yticks([0.3, 0.4, 0.6, 0.8, 1.0], labels=["0.3", "0.4", "0.6", "0.8", "1.0"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.legend(loc="lower left", frameon=False)
    ratio.axhline(0, color="0.4", linewidth=0.8)
    ratio.set(xlim=(16.8, 18.5), ylabel=r"$\Delta J/J\;[\%]$", xlabel=r"$\lg(E/\mathrm{eV})$")
    save(fig, "sd433_resolution_unfolded_spectra")

    fig, axes = plt.subplots(2, 2, figsize=(13.0, 11.0), layout="constrained")
    for ax, (parameter, label) in zip(axes.flat, (("J_0", r"$J_0\;[10^{-13}\,\mathrm{km}^{-2}\,\mathrm{sr}^{-1}\,\mathrm{yr}^{-1}\,\mathrm{eV}^{-1}]$"),
            ("lg_e01", r"$\lg(E_{01}/\mathrm{eV})$"), ("gamma_0", r"$\gamma_0$"), ("gamma_1", r"$\gamma_1$"))):
        for i, key in enumerate(("minus", "nominal", "plus")):
            ax.errorbar(i, rfits.loc[key, parameter], yerr=rfits.loc[key, parameter + "_error"],
                        fmt=markers[key], linestyle="none", color=colors[key], capsize=4)
        ax.set_xticks([0, 1, 2], [r"$-1\sigma$", "Nominal", r"$+1\sigma$"])
        ax.set_xlim(-0.35, 2.35)
        ax.set_ylabel(label)
        ax.ticklabel_format(axis="y", useOffset=False)
    save(fig, "sd433_resolution_fit_parameters")

    manifest = {"sources": {name: {"path": str(path), "sha256": sha(path)} for name, path in inputs.items()},
                "generator_sha256": sha(Path(__file__)), "plot_style": {"path": str(STYLE), "sha256": sha(STYLE)},
                "typography": "Exact project mplstyle including LaTeX text; no font or text-rendering overrides; no plot titles",
                "method": "Re-render frozen binned spectra and fitted parameters; no refitting.",
                "flux_axis_scale": "logarithmic for energy-scale spectrum and upper resolution-spectrum panel; residual and fit-parameter axes remain linear",
                "energy_error_bars": "Original archived convention: chi-square intervals on corrected counts; verified against nominal archived errors.",
                "resolution_variation": "R_sh and R_0 shifted simultaneously by +/-0.01; other response inputs unchanged.",
                "resolution_spectra": "Statistical errors omitted to resolve small changes; lower panel uses the corresponding nominal unfolded/model flux denominator.",
                "fit_range_log10_eV": [16.8, 18.5], "omega_01": .05,
                "exposure_km2_sr_yr": 2.847, "zenith_range_deg": [0, 40],
                "outputs": {p.name: sha(p) for p in HERE.glob("sd433_*.pdf")}}
    (HERE / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"figures": list(manifest["outputs"]), "checks": "Nominal fits, flux arrays and error bars agree with archive."}, indent=2))


if __name__ == "__main__":
    main()
