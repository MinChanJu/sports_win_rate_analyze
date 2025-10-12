from config import get_args
from pathlib import Path
import pandas as pd
import numpy as np
import json

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "quarter"]
team_code_path = Path(__file__).parent / "teamcode.json"

def _prepare_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    if team_code_path.exists(): data = json.loads(team_code_path.read_text())
    else: data = {"team_code": {}, "idx": 0}

    team_code = data.get("team_code", {})
    next_idx = data.get("idx", 0)

    teams_in_df = pd.concat([df["H_TEAM"], df["A_TEAM"]]).unique()
    for team in teams_in_df:
        if team not in team_code:
            team_code[team] = next_idx
            next_idx += 1

    data["team_code"] = team_code
    data["idx"] = next_idx
    
    team_code_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    drop_cols = [c for c in DEFAULT_DROP_COLS if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})
    df["H_TEAM"] = df["H_TEAM"].map(team_code)
    df["A_TEAM"] = df["A_TEAM"].map(team_code)
    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)
    return X, y

def load_single_csv(path: str | Path, seed: int = None) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    test_size = args.test_size
    valid_size = args.valid_size
    seed = args.seed if seed is None else seed

    df = pd.read_csv(path)
    
    # 1️⃣ 고유 gameKey 목록 추출
    unique_keys = df["gameKey"].unique()
    n_total = len(unique_keys)   # 예: 270경기
    n_valid = int(n_total * valid_size)  # 27
    n_test  = int(n_total * test_size)   # 54
    n_train = n_total - n_valid - n_test  # 189
    
    # 3️⃣ 고유 gameKey를 랜덤 섞기
    shuffled = pd.Series(unique_keys).sample(frac=1, random_state=seed).tolist()

    # 4️⃣ 분할
    train_keys = shuffled[:n_train]
    valid_keys = shuffled[n_train:n_train+n_valid]
    test_keys  = shuffled[n_train+n_valid:]
    
    train_df = df[df["gameKey"].isin(train_keys)]
    valid_df = df[df["gameKey"].isin(valid_keys)]
    test_df  = df[df["gameKey"].isin(test_keys)]
    
    X_train, y_train = _prepare_xy(train_df)
    X_valid, y_valid = _prepare_xy(valid_df)
    X_test,  y_test  = _prepare_xy(test_df)
    
    return {
        "train": {"X": X_train, "y": y_train},
        "valid": {"X": X_valid, "y": y_valid},
        "test": {"X": X_test, "y": y_test},
    }

def load_multi_csv(paths: list[str | Path]) -> dict[str, dict[str, np.ndarray]]:
    args = get_args()
    seed = args.seed
    
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