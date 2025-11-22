from sklearn.model_selection import train_test_split
from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "quarter", "split"]

def _prepare_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    drop_cols = [c for c in DEFAULT_DROP_COLS if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})
    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)
    return X, y

def load_single_csv(path: str | Path, seed: int = None) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.split_seed if seed is None else seed

    df = pd.read_csv(path)

    y = df["winner"]                         # 라벨 컬럼명에 맞게 수정
    X = df.drop(columns=["winner"])          # 라벨 제외하고 모두 X

    # ----------------------------
    # 2) train + temp 분리
    # temp → valid + test 로 다시 나눔
    # ----------------------------
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size = test_size + valid_size,          # valid + test 를 먼저 분리
        random_state = seed,
        shuffle = True
    )

    # temp → valid/test 비율 계산
    valid_ratio = valid_size / (test_size + valid_size)

    X_valid, X_test, y_valid, y_test = train_test_split(
        X_temp, y_temp,
        test_size = 1 - valid_ratio,        # valid:  test_size =? → 비율 계산됨
        random_state = seed,
        shuffle = True
    )

    # ----------------------------
    # 3) Numpy 로 변환
    # ----------------------------
    X_train, y_train = _prepare_xy(pd.concat([X_train, y_train], axis=1))
    X_valid, y_valid = _prepare_xy(pd.concat([X_valid, y_valid], axis=1))
    X_test,  y_test  = _prepare_xy(pd.concat([X_test,  y_test],  axis=1))

    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }

def load_multi_csv(paths: list[str | Path]) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    seed = args.split_seed
    
    X_train = y_train = X_valid = y_valid = X_test = y_test = None

    for i, path in enumerate(paths):
        if not Path(path).exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        data_path = load_single_csv(path, seed + i)  # 시드 변경하여 데이터 분할 다르게

        X_train = np.vstack([X_train, data_path["train"]["X"]]) if X_train is not None else data_path["train"]["X"]
        y_train = np.hstack([y_train, data_path["train"]["y"]]) if y_train is not None else data_path["train"]["y"]
        X_valid = np.vstack([X_valid, data_path["valid"]["X"]]) if X_valid is not None else data_path["valid"]["X"]
        y_valid = np.hstack([y_valid, data_path["valid"]["y"]]) if y_valid is not None else data_path["valid"]["y"]
        X_test  = np.vstack([X_test, data_path["test"]["X"]]) if X_test is not None else data_path["test"]["X"]
        y_test  = np.hstack([y_test, data_path["test"]["y"]]) if y_test is not None else data_path["test"]["y"]

    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }
    
if __name__ == "__main__":
    data = load_multi_csv([
        "../kbl_data_quarter_csv/2021-2022.csv",
        "../kbl_data_quarter_csv/2022-2023.csv",
        "../kbl_data_quarter_csv/2023-2024.csv",
        "../kbl_data_quarter_csv/2024-2025.csv",
    ])
    for split in ["train", "valid", "test"]:
        print(f"{split}: X={data[split]['X'].shape}, y={data[split]['y'].shape}")