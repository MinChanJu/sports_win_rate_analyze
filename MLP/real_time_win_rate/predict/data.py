from pathlib import Path
import random
import numpy as np
import pandas as pd
import torch

def load_state(ckpt_path: Path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "winner", "n"]

def load_single_csv(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)
    drop_df = df.drop(columns=DEFAULT_DROP_COLS)
    
    return drop_df, df
    
def load_multi_csv(csv_folder_list: list[Path], config: dict | None) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    total_csv_paths = []
    for folder in csv_folder_list:
        csv_paths = list(folder.glob("*.csv"))
        total_csv_paths.extend(csv_paths)
    
    if config is not None:
        test_size = config.get("test_size")
        seed = config.get("split_seed")
        
        if (test_size is None) or (seed is None):
            print("config에 test_size, split_seed 값이 필요합니다.")
            return None
        
        random.seed(seed)
        random.shuffle(total_csv_paths)
        
        n_total = len(total_csv_paths)
        n_test = int(n_total * test_size)
        
        test_csv_paths = total_csv_paths[:n_test]
        total_csv_paths = test_csv_paths
    
    drop_df_list = []
    df_list = []
        
    for csv_path in total_csv_paths:
        drop_df, df = load_single_csv(csv_path=csv_path)
        
        drop_df_list.append(drop_df)
        df_list.append(df)
        
    drop_df_all = pd.concat(drop_df_list, ignore_index=True)
    df_all = pd.concat(df_list, ignore_index=True)

    return drop_df_all, df_all