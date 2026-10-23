# Chapter 8 writing checklist

## Latest pull (22 October 2026, `c946adc`)

The newest upstream commit changes only `Chapter_6_Energy_reconstruction.tex` (introductory reconstruction and CIC prose). It leaves `Chapter_8_Combined_spectrum.tex`, its figures, and all open Chapter 8 items below unchanged. The Chapter 6 label `\label{sec:res_and_bias}` remains present; the Chapter 8 reference to `sec:res_bias` still needs correction. This pull has not been followed by a fresh thesis compilation.

## Status after pulling `origin/main` (22 October 2026)

The new draft adds prose for the SD-750 response, migration matrix, raw-spectrum comparison, spectral model, and the first combined-likelihood construction. The numbered headings below retain the intended outline; the pulled chapter currently groups these topics into three sections. Checkmarks below refer to material actually present in `Chapter_8_Combined_spectrum.tex`; an item remains open when the text is only partial or needs scientific verification.

### Resolve before further polishing

- [ ] Remove duplicate `\label{sec:sd750_spectrum}` and duplicate `\label{sec:combined_spectrum}`. Keep one coherent chapter structure. The standalone SD-750 and combined-fit tables now appear separately with distinct labels.
- [ ] Fix the introduction's `\cref{sec:sd750_dataset}` and `\cref{sec:sd750_response}` references; those labels are absent after the section reorganization. Also resolve `\cref{sec:res_bias}` and `\cref{appendix:chapter_combined}`, which have no matching labels in the current thesis source. The combined-results table reference now resolves.
- [ ] Verify and correct the displayed two-transition spectral model (143–158): the leading power has `+\gamma_0`, the transition factor uses `E_{ij}` with an index arrangement that needs checking, and the expression must reproduce the Chapter 7 convention.
- [ ] Verify and correct the SD-750 bias expression (77–93): define `x`, check the logarithm's domain and all subscripts, including `b4` versus `b_4`, against the implemented response.
- [x] Adopt the collaboration's established approach of treating the SD-433 and SD-750 contributions as independent likelihood terms for the combined fit. The draft states this choice (183–189); coincident events are not a blocker for this thesis analysis.
- [ ] Reconcile the prose claiming better high-energy resolution for SD-750 (74) with the migration-matrix comparison attributing the tighter high-energy spread to SD-433 (109), and check both against the plotted curves.
- [ ] Verify the statement that the ankle is at `4 PeV` (141); this is inconsistent with the fitted `\lg(E_{12}/\mathrm{eV})=18.641` in the existing table.
- [ ] Reconcile the displayed exposure macro `165.4(5.0)` in `values.tex` with the nominal analysis value `165.403`, explaining the uncertainty and rounding.
- [ ] Check the new raw-spectrum attribution of an approximately 5% difference to bad periods (126–129) against the analysis products before keeping it as a causal claim.
- [x] Keep a two-column standalone SD-750 fit table, marking only $E_{01}$ and $\omega_{12}$ as fixed. Present exposure-only and calibration-variation fits in a separate three-column table, with reported errors, parameter shifts, and fit-quality rows separated by rules.
- [ ] State the nominal combined fit range, fitted exposure shift, deviance/degrees of freedom, $p$-value, parameter uncertainties, and overlap agreement in the prose (fit quality and parameters are now in the table; range and overlap discussion remain open).
- [ ] Distinguish the nominal fit, which varies the SD-433 exposure with fixed calibration, from the later calibration-variation step. The draft defines `\mathcal L_{\mathrm{cal}}` but does not present that second result or its interpretation.
- [ ] Verify the Gaussian nuisance definitions and notation (187–222), including `\mathcal L_{\mathrm{cal}}` versus `\mathcal L_{AB}`, the exposure-shift definition, and which calibration covariance is intended.
- [ ] Add conclusions for the lower-limit scan, upper-limit scan, and width profile; they still appear only in figure captions.
- [ ] Add a chapter summary and clarify that the $\pm14\%$ band represents the common FD scale only, not the full combined systematic budget.

