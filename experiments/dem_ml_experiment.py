import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut, LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

RANDOM_STATE = 42
BASE = Path('.')
OUT = BASE / 'experiments' / 'results'
MODELS_DIR = BASE / 'experiments' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown='ignore', sparse=False)


def build_preprocessor(num_cols, cat_cols):
    return ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
            ]), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('ohe', make_ohe()),
            ]), cat_cols),
        ],
        sparse_threshold=0,
    )


def make_models():
    gpr_kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(length_scale=1.0) + WhiteKernel(noise_level=1.0)
    return {
        'dummy_mean': DummyRegressor(strategy='mean'),
        'ridge': Ridge(alpha=1.0),
        'random_forest': RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            min_samples_leaf=1,
            max_depth=None,
        ),
        'gpr': GaussianProcessRegressor(kernel=gpr_kernel, normalize_y=True, random_state=RANDOM_STATE),
        'xgboost': XGBRegressor(
            n_estimators=120,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            objective='reg:squarederror',
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
    }


def metrics(y_true, y_pred):
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {'rmse': float(rmse), 'mae': float(mae), 'r2': float(r2)}


def plot_pred_vs_actual(df_pred, task_name):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(df_pred['actual'], df_pred['predicted'], color='#1f77b4', s=60)
    lims = [min(df_pred['actual'].min(), df_pred['predicted'].min()), max(df_pred['actual'].max(), df_pred['predicted'].max())]
    ax.plot(lims, lims, '--', color='gray')
    for _, row in df_pred.iterrows():
        ax.annotate(str(row['sample_id']), (row['actual'], row['predicted']), fontsize=8, alpha=0.75)
    ax.set_xlabel('Факт')
    ax.set_ylabel('Прогноз')
    ax.set_title(f'LOOCV: факт vs прогноз ({task_name})')
    fig.tight_layout()
    fig.savefig(OUT / f'{task_name}_pred_vs_actual.png', dpi=180)
    plt.close(fig)


def plot_phi_vs_omega(df):
    fig, ax = plt.subplots(figsize=(6, 5))
    for soil, sub in df.groupby('soil_type'):
        ax.scatter(sub['omega'], sub['phi_exp'], s=70, label=f'{soil} / φ_exp')
        ax.scatter(sub['omega'], sub['phi_DEM'], s=70, marker='x', label=f'{soil} / φ_DEM')
    ax.set_xlabel('Влажность ω, %')
    ax.set_ylabel('Угол откоса φ, °')
    ax.set_title('Экспериментальный и DEM-угол откоса vs влажность')
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / 'phi_vs_omega.png', dpi=180)
    plt.close(fig)


def plot_delta_by_soil(df):
    order = list(df.groupby('soil_type')['delta_phi'].mean().sort_values().index)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    positions = np.arange(len(order))
    data = [df.loc[df['soil_type'] == soil, 'delta_phi'].values for soil in order]
    ax.boxplot(data, positions=positions, widths=0.55)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_xticks(positions)
    ax.set_xticklabels(order, rotation=15, ha='right')
    ax.set_ylabel('Δφ = φ_DEM − φ_exp, °')
    ax.set_title('Распределение ошибки Δφ по типам почв')
    fig.tight_layout()
    fig.savefig(OUT / 'delta_phi_by_soil.png', dpi=180)
    plt.close(fig)


def sanity_checks(df):
    checks = {
        'n_rows': int(len(df)),
        'n_cols': int(df.shape[1]),
        'missing_per_column': df.isna().sum().to_dict(),
        'duplicate_rows': int(df.duplicated().sum()),
        'delta_phi_matches_formula': bool(np.allclose(df['delta_phi'], df['phi_DEM'] - df['phi_exp'])),
        'sand_silt_clay_sum_unique': sorted(df.assign(total=df['sand_pct'] + df['silt_pct'] + df['clay_pct'])['total'].unique().tolist()),
        'split_counts': df['split'].value_counts().to_dict(),
    }
    return checks


