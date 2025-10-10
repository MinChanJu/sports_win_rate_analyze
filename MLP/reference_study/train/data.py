from sklearn.model_selection import train_test_split
from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "H_TEAM", "A_TEAM", "quarter"]

def _prepare_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    drop_cols = [c for c in DEFAULT_DROP_COLS if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})
    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)
    return X, y

def load_single_csv(path: str | Path) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.seed

    df = pd.read_csv(path)
    X, y = _prepare_xy(df)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=test_size + valid_size, random_state=seed, stratify=y)
    X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=test_size / (test_size + valid_size), random_state=seed, stratify=y_temp)
    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }

def load_multi_csv(paths: list[str | Path]) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.seed

    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    X, y = _prepare_xy(df)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=test_size + valid_size, random_state=seed, stratify=y)
    X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=test_size / (test_size + valid_size), random_state=seed, stratify=y_temp)
    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }