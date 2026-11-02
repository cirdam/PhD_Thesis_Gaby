"""Plot intrinsic spectral fits against the frozen nominal unfolded spectrum.

Run with /home/pbrichetto/sdana/.venv/bin/python. Original analysis files are
read-only. The archived response cutoff and spectral integral conventions are
preserved; the nominal broken-power-law deviance is verified before rendering.
The fit remains a forward-folded Poisson likelihood in observed-count space.
The preview contains a single logarithmic flux panel, without residuals.
The original data and fitted parameters are preserved.
"""
from pathlib import Path
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-supp-powerlaw")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from iminuit import Minuit
from scipy.integrate import quad
from scipy.special import xlogy
from scipy.stats import chi2

OUT = Path(__file__).resolve().parent
SOURCE = Path("/home/pbrichetto/phd_thesis/other_systematics_icrc2025_test7_omega005")
STYLE = Path("/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle")
EXPOSURE = 2.847
MATRIX_CUTOFF = 0.001


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    data = pd.read_csv(SOURCE / "nominal_spectrum.csv")
    nominal = pd.read_csv(SOURCE / "nominal_fit_parameters.csv").iloc[0]
    matrix = np.load(SOURCE / "nominal_migration_matrix.npy")
    x = data.lg_energy.to_numpy()
    mask = (x > 16.8) & (x < 18.5)
    x = x[mask]
    counts = data.counts.to_numpy()[mask]
    true_edges = 10 ** np.linspace(16, 20, matrix.shape[1] + 1)
    response = np.where(matrix >= MATRIX_CUTOFF, matrix, 0)[mask]

    def expected(j0, gamma):
        # Exact integral of J0*1e-13*(E/1e17)^(-gamma).
        exponent = 1 - gamma
        if abs(exponent) < 1e-10:
            integrated_flux = j0 * 1e4 * np.log(true_edges[1:] / true_edges[:-1])
        else:
            integrated_flux = j0 * 1e4 * (
                (true_edges[1:] / 1e17) ** exponent
                - (true_edges[:-1] / 1e17) ** exponent
            ) / exponent
        return EXPOSURE * (response @ integrated_flux)

    def deviance(observed, predicted):
        return 2 * np.sum(predicted - observed + xlogy(observed, observed / predicted))

    fit = Minuit(lambda J_0, gamma: float(deviance(counts, expected(J_0, gamma))),
                 J_0=0.9, gamma=3.1)
    fit.errordef = 1
    fit.limits["J_0"] = (0, None)
    fit.limits["gamma"] = (0, 10)
    fit.migrad()
    fit.hesse()
    assert fit.valid and fit.accurate
    pl_counts = expected(*fit.values)
    dof = len(counts) - 2
    pvalue = chi2.sf(fit.fval, dof)

    def broken_power_law(energy):
        return nominal.J_0 * 1e-13 * (energy / 1e17) ** (-nominal.gamma_0) * (
            1 + (energy / 10 ** nominal.lg_e01) ** (1 / nominal.w_01)
        ) ** ((nominal.gamma_0 - nominal.gamma_1) * nominal.w_01)

    nominal_integrals = np.array([
        quad(broken_power_law, low, high)[0]
        for low, high in zip(true_edges[:-1], true_edges[1:])
    ])
    bpl_counts = EXPOSURE * (response @ nominal_integrals)
    recovered_nominal_deviance = float(deviance(counts, bpl_counts))
    assert np.isclose(recovered_nominal_deviance, nominal.fval, atol=1e-8, rtol=0)
    # Guard the thesis' existing numerical claims instead of silently replacing them.
    assert f"{fit.fval:.1f}" == "41.1" and dof == 15
    assert f"{pvalue:.1e}" == "3.1e-04"

    def power_law(energy):
        return fit.values["J_0"] * 1e-13 * (energy / 1e17) ** (-fit.values["gamma"])

    # Display the accepted nominal unfolding, with its archived uncertainties.
    # Do not refit these points or treat these display residuals as count residuals.
    unfolded = data.unfolded_flux.to_numpy()[mask]
    errors = np.array([
        data.unfolded_flux_error_low.to_numpy()[mask],
        data.unfolded_flux_error_high.to_numpy()[mask],
    ])
    energy = 10 ** x
    smooth_x = np.linspace(16.8, 18.5, 600)
    smooth_energy = 10 ** smooth_x
    scale = energy ** 3 / 1e37
    smooth_scale = smooth_energy ** 3 / 1e37
    pl_flux = power_law(energy)
    bpl_flux = broken_power_law(energy)
    smooth_pl = power_law(smooth_energy)
    smooth_bpl = broken_power_law(smooth_energy)
    assert np.all(unfolded > 0) and np.all(errors >= 0)
    plt.style.use(STYLE)
    fig, ax = plt.subplots(layout="constrained")
    ax.errorbar(x, unfolded * scale, yerr=errors * scale, fmt="o", linestyle="none",
                color="black", markersize=4.5, capsize=2, label="SD-433 unfolded")
    ax.plot(smooth_x, smooth_pl * smooth_scale, color="C1", linewidth=1.8,
            label="Power law")
    ax.plot(smooth_x, smooth_bpl * smooth_scale, color="C0", linewidth=1.8,
            linestyle="--", label="Broken power law")
    ax.set_ylabel(r"$E^{3}J(E)\,/\,(10^{37}\,{\rm eV}^{2}\,{\rm km}^{-2}\,{\rm sr}^{-1}\,{\rm yr}^{-1})$")
    ax.set_yscale("log")
    ax.set_ylim(2.7, 14.2)
    ax.set_yticks([3, 4, 6, 8, 10, 14], labels=["3", "4", "6", "8", "10", "14"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.legend(loc="upper left", frameon=False)
    ax.set_xlabel(r"$\lg(E/{\rm eV})$")
    ax.set_xlim(16.8, 18.5)
    ax.grid(False)
    stem = "sd433_power_law_test"
    for suffix in ("pdf", "png"):
        path = OUT / f"{stem}.{suffix}"
        fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)

    fit_record = {"model": "single_power_law", "J_0": fit.values["J_0"],
                  "J_0_error": fit.errors["J_0"], "gamma": fit.values["gamma"],
                  "gamma_error": fit.errors["gamma"], "deviance": fit.fval,
                  "dof": dof, "pvalue": pvalue, "valid": bool(fit.valid),
                  "accurate_covariance": bool(fit.accurate)}
    pd.DataFrame([fit_record]).to_csv(OUT / "fit_parameters.csv", index=False)
    pd.DataFrame({"lg_energy": x, "counts": counts,
                  "power_law_expected_counts": pl_counts,
                  "nominal_expected_counts": bpl_counts,
                  "nominal_unfolded_flux": unfolded,
                  "nominal_unfolded_flux_error_low": errors[0],
                  "nominal_unfolded_flux_error_high": errors[1],
                  "intrinsic_power_law_flux": pl_flux,
                  "intrinsic_nominal_model_flux": bpl_flux,
                  "display_unfolded_relative_residual": unfolded / pl_flux - 1,
                  "count_space_relative_residual": counts / pl_counts - 1}).to_csv(
                      OUT / "binned_comparison.csv", index=False)
    pd.DataFrame({"lg_energy": smooth_x, "energy_eV": smooth_energy,
                  "intrinsic_power_law_flux": smooth_pl,
                  "intrinsic_nominal_model_flux": smooth_bpl,
                  "intrinsic_model_relative_difference": smooth_bpl / smooth_pl - 1}).to_csv(
                      OUT / "intrinsic_fit_curves.csv", index=False)
    inputs = [SOURCE / name for name in ["nominal_spectrum.csv", "nominal_fit_parameters.csv",
               "nominal_migration_matrix.npy", "run_manifest.json"]]
    provenance = {"operation": "Display intrinsic best-fit spectra with archived nominal unfolded data; preserve original forward-folded count-space fit",
                  "inputs": {str(path): digest(path) for path in inputs},
                  "script_sha256": digest(Path(__file__)), "style_sha256": digest(STYLE),
                  "command": "/home/pbrichetto/sdana/.venv/bin/python " + str(Path(__file__).resolve()),
                  "exposure_km2_sr_yr": EXPOSURE, "fit_lg_energy_range": [16.8, 18.5],
                  "true_lg_energy_range": [16.0, 20.0], "true_lg_bin_width": 0.01,
                  "reconstructed_lg_bin_width": 0.1, "matrix_cutoff": MATRIX_CUTOFF,
                  "nominal_deviance_reconstructed": recovered_nominal_deviance,
                  "nominal_deviance_archived": float(nominal.fval),
                  "statistical_errors": "Unchanged archived asymmetric nominal unfolded-flux statistical errors",
                  "display": "Smooth intrinsic PL and BPL fluxes multiplied by E^3; archived nominal unfolded-flux points; no folded curves",
                  "flux_axis_scale": "logarithmic; single flux panel with no residual panel",
                  "residual_data": "Retained unchanged in the numerical CSV for provenance; no residuals are displayed in this preview",
                  "likelihood": "Poisson deviance evaluated from observed counts and forward-folded expected counts, unchanged from the original test",
                  "outputs": {p.name: digest(p) for p in OUT.iterdir() if p.suffix in (".pdf", ".png", ".csv")},
                  "fit": fit_record}
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(fit_record, indent=2))


if __name__ == "__main__":
    main()
