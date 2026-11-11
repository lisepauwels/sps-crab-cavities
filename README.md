# sps-crab-cavities

Collimation studies of the crab cavities in the CERN SPS, simulated with
[Xsuite](https://xsuite.readthedocs.io/) / [Xcoll](https://github.com/xsuite/xcoll).

The main study produces **loss maps** with the two SPS crab cavities
(`acfcah.61738`, `acfcah.61739`, 1 MV total at 400.79 MHz) switched on, scanning:

- crab cavity phase (−179° to 179°)
- crab cavity plane (H or V)
- collimator gap (5, 7.5, 10, 15 σ)
- with and without machine errors

Losses are generated in two ways:

- **betatron** – transverse blow-up with the ADT (H or V plane)
- **off-momentum** – RF frequency sweep (positive or negative Δp)

## Repository layout

```
sps_with_aperture_inj_q20_beam_sagitta4.json   SPS Q20 injection line with aperture
cc_md_parameters.md                            Open questions for the crab cavity MD

studies/ccs_scans/                 Crab cavity scans (HTCondor)
├── scripts/                       Tracking scripts run on the nodes
│   ├── blowup.py                  Betatron loss maps (ADT blow-up)
│   └── off-momentum.py            Off-momentum loss maps (RF sweep)
├── data/                          Input line (sps_crab_scan_matched.json)
├── example.jobs.yaml              Scan definition: script + parameter grid
├── submit.sh                      Builds the Xsuite env, spools files, submits
├── submission_scripts/            job.sh, submission.sub, generate_jobs.py, environment.sh
├── tests/                         Notebooks for preparing the line and test runs
└── results/
    ├── postprocess.py / .ipynb    Combine per-job loss maps and plot them
    ├── jsons/                     Combined loss maps and summaries
    ├── plots/                     Loss map plots, by crab cavity plane
    ├── slides/                    Beamer slides (generate_beamer_slides.py, main.tex)
    └── NOTES.md                   Study log and known issues

prototyping/                       Exploratory notebooks
└── Debugging_LM/                  Debugging loss maps across Xcoll versions (0.6.8 vs 0.10.1)
```