## Global analysis choices and verified analysis products

- [x] Use the bad-period-cleaned SD-750 exposure: $\mathcal{E}_{750}=165.403\,\mathrm{km^2\,sr\,yr}$.
- [x] Adopt the SD-750 full-efficiency threshold $\lg(E/\mathrm{eV})=17.2$.
- [x] Record that 291,985 SD-750 events lie above full efficiency.
- [x] Record that 291,982 of these events lie in the plotted range $17.2\leq\lg(E/\mathrm{eV})<19.5$; three events lie above 19.5.
- [x] Use the updated ICRC 2025 SD-750 energy calibration.
- [x] Keep the SD-750 and combined figures in `figures/chapter_combined/`.
- [x] Confirm `\label{sec:res_and_bias}` exists in Chapter 6 for the Chapter 7 references.
- [ ] Rename one of the duplicate `eq:poisson_deviance` labels defined in Chapters 5 and 7.

## 8.1 Updated SD-750 dataset

- [x] State the SD-750 acquisition period and summarize the event-quality selection.
- [ ] Refer to `\cref{sec:triggers}` for the general geometrical and fiducial selections (the cuts are described, but this cross-reference is absent).
- [ ] State that bad acquisition periods are removed following the principles described in `\cref{sec:stability}` (bad periods are mentioned, but this cross-reference is absent).
- [ ] Quote the final exposure, $165.403\,\mathrm{km^2\,sr\,yr}$.
- [x] Refer to `\cref{sec:exposure}` instead of repeating the geometrical-exposure derivation (in the combined-likelihood section; also cite it by the dataset exposure).
- [ ] Quote the number of events above full efficiency: 291,985.

### SD-750 reconstruction efficiency

- [ ] Explain that the SD-750 efficiency is measured using showers independently selected and reconstructed by SD-433.
- [x] Define the numerator and denominator used to calculate the efficiency.
- [ ] Refer to `\cref{sec:efficiency}` for the general role of efficiency and the full-efficiency criterion.
- [x] Include `\cref{fig:sd750_efficiency}`.
- [x] Compare the updated curve with Ref. `\cite{PierreAuger:2021:InfillSpectrum}` (qualitative text and figure; explanation of the difference remains open).
- [ ] State that the first measured bin above 97% is $17.1\leq\lg(E/\mathrm{eV})<17.2$.
- [ ] Explain that its upper edge, $\lg(E/\mathrm{eV})=17.2$, is adopted so that the spectrum lies entirely beyond that bin.
- [ ] Explain that the difference from the EPJC 2021 curve is mainly associated with differences in event selection, particularly bad-period removal.
- [ ] Conclude that the nominal SD-750 spectrum begins at $\lg(E/\mathrm{eV})=17.2$.

## 8.2 Updated SD-750 spectrum

### Raw spectrum

- [ ] State that the raw flux follows the definition in `\cref{sec:raw_spectrum}`, particularly `\cref{eq:raw_flux}`.
- [x] Do not repeat the raw-flux derivation, exposure definition, or motivation for plotting $E^3J(E)$.
- [ ] State that the updated spectrum uses the same reconstructed-energy bins as EPJC 2021, including its two wide high-energy bins.
- [x] Include the corrected `\cref{fig:sd750_raw_spectrum}` calculated with $\mathcal{E}_{750}=165.403\,\mathrm{km^2\,sr\,yr}$.
- [ ] Compare the updated and published raw spectra in normalization, shape, energy range, and statistical precision (normalization and shape are drafted; verify the causal explanation and add the remaining comparisons).
- [ ] Keep this discussion at the reconstructed-spectrum level and defer the physical interpretation until after unfolding.

### SD-433 and SD-750 detector responses

