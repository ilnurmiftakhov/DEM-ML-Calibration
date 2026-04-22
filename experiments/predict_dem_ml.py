import argparse
from pathlib import Path

import joblib
import pandas as pd

BASE = Path(__file__).resolve().parent
MODELS_DIR = BASE / 'models'

MODEL_MAP = {
    'phi_exp_soil': MODELS_DIR / 'phi_exp_soil__gpr.joblib',
    'phi_dem_surrogate': MODELS_DIR / 'phi_dem_surrogate__xgboost.joblib',
    'delta_phi_calibration': MODELS_DIR / 'delta_phi_calibration__dummy_mean.joblib',
}


def main():
    parser = argparse.ArgumentParser(description='Predict DEM/ML targets from a CSV file.')
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--task', required=True, choices=MODEL_MAP.keys())
    parser.add_argument('--output', default=None, help='Path to save predictions CSV')
    args = parser.parse_args()

    model = joblib.load(MODEL_MAP[args.task])
    df = pd.read_csv(args.input)
    preds = model.predict(df)
    out = df.copy()
    out['prediction'] = preds

    output = Path(args.output) if args.output else Path(args.input).with_name(Path(args.input).stem + f'__{args.task}_predictions.csv')
    out.to_csv(output, index=False, encoding='utf-8-sig')
    print(f'Saved predictions to {output}')


if __name__ == '__main__':
    main()
