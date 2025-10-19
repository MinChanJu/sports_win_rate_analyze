from predict import predict_one
from pathlib import Path
from config import get_args
import pandas as pd
import numpy as np
import json
import sys

def main():
    args = get_args()
    team_code_path = Path(args.team_code_path)
    if not team_code_path.exists():
        print(f"teamcode.json 파일이 없습니다. 먼저 학습을 수행하세요. 경로: {team_code_path}")
        sys.exit(1)
            
    data = json.loads(team_code_path.read_text())
    team_code = data.get("team_code", {})
    
    ckpt = Path(args.ckpt_path) / args.model_filename
    if not ckpt.exists():
        print(f"체크포인트 파일이 없습니다: {ckpt}")
        sys.exit(1)

    df = pd.read_csv(args.predict_csv)
    if ':' in args.predict_range:
        start_str, end_str = args.predict_range.split(':')
        start_idx = int(start_str) if start_str else 0
        end_idx = int(end_str) if end_str else len(df)
        df = df.iloc[start_idx:end_idx]

    drop_df = df.drop(columns=["gameKey", "seasonName", "date", "quarter", "winner"])
    drop_df["H_TEAM"] = drop_df["H_TEAM"].map(team_code)
    drop_df["A_TEAM"] = drop_df["A_TEAM"].map(team_code)
    result = {}
    for idx in df.index:
        gameKey = df.loc[idx, "gameKey"]
        quarter = df.loc[idx, "quarter"]
        x_row = np.asarray(drop_df.loc[idx], dtype=np.float32)
        home_prob, away_prob = predict_one(ckpt, x_row)
        if gameKey not in result: result[gameKey] = {"metainfo": {"home": df.loc[idx, "H_TEAM"], "away": df.loc[idx, "A_TEAM"], "winner": df.loc[idx, "winner"], "quarters": []}}
        result[gameKey]["metainfo"]["quarters"].append(quarter)
        result[gameKey][quarter] = {
            "home": home_prob,
            "away": away_prob,
            "home_score": int(df.loc[idx, "H_PP"]),
            "away_score": int(df.loc[idx, "A_PP"]),
        }

    with open(args.report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> {args.report_path}")

if __name__ == "__main__":
    main()