# Release notes: v0.1-pilot

## DEM-ML-Calibration v0.1-pilot

**Release type:** pilot / proof-of-concept  
**Tag:** `v0.1-pilot`

## Summary
This release captures the first reproducible pilot version of the DEM/ML calibration workflow for the angle of repose of soils. It packages the local data structure, experiment scripts, trained reference models, quantitative outputs, and documentation required for internal review, grant reporting, and external technical inspection.

The release should be interpreted as a **pilot research snapshot**, not as a validated production framework.

## Included in this release
- baseline ML experiment pipeline;
- extended experiment suite for manuscript-oriented analysis;
- trained pilot models (`joblib`);
- LOOCV, holdout, and leave-one-soil-type-out metrics;
- bootstrap and ablation results;
- plots and machine-generated CSV/JSON artifacts;
- Russian and English repository documentation;
- short one-page grant/demo brief.

## Main scientific takeaways
1. **`phi_exp` can be approximated well under LOOCV** using Gaussian Process Regression.
2. **`phi_DEM` can be approximated by a surrogate model** with XGBoost on the current pilot dataset.
3. **Transfer to an unseen soil type is not yet validated**: errors increase strongly under leave-one-soil-type-out evaluation.
4. **Direct prediction of `delta_phi` is not supported** on the current dataset; the best LOOCV baseline remains the constant predictor.
5. **The main bottleneck is dataset coverage, not model complexity.**

## Key pilot metrics
| Task | Best model | LOOCV RMSE | LOOCV MAE | LOOCV R² |
|---|---|---:|---:|---:|
| `phi_exp_soil` | GPR | 1.083 | 0.892 | 0.994 |
| `phi_dem_surrogate` | XGBoost | 3.532 | 2.328 | 0.933 |
| `delta_phi_calibration` | Dummy Mean | 0.648 | 0.567 | -0.190 |

### Stress test: transfer to unseen soil type
| Task | Best model | LOOCV MAE | LOGO MAE |
|---|---|---:|---:|
| `phi_exp_soil` | GPR | 0.892 | 8.017 |
| `phi_dem_surrogate` | XGBoost | 2.328 | 9.329 |
| `delta_phi_calibration` | Dummy Mean | 0.567 | 0.553 |

## Limitations
- very small sample size: `n = 12`;
- strong risk of instability in estimated metrics;
- high LOOCV quality does not imply broad generalization;
- surrogate conclusions remain local to the currently observed regimes;
- no validated ML calibration model for `delta_phi` yet.

## Recommended next steps
- expand the dataset to at least 50–100+ observations;
- cover wider soil-type and moisture ranges;
- run a more systematic DEM design of experiments;
- adopt nested CV and stronger out-of-group validation;
- revisit direct `delta_phi` modeling after data expansion.

## Main files to inspect
- `README.md`
- `README.en.md`
- `docs/summary_for_grant.md`
- `experiments/dem_ml_experiment.py`
- `experiments/dem_ml_article_experiments.py`
- `experiments/results/cv_results.csv`
- `experiments/article_results/bootstrap_summary.csv`
- `experiments/article_results/phi_dem_ablation.csv`
- `experiments/article_results/delta_indirect_vs_direct.csv`

## Citation
If you use this repository in internal reports, grant materials, or technical reviews, cite the repository version/tag and refer to `CITATION.cff`.
