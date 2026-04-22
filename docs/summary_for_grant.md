# DEM-ML-Calibration: one-page project brief for grant/demo use

## Project title
**Pilot DEM/ML calibration of the soil angle of repose for future surrogate modeling and automated parameter tuning**

## Project status
Pilot stage completed on a small local dataset.

## Problem
Calibration of DEM models for soil-like materials is labor-intensive and computationally expensive. Even when DEM reproduces observed macroscopic behavior, selecting contact parameters remains nontrivial. A practical question for the next phase is whether a combined DEM/ML workflow can reduce calibration cost and support faster screening of parameter sets.

## What was done
A reproducible local pipeline was built around a structured dataset combining:
- soil type and granulometric composition;
- moisture and bulk density;
- DEM parameter settings;
- experimental angle of repose (`phi_exp`);
- DEM angle of repose (`phi_DEM`);
- calibration residual `delta_phi = phi_DEM - phi_exp`.

Three ML tasks were tested:
1. prediction of `phi_exp` from soil properties;
2. surrogate prediction of `phi_DEM`;
3. direct prediction of calibration error `delta_phi`.

The following model families were compared:
- Dummy baseline;
- Ridge regression;
- Random Forest;
- Gaussian Process Regression;
- XGBoost.

Validation included:
- leave-one-out cross-validation (LOOCV);
- leave-one-soil-type-out (LOGO);
- bootstrap-based stability analysis;
- feature-group ablation for the DEM surrogate.

## Data scope
- number of observations: **12**;
- no missing values;
- no duplicate rows;
- four soil groups represented;
- target variables internally consistent (`delta_phi = phi_DEM - phi_exp`).

## Main results
### Best LOOCV models
| Task | Best model | RMSE | MAE | R² |
|---|---|---:|---:|---:|
| `phi_exp_soil` | GPR | 1.083 | 0.892 | 0.994 |
| `phi_dem_surrogate` | XGBoost | 3.532 | 2.328 | 0.933 |
| `delta_phi_calibration` | Dummy Mean | 0.648 | 0.567 | -0.190 |

### Transfer to an unseen soil type
| Task | Best model | LOOCV MAE | LOGO MAE |
|---|---|---:|---:|
| `phi_exp_soil` | GPR | 0.892 | 8.017 |
| `phi_dem_surrogate` | XGBoost | 2.328 | 9.329 |
| `delta_phi_calibration` | Dummy Mean | 0.567 | 0.553 |

## Interpretation
The pilot results are encouraging only in a narrow sense:
- `phi_exp` and `phi_DEM` can be approximated well under interpolation-like validation;
- the DEM surrogate is promising as a local response approximator;
- direct modeling of `delta_phi` is not yet supported by the data.

At the same time, the core negative finding is important:
- performance drops sharply under leave-one-soil-type-out validation;
- therefore the current models should **not** be treated as validated for transfer to unseen soil classes.

## Why this matters for the next grant stage
This pilot phase already delivered:
- a reproducible codebase;
- trained reference models;
- baseline metrics and stress tests;
- a clean structure for data, code, and outputs;
- a concrete diagnosis of where the bottleneck is.

The bottleneck is **not** model complexity. The bottleneck is **data coverage**.

## What should be funded next
### 1. Expansion of the master dataset
Target: at least **50–100+ observations** with balanced coverage across soil types and moisture ranges.

### 2. Planned DEM design of experiments
Systematic variation of:
- `omega`;
- `model_n`, `model_t`, `model_c`;
- `k_d`, `kd_k`, `e`, `d_p`.

### 3. Next-stage validation protocol
- nested CV;
- group-based splits by soil type;
- bootstrap confidence intervals;
- explicit out-of-group testing.

### 4. Final target outcome
A practically usable workflow for:
- surrogate prediction of DEM response;
- ranking promising DEM parameter sets;
- future automatic minimization of `|delta_phi|` for new soil conditions.

## Deliverables already available
- reproducible scripts in `experiments/`;
- trained models in `experiments/models/`;
- baseline and extended results in `experiments/results/` and `experiments/article_results/`;
- project README in Russian and English;
- local manuscript draft kept outside the public Git release flow.

## Risk statement
This is a **pilot proof-of-concept**, not a production-ready calibration framework. Any future claim of broad generalization requires a larger dataset and stricter out-of-group validation.