- [ ] State that the bias and resolution enter the response function defined in `\cref{forward_folding}` and `\cref{eq:resolution_function}`.
- [ ] Refer to `\cref{subsec:calibration_sample}` and `\cref{subsec:calibration_fit}` for the adopted SD-750 reference scale and resolution parameterization.
- [ ] Refer to `\cref{sec:energy_calibration}` for the relation between the SD-433 and SD-750 energy scales.
- [x] Include `\cref{fig:sd433_sd750_response}`.
- [ ] Discuss only the different thresholds, biases, and resolutions of the two arrays.
- [x] State explicitly that the EPJC 2021 SD-750 bias and resolution are retained for the present analysis.
- [ ] Do not repeat the definitions or extraction of bias and resolution.

### SD-750 migration matrix

- [x] State that the matrix is constructed using the Chapter 7 formalism (current draft cites `\cref{sec:unfolded_spectrum}`; check whether `\cref{forward_folding}` is the more precise reference).
- [ ] Refer to `\cref{eq:migration_matrix2}` for the exact definition.
- [x] Refer to `\cref{eq:matrix_approx}` for the numerical approximation.
- [ ] Refer to `\cref{eq:resolution_function}` for the detector response.
- [x] Do not repeat the derivation or validation of the approximate matrix.
- [x] Include `\cref{fig:sd750_migration_matrix}`.
- [ ] Explain the efficiency suppression below threshold, bias relative to the diagonal, and width produced by the resolution.
- [x] Identify $i$ as the reconstructed-energy index and $j$ as the true-energy index (in the matrix caption).

### Forward-folded fit and unfolded spectrum

- [ ] State that the SD-750 spectrum uses the binned Poisson forward-folding method introduced in `\cref{forward_folding}`.
- [ ] Refer to `\cref{eq:expected_true_counts}` and `\cref{eq:expected_reconstructed_counts}` for the expected event counts.
- [ ] Refer to `\cref{eq:poisson_deviance}` for the fit statistic.
- [ ] Refer to `\cref{eq:correction_factor}` and `\cref{sec:unfolded_spectrum}` for the construction of unfolded points.
- [x] Do not redefine forward folding, unfolding, or the Poisson likelihood.
- [ ] State the nominal fit range, $17.2\leq\lg(E/\mathrm{eV})<19.5$.
- [x] State that the spectral model extends `\cref{eq:bplwst}` with a second smooth transition describing the ankle (displayed equation still requires correction).
- [ ] State the fit configuration: $J_0$, $\omega_{01}$, $\gamma_0$, $\gamma_1$, $E_{12}$, and $\gamma_2$ free; $E_{01}$ fixed to the SD-433 result; $\omega_{12}=0.05$ fixed.
- [x] Include `\cref{fig:sd750_unfolded_spectrum}`.
- [x] Include `\cref{tab:sd750_fit_parameters}`.
- [x] Quote $D^2=18.07$ for 17 degrees of freedom and $p=0.385$.
- [x] Explain that fixing the second-knee position to the SD-433 value gives an acceptable description of the SD-750 data (fixed position and fit quality are stated; an explicit concluding sentence would help).
- [ ] Compare the updated unfolded points with EPJC 2021 without repeating the raw-spectrum discussion.
- [ ] State that the EPJC points do not enter either the fit or the residuals.

## 8.3 Combined SD-433 and SD-750 spectrum

### Motivation and consistency

- [ ] Recall that the standalone SD-433 spectrum is presented in `\cref{sec:unfolded_spectrum}`.
- [ ] Recall that the SD-433 scale is calibrated against SD-750 in `\cref{sec:energy_calibration}`.
- [ ] Explain that the two spectra share the underlying FD energy scale but have different efficiencies, exposures, detector responses, and statistical reach.
- [ ] Explain that SD-433 provides statistics below and around the second knee, whereas SD-750 extends the measurement through the ankle.
- [ ] Explain that the overlap tests the consistency of the measurements.

### Combined likelihood

