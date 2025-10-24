from pathlib import Path
import pandas as pd
import torch

def load_state(ckpt_path: Path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}

def load_csv_path(csv_path: Path, start: int, end: int | None, team_code: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)
    if end is None: df = df.iloc[start:]
    else: df = df.iloc[start:end]
    
    drop_df = df.drop(columns=["gameKey", "seasonName", "date", "quarter", "winner"])
    drop_df["H_TEAM"] = drop_df["H_TEAM"].map(team_code)
    drop_df["A_TEAM"] = drop_df["A_TEAM"].map(team_code)
    
    return df, drop_df

def load_csv_paths(csv_path_list: list[Path], start: int, end: int | None, team_code: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_list = [load_csv_path(csv_path, start, end, team_code) for csv_path in csv_path_list]
    df = pd.concat([d[0] for d in df_list], ignore_index=True)
    drop_df = pd.concat([d[1] for d in df_list], ignore_index=True)
    return df, drop_df