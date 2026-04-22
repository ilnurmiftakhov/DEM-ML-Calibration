## DEM-ML-Calibration v0.1-pilot

First pilot release of a reproducible DEM/ML workflow for soil angle-of-repose calibration.

### Included
- baseline and extended experiment scripts;
- trained pilot models;
- LOOCV, holdout, LOGO, bootstrap, and ablation results;
- plots and machine-generated CSV/JSON artifacts;
- Russian and English documentation;
- one-page grant/demo brief.

### Main takeaways
- `phi_exp` is approximated best by **GPR** under LOOCV.
- `phi_DEM` is approximated best by **XGBoost** as a local surrogate.
- transfer to an unseen soil type is **not validated**: errors rise sharply under leave-one-soil-type-out.
- direct prediction of `delta_phi` is **not supported** on the current dataset.

### Pilot metrics
| Task | Best model | LOOCV MAE | LOGO MAE |
|---|---|---:|---:|
| `phi_exp_soil` | GPR | 0.892 | 8.017 |
| `phi_dem_surrogate` | XGBoost | 2.328 | 9.329 |
| `delta_phi_calibration` | Dummy Mean | 0.567 | 0.553 |

### Limitations
- very small dataset (`n = 12`);
- pilot/proof-of-concept only;
- no claim of broad generalization.

### Recommended next step
Expand the master dataset and repeat evaluation with stronger out-of-group validation.
