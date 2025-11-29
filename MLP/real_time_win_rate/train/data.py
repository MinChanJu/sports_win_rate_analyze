import random
from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "winner", "n"]

def load_single_csv(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    
    X = df.drop(columns=DEFAULT_DROP_COLS).values.astype(np.float32)
    y = df["winner"].map({"home": 0, "away": 1}).values.astype(np.int64)

    return X, y

def load_multi_csv(csv_folder_list: list[Path]) -> dict[str, dict[str, np.ndarray]]:
    total_csv_paths = []
    for folder in csv_folder_list:
        csv_paths = list(folder.glob("*.csv"))
        total_csv_paths.extend(csv_paths)

    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.split_seed
    
    random.seed(seed)
    random.shuffle(total_csv_paths)
    
    n_total = len(total_csv_paths)
    n_test = int(n_total * test_size)
    n_valid = int(n_total * valid_size)
    
    test_csv_paths = total_csv_paths[:n_test]
    valid_csv_paths = total_csv_paths[n_test:n_test + n_valid]
    train_csv_paths = total_csv_paths[n_test + n_valid:]
    
    X_train_list, y_train_list = [], []
    X_valid_list, y_valid_list = [], []
    X_test_list, y_test_list = [], []
    
    for csv_path in train_csv_paths:
        X, y = load_single_csv(csv_path=csv_path)
        X_train_list.append(X)
        y_train_list.append(y)
    
    for csv_path in valid_csv_paths:
        X, y = load_single_csv(csv_path=csv_path)
        X_valid_list.append(X)
        y_valid_list.append(y)
    
    for csv_path in test_csv_paths:
        X, y = load_single_csv(csv_path=csv_path)
        X_test_list.append(X)
        y_test_list.append(y)

    X_train = np.vstack(X_train_list)
    y_train = np.hstack(y_train_list)
    
    X_valid = np.vstack(X_valid_list)
    y_valid = np.hstack(y_valid_list)
    
    X_test = np.vstack(X_test_list)
    y_test = np.hstack(y_test_list)

    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }
    
if __name__ == "__main__":
    data = load_multi_csv([
        Path("../kbl_real_time_csv/2021-2022"),
        Path("../kbl_real_time_csv/2022-2023"),
        Path("../kbl_real_time_csv/2023-2024"),
        Path("../kbl_real_time_csv/2024-2025"),
    ])
    for split in ["train", "valid", "test"]:
        print(f"{split}: X={data[split]['X'].shape}, y={data[split]['y'].shape}")