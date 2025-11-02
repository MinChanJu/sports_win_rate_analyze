from data import load_state, load_csv_paths
from predict import predict_one
from device import get_device
from config import get_args
from confusionMatrix import save_confusion_matrix
from pathlib import Path
from model import MLP
import numpy as np
import json
import sys

predict_csv_path_map = {
    "combined": [
        "../kbl_data_quarter_csv/2021-2022.csv",
        "../kbl_data_quarter_csv/2022-2023.csv",
        "../kbl_data_quarter_csv/2023-2024.csv",
        "../kbl_data_quarter_csv/2024-2025.csv",
    ],
    "2021-2022": [
        "../kbl_data_quarter_csv/2021-2022.csv",
    ],
    "2022-2023": [
        "../kbl_data_quarter_csv/2022-2023.csv",
    ],
    "2023-2024": [
        "../kbl_data_quarter_csv/2023-2024.csv",
    ],
    "2024-2025": [
        "../kbl_data_quarter_csv/2024-2025.csv",
    ],
}

def main():
    args = get_args()
    team_code_path = Path(args.team_code_path)
    if not team_code_path.exists():
        print(f"teamcode.json 파일이 없습니다. 먼저 학습을 수행하세요. 경로: {team_code_path}")
        sys.exit(1)
            
    data = json.loads(team_code_path.read_text())
    team_code = data.get("team_code", {})
    
    model_path = Path(args.model_dir) / f'{args.model_type}' / 'best_model.pt'
    if not model_path.exists():
        print(f"체크포인트 파일이 없습니다: {model_path}")
        sys.exit(1)
    
    model_info_path = Path(args.model_dir) / f'{args.model_type}' / 'best_model.json'
    if not model_info_path.exists():
        print(f"모델 정보 파일이 없습니다: {model_info_path}")
        sys.exit(1)
    model_info = json.loads(model_info_path.read_text())

    predict_csv_list = predict_csv_path_map.get(args.model_type, [])
    if not predict_csv_list:
        print(f"알 수 없는 모델 타입입니다: {args.model_type}")
        sys.exit(1)
        
    if (args.predict_split):
        df, drop_df = load_csv_paths(predict_csv_list, team_code, model_info.get("config", None))
    else:
        df, drop_df = load_csv_paths(predict_csv_list, team_code, None)

    device = get_device()
    in_dim = drop_df.shape[1]
    model = MLP(in_dim).to(device)
    state_dict, _ = load_state(model_path)
    model.load_state_dict(state_dict)
    model.eval()
    
    result = {}
    for idx in df.index:
        gameKey = df.loc[idx, "gameKey"]
        quarter = df.loc[idx, "quarter"]
        x_row = np.asarray(drop_df.loc[idx], dtype=np.float32)
        home_prob, away_prob = predict_one(model, x_row, device)
        if gameKey not in result: result[gameKey] = {"metainfo": {"home": df.loc[idx, "H_TEAM"], "away": df.loc[idx, "A_TEAM"], "winner": df.loc[idx, "winner"], "quarters": []}}
        result[gameKey]["metainfo"]["quarters"].append(quarter)
        result[gameKey][quarter] = {
            "home": home_prob,
            "away": away_prob,
            "home_score": int(df.loc[idx, "H_PP"]),
            "away_score": int(df.loc[idx, "A_PP"]),
        }

    report_path = Path(args.model_dir) / Path(args.model_type) / 'predict_report.json'
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> {report_path}")

    save_path = Path(args.model_dir) / Path(args.model_type) / 'confusion_matrix.png'
    save_confusion_matrix(report_path, save_path)

if __name__ == "__main__":
    main()