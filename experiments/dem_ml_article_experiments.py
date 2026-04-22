import json
import warnings
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
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut, LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings('ignore')

RANDOM_STATE = 42
rng = np.random.default_rng(RANDOM_STATE)
BASE = Path('.')
OUT = BASE / 'experiments' / 'article_results'
OUT.mkdir(parents=True, exist_ok=True)


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown='ignore', sparse=False)


def preprocessor_for(X):
    cat_cols = X.select_dtypes(include=['object']).columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]
    return ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imp', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
            ]), num_cols),
            ('cat', Pipeline([
                ('imp', SimpleImputer(strategy='most_frequent')),
                ('ohe', make_ohe()),
            ]), cat_cols),
        ],
        sparse_threshold=0,
    )


def metrics(y_true, y_pred):
    return {
        'rmse': float(mean_squared_error(y_true, y_pred, squared=False)),
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'r2': float(r2_score(y_true, y_pred)),
    }


def models():
    gpr_kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(length_scale=1.0) + WhiteKernel(noise_level=1.0)
    return {
        'dummy_mean': DummyRegressor(strategy='mean'),
        'ridge': Ridge(alpha=1.0),
        'random_forest': RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE),
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


def make_pipe(X, model):
    return Pipeline([
        ('prep', preprocessor_for(X)),
        ('model', model),
    ])


def evaluate_task(df, features, target):
    X = df[features].copy()
    y = df[target].copy()
    loo = LeaveOneOut()
    logo = LeaveOneGroupOut()
    rows = []
    for name, model in models().items():
        pipe = make_pipe(X, model)
        pred_loo = cross_val_predict(pipe, X, y, cv=loo)
        pred_logo = cross_val_predict(pipe, X, y, cv=logo.split(X, y, groups=df['soil_type']))
        row = {'model': name, 'target': target}
        row.update({f'loo_{k}': v for k, v in metrics(y, pred_loo).items()})
        row.update({f'logo_{k}': v for k, v in metrics(y, pred_logo).items()})
        rows.append(row)
    return pd.DataFrame(rows).sort_values(['loo_rmse', 'loo_mae'])


def bootstrap_best_model(df, features, target, model_name, n_boot=100):
    X_all = df[features].copy()
    y_all = df[target].copy().reset_index(drop=True)
    n = len(df)
    rows = []
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        X = X_all.iloc[idx].reset_index(drop=True)
        y = y_all.iloc[idx].reset_index(drop=True)
        pipe = make_pipe(X, models()[model_name])
        try:
            pred = cross_val_predict(pipe, X, y, cv=LeaveOneOut())
            m = metrics(y, pred)
            m['bootstrap_id'] = int(b)
            rows.append(m)
        except Exception:
            continue
    return pd.DataFrame(rows)


def summarise_bootstrap(df_boot):
    out = {}
    for col in ['rmse', 'mae', 'r2']:
        vals = df_boot[col].dropna().values
        out[col] = {
            'mean': float(np.mean(vals)),
            'ci_2_5': float(np.quantile(vals, 0.025)),
            'ci_97_5': float(np.quantile(vals, 0.975)),
        }
    return out


def plot_bootstrap_distributions(boot_tables):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    task_order = ['phi_exp_soil', 'phi_dem_surrogate', 'delta_phi_calibration']
    metric_names = ['rmse', 'mae', 'r2']
    for ax, metric in zip(axes, metric_names):
        data = [boot_tables[t][metric].dropna().values for t in task_order]
        ax.boxplot(data, labels=task_order)
        ax.set_title(f'Bootstrap-распределение {metric.upper()}')
        ax.tick_params(axis='x', rotation=20)
    fig.tight_layout()
    fig.savefig(OUT / 'bootstrap_metric_distributions.png', dpi=180)
    plt.close(fig)