- [x] Define the combined likelihood as the product of the SD-433 and SD-750 terms, with exposure and calibration constraints (the draft gives this form instead of an explicit sum of deviances).
- [ ] Refer to `\cref{forward_folding}` for each individual likelihood contribution.
- [ ] State that each detector retains its own exposure, efficiency, response matrix, counts, and fit range.
- [x] State that both contributions share one physical spectral model (the first-step fit refers to the common model in `\cref{eq:extended_bplwst}`).
- [ ] Identify the common spectral parameters and array-specific response inputs.
- [ ] Refer to `\cref{subsec:calibration_fit}` for the nominal SD-433 calibration parameters $A$ and $B$.
- [ ] Refer to `\cref{subsec:calibration_systematic}` for their allowed systematic variations.
- [x] State that $A$ and $B$ remain at their nominal values in the nominal combined fit (the first step varies only the exposure and spectral parameters).
- [x] Document the treatment of the SD-433 exposure nuisance (definition and uncertainty still require verification).
- [ ] Clarify that the displayed combined datapoints are a representation of the measurement; the fit is performed on the separate reconstructed counts.

### Combined result

- [x] Include `\cref{fig:sd433_sd750_combined_spectrum}`.
- [ ] State that the combined datapoints begin at $\lg(E/\mathrm{eV})=16.8$.
- [x] State that SD-433 binning is used below 17.2 and SD-750 binning from 17.2 upward (in the combined-spectrum caption).
- [ ] Discuss the agreement of the standalone measurements in their overlap.
- [ ] State whether a relative normalization offset remains.
- [x] Add a table of the combined-fit spectral parameters and fit quality for the exposure-only and calibration-variation fits.
- [ ] Compare the combined second-knee result with `\cref{table:sd433_fits_omega}`.
- [ ] Discuss the improvement in $\omega_{01}$, the post-knee index, and the ankle parameters.

### Energy-scale systematic band

- [ ] State that the common FD energy-scale uncertainty is discussed in `\cref{sec:systematics}`.
- [x] Refer specifically to the propagation derived in `\cref{eq:energy_systematic_bplwst}` (in the systematic-band caption).
- [x] Do not repeat the change-of-variables derivation.
- [ ] Explain that the $\pm14\%$ shift is coherent because both spectra inherit the same FD energy scale.
- [x] Include `\cref{fig:sd433_sd750_combined_systematic}`.
- [x] Clarify that error bars are statistical and the shaded band represents only the propagated common energy-scale uncertainty (in the caption).
- [x] Do not describe this band as the complete systematic budget.

## 8.4 Stability of the combined fit

### Minimum SD-750 energy

- [ ] Refer to `\cref{fig:sd433_fit_min_stability}` for the analogous SD-433-only test.
- [ ] Explain that the combined scan determines where SD-750 can safely enter the joint likelihood.
- [x] Include `\cref{fig:combined_fit_min_scan}`.
- [x] State that the scan covers $17.0\leq\lg(E_{\min}^{750}/\mathrm{eV})\leq17.5$ (in the caption).
- [x] Explain that fits beginning below 17.2 are disfavoured (the caption states the fit first becomes acceptable at 17.2; add discussion in the text).
- [ ] Connect this behaviour with the independently measured efficiency threshold.
- [ ] Use the scan to justify the nominal lower boundary of 17.2.

### Maximum SD-750 energy

- [x] Include `\cref{fig:combined_fit_max_scan}`.
- [ ] Explain that the scan tests sensitivity to the sparsely populated highest-energy bins.
- [ ] Discuss the total deviance, deviance per degree of freedom, and $p$-value.
- [ ] State whether the second-knee parameters remain stable.
- [ ] Explain the adopted upper fit boundary.

### Second-knee transition width

