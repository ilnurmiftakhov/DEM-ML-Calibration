# DEM-ML-Calibration

A pilot repository for **DEM calibration of the angle of repose** using **machine learning** on a very small local soil dataset.

## What is included

This repository contains:
- the project’s local source data files;
- reproducible Python scripts for baseline and extended experiments;
- trained pilot models;
- metrics tables, plots, and machine-generated analysis artifacts;
- concise working notes describing the research plan.

**Not included in Git:** article drafts, publication manuscripts, and narrative research reports prepared for submission/editorial work. Those are intentionally excluded from version control.

---

## Project goal

The goal is to test whether a small merged table containing:
- soil properties,
- DEM parameters,
- experimental angle-of-repose measurements,
- DEM-based angle-of-repose values,

is sufficient to build a pilot DEM/ML workflow for three tasks:
1. predicting `phi_exp` from soil properties;
2. building a surrogate model for `phi_DEM`;
3. directly predicting the calibration error `delta_phi = phi_DEM - phi_exp`.

---

## Key constraints

- the dataset is extremely small: **n = 12**;
- results should be interpreted as **pilot / proof-of-concept** only;
- good LOOCV scores do **not** imply validated transfer to unseen soil types;
- for `delta_phi`, no robust predictive model has been established at this stage.

---

## Short results summary

### Best models by LOOCV

| Task | Best model | RMSE | MAE | R² |
|---|---|---:|---:|---:|
| `phi_exp_soil` | GPR | 1.083 | 0.892 | 0.994 |
| `phi_dem_surrogate` | XGBoost | 3.532 | 2.328 | 0.933 |
| `delta_phi_calibration` | Dummy Mean | 0.648 | 0.567 | -0.190 |

### Main stress test: transfer to an unseen soil type

| Task | Best model | LOOCV MAE | LOGO MAE |
|---|---|---:|---:|
| `phi_exp_soil` | GPR | 0.892 | 8.017 |
| `phi_dem_surrogate` | XGBoost | 2.328 | 9.329 |
| `delta_phi_calibration` | Dummy Mean | 0.567 | 0.553 |

**Takeaway:** current models mainly behave as local interpolators within already observed soil types. Reliable generalization to a new soil type is not yet demonstrated.

---

## Repository structure

```text
DEM-ML-Calibration/
├── README.md
├── README.en.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── Структура данных.xlsx                  # source master table
├── Задачи по DEM модели.docx             # task description and working requirements
├── experiments/
│   ├── dem_ml_experiment.py              # baseline reproducible ML pipeline
│   ├── dem_ml_article_experiments.py     # extended experiments for the manuscript
│   ├── predict_dem_ml.py                 # inference from saved models
│   ├── models/                           # trained pilot models
│   ├── templates/                        # CSV templates for inference
│   ├── results/                          # baseline metrics, plots, and outputs
│   └── article_results/                  # bootstrap, ablation, and LOGO analysis
├── notes/
│   └── plan_DEM_ML.md                    # short project plan
├── docs/
│   ├── summary_for_grant.md              # one-page grant/demo brief
│   └── release_notes_v0.1-pilot.md       # release notes for the pilot tag
├── outputs/                              # excluded from Git: text reports
└── papers/                               # excluded from Git: manuscripts and article drafts
```

---

## Quick start

### 1. Clone

```bash
git clone git@github.com:ilnurmiftakhov/DEM-ML-Calibration.git
cd DEM-ML-Calibration
```

### 2. Install dependencies

Recommended Python version: **3.10+**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell / cmd
pip install -r requirements.txt
```

### 3. Run the baseline experiment

```bash
python experiments/dem_ml_experiment.py
```

### 4. Run the extended experiment suite

```bash
python experiments/dem_ml_article_experiments.py
```

### 5. Run inference with a saved model

```bash
python experiments/predict_dem_ml.py \
  --task phi_dem_surrogate \
  --input experiments/templates/phi_dem_surrogate_input_template.csv
```

---

## What the scripts generate

### `experiments/dem_ml_experiment.py`
Creates:
- dataset sanity checks;
- LOOCV model comparison;
- holdout metrics;
- leave-one-soil-type-out metrics;
- permutation importance;
- fact-vs-prediction plots;
- saved `joblib` models.

### `experiments/dem_ml_article_experiments.py`
Additionally creates:
- bootstrap metric distributions;
- feature-group ablation results;
- direct vs indirect `delta_phi` comparison;
- surrogate model error by soil type;
- aggregate CSV/PNG outputs for reporting and presentation.

---

## Core artifacts

### Baseline results
- `experiments/results/cv_results.csv`
- `experiments/results/best_models.json`
- `experiments/results/sanity_checks.json`
- `experiments/results/summary.json`

### Extended results
- `experiments/article_results/bootstrap_summary.csv`
- `experiments/article_results/phi_dem_ablation.csv`
- `experiments/article_results/delta_indirect_vs_direct.csv`
- `experiments/article_results/phi_dem_error_by_soil.csv`
- `experiments/article_results/loocv_vs_logo_mae.png`

### Saved models
- `experiments/models/phi_exp_soil__gpr.joblib`
- `experiments/models/phi_dem_surrogate__xgboost.joblib`
- `experiments/models/delta_phi_calibration__dummy_mean.joblib`

---

## Grant / demo orientation

This repository is already structured for a grant appendix, stage report, or external demonstration because it separates:
- **source project data**;
- **reproducible code**;
- **trained model artifacts**;
- **quantitative results and figures**;
- **concise planning notes**.

For formal sharing or expert review, the recommended minimal release package is:
1. `README.md` / `README.en.md`
2. `LICENSE`
3. `requirements.txt`
4. `Структура данных.xlsx`
5. `Задачи по DEM модели.docx`
6. `experiments/`
7. `notes/plan_DEM_ML.md`
8. `docs/summary_for_grant.md`

---

## Interpretation note

This repository intentionally preserves the **actual pilot findings**, including the negative ones:
- no robust model for `delta_phi`;
- strong performance drop under leave-one-soil-type-out validation;
- high metric instability due to the tiny sample size.

This is deliberate: the repository is meant to serve as an honest, reproducible research base for the next project phase, not as a polished benchmark claiming broad generalization.

---

## License note

See `LICENSE`.

In short:
- the **code** in this repository is released under the MIT License;
- the **research data files and manuscript-oriented text materials** remain restricted unless explicitly stated otherwise.

## Citation

See `CITATION.cff` for repository citation metadata.
