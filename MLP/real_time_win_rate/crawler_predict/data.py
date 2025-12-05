import json
from pathlib import Path
from config import get_args
import numpy as np
import pandas as pd
import random
import torch

def load_state(ckpt_path: Path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}

def transform_stats_to_array(game_stats: dict) -> np.ndarray:
    feature_order_path = Path(__file__).parent / "../kbl_real_time_csv/feature_order.json"
    if not feature_order_path.exists():
        raise FileNotFoundError(f"Feature order file not found: {feature_order_path}")
    feature_order = json.loads(feature_order_path.read_text(encoding="utf-8"))
    row = {
        f"{'H' if team == 'home' else 'A'}_{stat}": value
        for team, stats in game_stats.items()
        for stat, value in stats.items()
    }
    array = np.array([row.get(feature, 0.0) for feature in feature_order if feature not in DEFAULT_DROP_COLS], dtype=np.float32)
    return array

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "winner", "n"]

def load_single_csv(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    drop_df = df.drop(columns=DEFAULT_DROP_COLS)
    return df, drop_df
    
def load_multi_csv(csv_folder_list: list[Path], test_game_keys: list[str] | None) -> tuple[pd.DataFrame, pd.DataFrame, str] | None:
    total_csv_paths: list[Path] = []
    for folder in csv_folder_list:
        csv_paths = list(folder.glob("*.csv"))
        total_csv_paths.extend(csv_paths)
    
    args = get_args()
    
    if test_game_keys is not None:
        total_csv_paths = [path for path in total_csv_paths if path.stem in test_game_keys]
        if not total_csv_paths:
            print("테스트용 CSV 파일이 없습니다.")
            return None
    
    random.seed(args.seed)
    specific_csv_path = random.choice(total_csv_paths)
    gameKey = specific_csv_path.stem
    print(f"선택된 CSV 파일: {specific_csv_path}")
    
    df, drop_df = load_single_csv(csv_path=specific_csv_path)

    return df, drop_df, gameKey

if __name__ == "__main__":
    csv_folder_list = [
        Path("../kbl_real_time_csv/2021-2022"),
        Path("../kbl_real_time_csv/2022-2023"),
        Path("../kbl_real_time_csv/2023-2024"),
        Path("../kbl_real_time_csv/2024-2025"),
    ]
    
    test_game_keys = [
        "S45G01N115",
        "S43G01N105",
        "S45G01N40",
        "S41G01N184",
        "S41G01N22",
        "S43G01N234",
        "S43G01N166",
        "S45G01N53",
    ]
    
    df, drop_df, gameKey = load_multi_csv(csv_folder_list, test_game_keys)
    
    print("데이터 로드 완료.")
    print(f"총 데이터 개수: {df.shape[0]}")
    print(f"특징 개수: {len(df['gameKey'].values)}")
    print(f"선택된 게임 키: {gameKey}")
    print(drop_df.shape)