from predict import predict_one
from pathlib import Path
import pandas as pd
import numpy as np
import json
import sys

def main():
    team_code_path = Path(__file__).parent / "../train/teamcode.json"
    if not team_code_path.exists(): 
        print("teamcode.json 파일이 없습니다. 먼저 학습을 수행하세요.")
        sys.exit(1)
            
    data = json.loads(team_code_path.read_text())
    team_code = data.get("team_code", {})
    
    ckpt = Path("../models/13/combined_best_model.pt")  # 당신이 저장한 체크포인트 경로
    if not ckpt.exists():
        print("체크포인트 파일이 없습니다:", ckpt)
        sys.exit(1)
    
    df = pd.read_csv("../kbl_data_quarter_csv/2024-2025.csv").loc[909:]  # 당신의 테스트 데이터 경로
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

    with open('report.json', "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> report.json")
    
if __name__ == "__main__":
    main()