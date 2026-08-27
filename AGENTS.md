# PhD Thesis repository instructions

This repository contains Gabriel Brichetto Orquera's PhD thesis on the measurement of the second knee in the cosmic-ray energy spectrum with the Pierre Auger Observatory.

## Scientific editing rules

- Do not invent scientific facts, numerical values, references, or analysis results.
- If information is uncertain or missing, flag it rather than guessing.
- Do not silently replace analysis values with values found elsewhere.
- Numerical results used throughout the thesis should preferentially be defined in `values.tex`.
- Generic notation and formatting macros belong in `utilities.tex`.
- Preserve established notation unless explicitly asked to change it.
- Distinguish clearly between SD-433, SD-750, and combined-spectrum results.
- The final thesis should describe the frozen reconstruction used for the measurement, not the chronological history of every reconstruction version.
- Earlier reconstruction or configuration comparisons should be retained only when they serve as meaningful robustness tests.

## Writing style

- Scientific prose should be precise and natural.
- Avoid unnecessary verbosity.
- Avoid first-person plural ("we") unless explicitly requested.
- Prefer one sentence per line in the LaTeX source.
- Preserve LaTeX commands and notation.
- Do not rewrite unrelated sections when working on a targeted request.

## Workflow

- Inspect relevant files before editing.
- Make small, coherent changes.
- Compile and check references when possible after structural edits.
- Do not make broad repository-wide changes without first describing the proposed change.
- Use meaningful commit messages.
