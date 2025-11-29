import random
from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np

DEFAULT_DROP_COLS = ["seasonName", "date"]

def load_single_csv(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    
    df = df.drop(columns=DEFAULT_DROP_COLS)
    df["winner"] = df["winner"].map({"home": 0, "away": 1}).astype(np.int64)
    
    return df

def load_multi_csv(csv_path_list: list[Path]) -> dict[str, dict[str, np.ndarray]]:
    df_list = [load_single_csv(csv_path) for csv_path in csv_path_list]
    df_all = pd.concat(df_list, ignore_index=True)
    game_keys = list(df_all["gameKey"])

    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.split_seed
    
    random.seed(seed)
    random.shuffle(game_keys)
    
    n_total = len(game_keys)
    n_test = int(n_total * test_size)
    n_valid = int(n_total * valid_size)
    
    # ----- 데이터 분할 -----
    # Train 데이터
    train_game_keys = set(game_keys[n_test + n_valid:])
    train_df = df_all[df_all["gameKey"].isin(train_game_keys)].reset_index(drop=True)
    X_train = train_df.drop(columns=["winner", "gameKey"]).values.astype(np.float32)
    y_train = train_df["winner"].values.astype(np.int64)
    
    # Valid 데이터
    valid_game_keys = set(game_keys[n_test:n_test + n_valid])
    valid_df = df_all[df_all["gameKey"].isin(valid_game_keys)].reset_index(drop=True)
    X_valid = valid_df.drop(columns=["winner", "gameKey"]).values.astype(np.float32)
    y_valid = valid_df["winner"].values.astype(np.int64)
    
    # Test 데이터
    test_game_keys = set(game_keys[:n_test])
    test_df = df_all[df_all["gameKey"].isin(test_game_keys)].reset_index(drop=True)
    X_test = test_df.drop(columns=["winner", "gameKey"]).values.astype(np.float32)
    y_test = test_df["winner"].values.astype(np.int64)

    return {
        "train": {"X": X_train, "y": y_train, "gameKey": train_game_keys},
        "valid": {"X": X_valid, "y": y_valid, "gameKey": valid_game_keys},
        "test": {"X": X_test, "y": y_test, "gameKey": test_game_keys},
    }

if __name__ == "__main__":
    data = load_multi_csv([
        Path("../kbl_data_csv/2021-2022.csv"),
        Path("../kbl_data_csv/2022-2023.csv"),
        Path("../kbl_data_csv/2023-2024.csv"),
        Path("../kbl_data_csv/2024-2025.csv"),
    ])
    for split in ["train", "valid", "test"]:
        print(f"{split}: X={data[split]['X'].shape}, y={data[split]['y'].shape}, gameKey count={len(data[split]['gameKey'])}")