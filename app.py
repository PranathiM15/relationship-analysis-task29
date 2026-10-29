from __future__ import annotations

import base64
import io
import secrets
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Works without a desktop display.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent
DATASETS = ROOT / 'datasets'
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB CSV upload limit
UPLOADS: dict[str, pd.DataFrame] = {}

BUILT_IN_DATASETS = {
    'iris_dataset.csv': {'label': 'Iris dataset', 'description': 'Flower measurements across three Iris species.'},
    'housing_dataset.csv': {'label': 'Housing dataset', 'description': 'Example home sizes, features, distance, and prices.'},
    'student_performance_dataset.csv': {'label': 'Student performance', 'description': 'Example study habits and student scores.'},
}


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column labels and remove completely blank rows/columns."""
    df = df.copy()
    df.columns = [str(c).strip() or f'column_{i+1}' for i, c in enumerate(df.columns)]
    df = df.dropna(how='all').dropna(axis=1, how='all')
    # Make duplicate names distinct so the column selectors stay predictable.
    seen: dict[str, int] = {}
    unique = []
    for col in df.columns:
        seen[col] = seen.get(col, 0) + 1
        unique.append(col if seen[col] == 1 else f'{col}_{seen[col]}')
    df.columns = unique
    return df


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=[np.number]).columns.tolist()


def describe_pattern(r: float) -> tuple[str, str]:
    if r >= 0.70:
        return 'Strong positive', 'As one variable increases, the other tends to increase clearly.'
    if r >= 0.30:
        return 'Moderate positive', 'The variables tend to increase together, with some spread.'
    if r > -0.30:
        return 'Weak / no linear pattern', 'There is little clear straight-line relationship in these observations.'
    if r > -0.70:
        return 'Moderate negative', 'As one variable increases, the other tends to decrease.'
    return 'Strong negative', 'As one variable increases, the other tends to decrease clearly.'


def get_frame(dataset: str | None, upload_id: str | None) -> tuple[pd.DataFrame | None, str | None]:
    if upload_id:
        df = UPLOADS.get(upload_id)
        return (df.copy(), None) if df is not None else (None, 'That uploaded file has expired. Upload it again.')
    if dataset not in BUILT_IN_DATASETS:
        return None, 'Choose one of the included datasets.'
    path = DATASETS / dataset
    if not path.is_file():
        return None, f'The dataset file is missing: {dataset}'
    try:
        return clean_dataframe(pd.read_csv(path)), None
    except Exception as exc:
        return None, f'Could not read the CSV: {exc}'


@app.get('/')
def index():
    return render_template('index.html', datasets=BUILT_IN_DATASETS)


@app.get('/api/dataset')
def dataset_info():
    dataset = request.args.get('name', 'iris_dataset.csv')
    df, error = get_frame(dataset, None)
    if error:
        return jsonify({'error': error}), 400
    assert df is not None
    nums = numeric_columns(df)
    return jsonify({
        'name': BUILT_IN_DATASETS[dataset]['label'],
        'description': BUILT_IN_DATASETS[dataset]['description'],
        'columns': nums,
        'rows': int(len(df)),
        'column_count': int(len(df.columns)),
        'preview': df.head(5).astype(object).where(pd.notna(df.head(5)), None).to_dict(orient='records'),
    })


@app.post('/api/upload')
def upload_csv():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'Choose a CSV file first.'}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Please upload a .csv file.'}), 400
    try:
        df = clean_dataframe(pd.read_csv(file, low_memory=False))
    except Exception as exc:
        return jsonify({'error': f'Could not read that CSV: {exc}'}), 400
    if df.empty:
        return jsonify({'error': 'The CSV has no data rows.'}), 400
    nums = numeric_columns(df)
    if len(nums) < 2:
        return jsonify({'error': 'Your CSV needs at least two numeric columns to make a scatter plot.'}), 400
    token = secrets.token_urlsafe(12)
    UPLOADS[token] = df
    # Keep this small local training app from holding many large uploads forever.
    while len(UPLOADS) > 8:
        UPLOADS.pop(next(iter(UPLOADS)))
    return jsonify({
        'upload_id': token,
        'name': Path(file.filename).name,
        'columns': nums,
        'rows': int(len(df)),
        'column_count': int(len(df.columns)),
        'preview': df.head(5).astype(object).where(pd.notna(df.head(5)), None).to_dict(orient='records'),
        'description': 'Your CSV is being analyzed locally by this app.',
    })


@app.post('/api/analyze')
def analyze():
    payload = request.get_json(silent=True) or {}
    df, error = get_frame(payload.get('dataset'), payload.get('upload_id'))
    if error:
        return jsonify({'error': error}), 400
    assert df is not None
    x_col, y_col = payload.get('x'), payload.get('y')
    nums = numeric_columns(df)
    if x_col not in nums or y_col not in nums:
        return jsonify({'error': 'Select two numeric columns from the current dataset.'}), 400
    if x_col == y_col:
        return jsonify({'error': 'Choose two different columns for the X and Y axes.'}), 400

    pair = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(pair) < 2:
        return jsonify({'error': 'At least two rows with valid numbers are needed.'}), 400
    x = pair[x_col].astype(float).to_numpy()
    y = pair[y_col].astype(float).to_numpy()
    corr = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 0 and np.std(y) > 0 else 0.0
    if not np.isfinite(corr):
        corr = 0.0
    pattern, interpretation = describe_pattern(corr)

    # Plot in memory, so no output files accumulate in the project folder.
    fig, ax = plt.subplots(figsize=(8.8, 5.0), dpi=115)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#fbfcff')
    ax.scatter(x, y, s=42, alpha=.78, c='#556cf6', edgecolors='white', linewidths=.65, zorder=3)
    if np.std(x) > 0:
        slope, intercept = np.polyfit(x, y, 1)
        xx = np.linspace(float(np.min(x)), float(np.max(x)), 100)
        ax.plot(xx, slope * xx + intercept, color='#ff865d', linewidth=2.3, zorder=2, label='Trend line')
        ax.legend(frameon=False, loc='best')
    ax.set_xlabel(x_col.replace('_', ' ').title(), color='#43506c', labelpad=10)
    ax.set_ylabel(y_col.replace('_', ' ').title(), color='#43506c', labelpad=10)
    ax.grid(True, color='#e9edf6', linewidth=.8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#dce2ef')
    ax.tick_params(colors='#7a849c', labelsize=9)
    ax.margins(x=.06, y=.12)
    fig.tight_layout(pad=2)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    image = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')

    sample_size = len(pair)
    direction = 'increase together' if corr > .30 else ('move in opposite directions' if corr < -.30 else 'show a weak straight-line pattern')
    observations = [
        f'The plot uses {sample_size:,} valid paired observations from “{x_col}” and “{y_col}”.',
        f'Pearson correlation is {corr:+.3f}; the variables {direction}.',
        f'“{x_col}” ranges from {np.min(x):,.3g} to {np.max(x):,.3g}; “{y_col}” ranges from {np.min(y):,.3g} to {np.max(y):,.3g}.',
        'Correlation describes an association, not proof that one variable causes the other.'
    ]
    return jsonify({
        'image': image, 'correlation': corr, 'pattern': pattern,
        'interpretation': interpretation, 'observations': observations,
        'rows_used': sample_size, 'x': x_col, 'y': y_col,
    })


@app.errorhandler(413)
def too_large(_error):
    return jsonify({'error': 'That file is larger than 10 MB. Please upload a smaller CSV.'}), 413


if __name__ == '__main__':
    print('\nScatterLab is ready. Open http://127.0.0.1:5000 in your browser.')
    print('Press Ctrl+C in this terminal to stop the server.\n')
    app.run(debug=False, host='127.0.0.1', port=5000)