def ablation_phi_dem(df):
    configs = {
        'full': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
        'soil_only': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk'],
        'dem_only': ['model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
        'no_omega': ['soil_type', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
        'no_friction': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'd_p'],
    }
    rows = []
    y = df['phi_DEM'].copy()
    for name, features in configs.items():
        X = df[features].copy()
        pipe = make_pipe(X, models()['xgboost'])
        pred_loo = cross_val_predict(pipe, X, y, cv=LeaveOneOut())
        pred_logo = cross_val_predict(pipe, X, y, cv=LeaveOneGroupOut().split(X, y, groups=df['soil_type']))
        row = {'config': name, 'n_features': len(features)}
        row.update({f'loo_{k}': v for k, v in metrics(y, pred_loo).items()})
        row.update({f'logo_{k}': v for k, v in metrics(y, pred_logo).items()})
        rows.append(row)
    res = pd.DataFrame(rows).sort_values('loo_rmse')
    res.to_csv(OUT / 'phi_dem_ablation.csv', index=False, encoding='utf-8-sig')

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(res['config'], res['loo_mae'], color='#4c78a8')
    ax.set_ylabel('LOOCV MAE, °')
    ax.set_title('Ablation для surrogate-модели φ_DEM (XGBoost)')
    ax.tick_params(axis='x', rotation=20)
    fig.tight_layout()
    fig.savefig(OUT / 'phi_dem_ablation_mae.png', dpi=180)
    plt.close(fig)
    return res


def indirect_vs_direct_delta(df):
    features_exp = ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk']
    features_dem = ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p']

    X_exp = df[features_exp].copy()
    X_dem = df[features_dem].copy()
    y_exp = df['phi_exp'].copy()
    y_dem = df['phi_DEM'].copy()
    y_delta = df['delta_phi'].copy()

    pred_exp = cross_val_predict(make_pipe(X_exp, models()['gpr']), X_exp, y_exp, cv=LeaveOneOut())
    pred_dem = cross_val_predict(make_pipe(X_dem, models()['xgboost']), X_dem, y_dem, cv=LeaveOneOut())
    indirect = pred_dem - pred_exp
    direct = cross_val_predict(make_pipe(X_dem, models()['dummy_mean']), X_dem, y_delta, cv=LeaveOneOut())

    rows = []
    for name, pred in [('indirect_phi_dem_minus_phi_exp', indirect), ('direct_dummy_delta', direct)]:
        row = {'approach': name}
        row.update(metrics(y_delta, pred))
        rows.append(row)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / 'delta_indirect_vs_direct.csv', index=False, encoding='utf-8-sig')

    comp = pd.DataFrame({
        'sample_id': df['sample_id'],
        'delta_actual': y_delta,
        'delta_indirect': indirect,
        'delta_direct': direct,
    })
    comp.to_csv(OUT / 'delta_indirect_vs_direct_predictions.csv', index=False, encoding='utf-8-sig')

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(comp))
    ax.plot(x, comp['delta_actual'], 'o-', label='Факт')
    ax.plot(x, comp['delta_indirect'], 's--', label='Непрямой прогноз')
    ax.plot(x, comp['delta_direct'], 'x--', label='Прямой baseline')
    ax.set_xticks(x)
    ax.set_xticklabels(comp['sample_id'], rotation=45, ha='right')
    ax.set_ylabel('Δφ, °')
    ax.set_title('Сравнение прямого и непрямого прогноза ошибки калибровки')
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / 'delta_indirect_vs_direct.png', dpi=180)
    plt.close(fig)
    return res


def soilwise_error_plot(df):
    df_pred = pd.read_csv(BASE / 'experiments' / 'results' / 'phi_dem_surrogate_best_predictions.csv')
    merged = df[['sample_id', 'soil_type']].merge(df_pred[['sample_id', 'actual', 'predicted']], on='sample_id')
    merged['abs_error'] = (merged['predicted'] - merged['actual']).abs()
    g = merged.groupby('soil_type')['abs_error'].agg(['mean', 'max', 'count']).reset_index()
    g.to_csv(OUT / 'phi_dem_error_by_soil.csv', index=False, encoding='utf-8-sig')

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(g['soil_type'], g['mean'], color='#f58518')
    ax.set_ylabel('Средняя |ошибка|, °')
    ax.set_title('Ошибка surrogate-модели φ_DEM по типам почв')
    ax.tick_params(axis='x', rotation=20)
    fig.tight_layout()
    fig.savefig(OUT / 'phi_dem_error_by_soil.png', dpi=180)
    plt.close(fig)
    return g


def main():
    df = pd.read_excel(BASE / 'Структура данных.xlsx', sheet_name='Датасет')

    task_defs = {
        'phi_exp_soil': {
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk'],
            'target': 'phi_exp',
            'best_model': 'gpr',
        },
        'phi_dem_surrogate': {
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
            'target': 'phi_DEM',
            'best_model': 'xgboost',
        },
        'delta_phi_calibration': {
            'features': ['soil_type', 'omega', 'sand_pct', 'silt_pct', 'clay_pct', 'rho_bulk', 'model_n', 'model_t', 'model_c', 'k_d', 'kd_k', 'e', 'd_p'],
            'target': 'delta_phi',
            'best_model': 'dummy_mean',
        },
    }

    summary_rows = []
    boot_tables = {}

    for task_name, task in task_defs.items():
        res = evaluate_task(df, task['features'], task['target'])
        res.to_csv(OUT / f'{task_name}_model_compare.csv', index=False, encoding='utf-8-sig')
        boot = bootstrap_best_model(df, task['features'], task['target'], task['best_model'])
        boot.to_csv(OUT / f'{task_name}_bootstrap_metrics.csv', index=False, encoding='utf-8-sig')
        boot_tables[task_name] = boot
        summary = summarise_bootstrap(boot)
        summary_rows.append({
            'task': task_name,
            'best_model': task['best_model'],
            'loo_rmse_mean': summary['rmse']['mean'],
            'loo_rmse_ci_2_5': summary['rmse']['ci_2_5'],
            'loo_rmse_ci_97_5': summary['rmse']['ci_97_5'],
            'loo_mae_mean': summary['mae']['mean'],
            'loo_mae_ci_2_5': summary['mae']['ci_2_5'],
            'loo_mae_ci_97_5': summary['mae']['ci_97_5'],
            'loo_r2_mean': summary['r2']['mean'],
            'loo_r2_ci_2_5': summary['r2']['ci_2_5'],
            'loo_r2_ci_97_5': summary['r2']['ci_97_5'],
        })

    pd.DataFrame(summary_rows).to_csv(OUT / 'bootstrap_summary.csv', index=False, encoding='utf-8-sig')
    plot_bootstrap_distributions(boot_tables)
    ablation_phi_dem(df)
    indirect_vs_direct_delta(df)
    soilwise_error_plot(df)

    with open(OUT / 'article_experiment_summary.json', 'w', encoding='utf-8') as f:
        json.dump({'tasks': summary_rows}, f, ensure_ascii=False, indent=2)

    print('Article experiments saved to', OUT)


if __name__ == '__main__':
    main()