def main():
    df = pd.read_excel(BASE / 'Структура данных.xlsx', sheet_name='Датасет')
    utf_map = {
        'супесчаный': 'супесчаный',
        'лёгкий суглинок': 'лёгкий суглинок',
        'средний суглинок': 'средний суглинок',
        'тяжёлый суглинок': 'тяжёлый суглинок',
    }
    if 'soil_type' in df:
        df['soil_type'] = df['soil_type'].map(lambda x: utf_map.get(x, x))

    df.to_csv(OUT / 'dataset_export_utf8.csv', index=False, encoding='utf-8-sig')

    checks = sanity_checks(df)
    with open(OUT / 'sanity_checks.json', 'w', encoding='utf-8') as f:
        json.dump(checks, f, ensure_ascii=False, indent=2)

    plot_phi_vs_omega(df)
    plot_delta_by_soil(df)

    tasks = {
        'phi_exp_soil': {
            'target': 'phi_exp',
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk'],
        },
        'phi_dem_surrogate': {
            'target': 'phi_DEM',
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
        },
        'delta_phi_calibration': {
            'target': 'delta_phi',
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
        },
    }

    all_results = []
    best_rows = []
    loo = LeaveOneOut()
    logo = LeaveOneGroupOut()

    for task_name, task in tasks.items():
        X = df[task['features']].copy()
        y = df[task['target']].copy()
        cat_cols = X.select_dtypes(include=['object']).columns.tolist()
        num_cols = [c for c in X.columns if c not in cat_cols]
        preprocessor = build_preprocessor(num_cols, cat_cols)
        task_preds = []

        logo_results = []
        for model_name, model in make_models().items():
            pipe = Pipeline([
                ('preprocess', preprocessor),
                ('model', model),
            ])
            preds = cross_val_predict(pipe, X, y, cv=loo)
            row = {
                'task': task_name,
                'target': task['target'],
                'model': model_name,
            }
            row.update(metrics(y, preds))
            all_results.append(row)
            pred_df = pd.DataFrame({
                'task': task_name,
                'model': model_name,
                'sample_id': df['sample_id'],
                'actual': y,
                'predicted': preds,
                'residual': preds - y,
            })
            task_preds.append(pred_df)

            logo_preds = cross_val_predict(pipe, X, y, cv=logo.split(X, y, groups=df['soil_type']))
            logo_row = {
                'task': task_name,
                'target': task['target'],
                'model': model_name,
            }
            logo_row.update(metrics(y, logo_preds))
            logo_results.append(logo_row)

        res_df = pd.DataFrame([r for r in all_results if r['task'] == task_name]).sort_values(['rmse', 'mae'])
        pd.DataFrame(logo_results).sort_values(['rmse', 'mae']).to_csv(OUT / f'{task_name}_logo_results.csv', index=False, encoding='utf-8-sig')
        best_model_name = res_df.iloc[0]['model']
        best_rows.append(res_df.iloc[0].to_dict())

        best_pred_df = [p for p in task_preds if p['model'].iloc[0] == best_model_name][0]
        best_pred_df.to_csv(OUT / f'{task_name}_best_predictions.csv', index=False, encoding='utf-8-sig')
        plot_pred_vs_actual(best_pred_df, task_name)

        best_pipe = Pipeline([
            ('preprocess', preprocessor),
            ('model', make_models()[best_model_name]),
        ])
        best_pipe.fit(X, y)
        joblib.dump(best_pipe, MODELS_DIR / f'{task_name}__{best_model_name}.joblib')

        transformed_X = best_pipe.named_steps['preprocess'].transform(X)
        try:
            feature_names = best_pipe.named_steps['preprocess'].get_feature_names_out().tolist()
        except Exception:
            feature_names = [f'f{i}' for i in range(transformed_X.shape[1])]

        perm = permutation_importance(best_pipe, X, y, n_repeats=30, random_state=RANDOM_STATE)
        fi = pd.DataFrame({
            'feature': X.columns,
            'importance_mean': perm.importances_mean,
            'importance_std': perm.importances_std,
        }).sort_values('importance_mean', ascending=False)
        fi.to_csv(OUT / f'{task_name}_permutation_importance.csv', index=False, encoding='utf-8-sig')

        split_metrics = {}
        if 'split' in df.columns:
            train_mask = df['split'] == 'train'
            val_mask = df['split'] == 'val'
            test_mask = df['split'] == 'test'
            if train_mask.sum() > 0:
                holdout_pipe = Pipeline([
                    ('preprocess', preprocessor),
                    ('model', make_models()[best_model_name]),
                ])
                holdout_pipe.fit(X.loc[train_mask], y.loc[train_mask])
                for split_name, mask in [('val', val_mask), ('test', test_mask), ('val_test', val_mask | test_mask)]:
                    if mask.sum() > 0:
                        pred_split = holdout_pipe.predict(X.loc[mask])
                        split_metrics[split_name] = metrics(y.loc[mask], pred_split)
        with open(OUT / f'{task_name}_holdout_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(split_metrics, f, ensure_ascii=False, indent=2)

    results_df = pd.DataFrame(all_results).sort_values(['task', 'rmse', 'mae'])
    results_df.to_csv(OUT / 'cv_results.csv', index=False, encoding='utf-8-sig')
    with open(OUT / 'best_models.json', 'w', encoding='utf-8') as f:
        json.dump(best_rows, f, ensure_ascii=False, indent=2)

    summary = {
        'sanity_checks': checks,
        'best_models': best_rows,
    }
    with open(OUT / 'summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print('Done. Results in', OUT)


if __name__ == '__main__':
    main()