- [ ] Recall that SD-433 alone cannot constrain $\omega_{01}$, as discussed in `\cref{subsec:transition_systematic}`.
- [ ] Refer to `\cref{fig:omega_study}` for the SD-433-only width scan.
- [x] Do not repeat the toy-Monte-Carlo study.
- [ ] Explain that the combined profile tests whether the additional SD-750 lever arm constrains the width.
- [x] Include `\cref{fig:combined_omega_profile}`.
- [x] State that the remaining spectral parameters are profiled at each fixed $\omega_{01}$ (in the caption).
- [x] State that the SD-433 exposure is fixed and $A$ and $B$ are unchanged in this profile (in the caption).
- [x] Quote the minimum at $\omega_{01}=0.314$ (in the caption).
- [ ] Use the significant $\Delta D^2$ crossings to report the allowed interval.
- [ ] Contrast the finite combined minimum with the weak SD-433-only constraint.

### Calibration-parameter variation

- [ ] Refer to `\cref{subsec:calibration_systematic}` for the allowed SD-433 calibration variation.
- [ ] Do not repeat the analytical propagation of changes in $A$ and $B$.
- [ ] Explain that floating $A$, $B$, and the exposure simultaneously produces strong correlations.
- [ ] State that the exposure is therefore fixed to the value preferred by the preceding fit.
- [ ] Use only the significant calibration displacement $\delta$, leaving the nominal presentation of $A$ and $B$ unchanged.
- [ ] Report the fitted $\delta$, its uncertainty, the deviance change, and its effect on the spectral parameters.
- [ ] Conclude whether the nominal result is stable under the allowed calibration variation.

## 8.5 Chapter summary

- [ ] State that the revised reconstruction and energy calibration produce an updated SD-750 spectrum; refer to `\cref{subsec:calibration_sample}`.
- [ ] State that the forward-folding method from `\cref{forward_folding}` is applied consistently to SD-750.
- [ ] Summarize the comparison with EPJC 2021 without repeating the detailed raw and unfolded discussions.
- [ ] State that the standalone SD-750 spectrum is compatible with a second knee at the SD-433 position.
- [ ] Summarize the combined SD-433--SD-750 energy range and fit.
- [ ] Quote the final second-knee position, transition width, spectral indices, ankle parameters, deviance, and $p$-value.
- [ ] State that the combination improves the constraint on $\omega_{01}$ relative to `\cref{subsec:transition_systematic}`.
- [ ] Summarize the lower- and upper-energy stability scans.
- [ ] State that the common energy-scale uncertainty is propagated using `\cref{eq:energy_systematic_bplwst}`.
- [ ] Conclude that the arrays give a consistent continuous spectrum from below the second knee through the ankle.

## Figure and reproducibility checks

- [x] `sd750_efficiency.pdf`: verified; independent of exposure.
- [x] `sd750_raw_spectrum.pdf`: regenerated with exposure 165.403 and exact EPJC 2021 binning.
- [x] `sd433_sd750_bias_resolution.pdf`: verified against the adopted response parameterizations.
- [x] `sd750_migration_matrix.pdf`: verified; independent of exposure.
- [x] `sd750_unfolded_spectrum.pdf`: verified to use the corrected normalization.
- [x] `sd433_sd750_combined_spectrum.pdf`: verified to use exposure 165.403 and combined points beginning at 16.8.
- [x] `sd433_sd750_combined_spectrum_systematic.pdf`: verified to use the combined points and coherent energy-scale band.
- [x] `combined_fit_max_scan_deviance.pdf`: verified to use exposure 165.403.
- [x] `combined_fit_min_scan_deviance.pdf`: numerically checked against the nominal combined configuration.
- [x] `combined_omega_profile.pdf`: numerically checked; minimum at $\omega_{01}=0.314$.
- [ ] Preserve the final generating scripts and metadata for the minimum-energy scan and $\omega_{01}$ profile beside the analysis outputs.
- [ ] Compile the thesis again after the pulled changes and check the Chapter 8 references; the earlier successful compilation predates this draft.
