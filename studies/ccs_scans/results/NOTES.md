# Notes

## 2026-07-29 -- collimator gap mistake

- The collimator gap used when saving the betatron and off-momentum loss maps in
  `results/plots/` was wrong.
- The beamer deck in `results/slides/` currently states TCP/TCSM at **5 sigma** (per
  confirmation at the time it was built) -- this needs to be corrected once the right value is
  known.
- Simulations are being re-run to produce the corrected loss maps.
- TODO once the re-run lands:
  - Update the gap value(s) in `results/slides/main.tex` (Overview frame + `generate_beamer_slides.py`'s settings table).
  - Regenerate `results/slides/generated_slides.tex` / `generated_settings_table.tex` and recompile `main.pdf`.
