import os
import pandas as pd

def download_kaggle_dataset(dataset_slug: str, download_path: str = "data/kaggle") -> str:
    search_name = dataset_slug.split('/')[-1] if '/' in dataset_slug else dataset_slug
    base = download_path
    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(".csv"):
                return os.path.join(root, file)
    os.makedirs(download_path, exist_ok=True)
    try:
        import opendatasets as od
        od.download(f"https://www.kaggle.com/datasets/{dataset_slug}", data_dir=download_path)
    except Exception as e:
        raise RuntimeError(f"Kaggle download failed: {e}")
    for root, dirs, files in os.walk(download_path):
        for file in files:
            if file.endswith(".csv"):
                return os.path.join(root, file)
    raise FileNotFoundError("No CSV found.")

def summarize_dataset(df: pd.DataFrame) -> dict:
    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns},
        "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
        "sample_rows": df.head(5).to_dict(orient="records"),
        "numeric_stats": {},
        "categorical_stats": {}
    }
    for col in df.select_dtypes(include="number").columns:
        summary["numeric_stats"][col] = {
            "min": round(float(df[col].min()), 4),
            "max": round(float(df[col].max()), 4),
            "mean": round(float(df[col].mean()), 4),
            "std": round(float(df[col].std()), 4),
            "median": round(float(df[col].median()), 4)
        }
    for col in df.select_dtypes(include="object").columns:
        summary["categorical_stats"][col] = {
            "unique_values": int(df[col].nunique()),
            "top_values": df[col].value_counts().head(5).to_dict()
        }
    return summary

def extract_subset(df: pd.DataFrame, condition: str = None, columns: list = None, limit: int = None) -> pd.DataFrame:
    result = df.copy()
    if columns:
        result = result[columns]
    if condition:
        result = result.query(condition)
    if limit:
        result = result.head(limit)
    return result