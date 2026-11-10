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

## Running the scans

The scans run on lxplus / HTCondor with EOS. The paths in `submit.sh` are hardcoded
for user `lpauwels`, so edit them before running the scans under another account.

```bash
cd studies/ccs_scans
./submit.sh
```

`submit.sh` builds a packed Xsuite virtual environment on EOS if one doesn't exist
yet (`ENVNAME`, currently `xcoll_0.11.4`). It then tars `scripts/` and `data/`,
expands `example.jobs.yaml` into `jobs.list` (one job per parameter combination)
and submits with `condor_submit`. Each job writes its output to EOS under
`studies/<STUDYNAME>/<case>/job_<n>/`.

To combine and plot the results of a case:

```bash
cd studies/ccs_scans/results
python postprocess.py <study> <case>   # e.g. crab_cavities_scans betatron_lossmaps
```

## Not tracked in git

Large simulation outputs from `prototyping/Debugging_LM/` (particle dumps,
impact tables and monitor files, up to 7 GB each) are excluded via `.gitignore`.
They exist only locally and can be regenerated with the notebooks.

## Known issues

The plots in `results/plots/` were saved with the wrong collimator gap; see
`studies/ccs_scans/results/NOTES.md`.
