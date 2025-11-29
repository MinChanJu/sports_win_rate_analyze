from data import load_state, load_multi_csv
from predict import predict_one
from device import get_device
from config import get_args
from confusionMatrix import save_confusion_matrix
from pathlib import Path
from tqdm import tqdm
from model import MLP
import numpy as np
import json
import sys

predict_csv_path_map: dict[str, list[Path]] = {
    "combined": [
        Path("../kbl_real_time_csv/2021-2022"),
        Path("../kbl_real_time_csv/2022-2023"),
        Path("../kbl_real_time_csv/2023-2024"),
        Path("../kbl_real_time_csv/2024-2025"),
    ],
    "2021-2022": [
        Path("../kbl_real_time_csv/2021-2022"),
    ],
    "2022-2023": [
        Path("../kbl_real_time_csv/2022-2023"),
    ],
    "2023-2024": [
        Path("../kbl_real_time_csv/2023-2024"),
    ],
    "2024-2025": [
        Path("../kbl_real_time_csv/2024-2025"),
    ],
}

def main():
    args = get_args()
            
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
        drop_df_all, df_all = load_multi_csv(predict_csv_list, model_info.get("config", {}))
    else:
        drop_df_all, df_all = load_multi_csv(predict_csv_list, None)

    device = get_device()
    in_dim = drop_df_all.shape[1]
    model = MLP(in_dim).to(device)
    state_dict, _ = load_state(model_path)
    model.load_state_dict(state_dict)
    model.eval()
    
    result = {}
    for idx in tqdm(df_all.index, desc="Predicting"):
        gameKey = df_all.loc[idx, "gameKey"]
        n = df_all.loc[idx, "n"]
        x_row = np.asarray(drop_df_all.loc[idx], dtype=np.float32)
        home_prob, away_prob = predict_one(model, x_row, device)
        if gameKey not in result:
            result[gameKey] = {
                "metainfo": {
                    "home": int(df_all.loc[idx, "H_TEAM"]),
                    "away": int(df_all.loc[idx, "A_TEAM"]),
                    "winner": df_all.loc[idx, "winner"],
                    "max_n": int(n),
                }
            }
        result[gameKey]["metainfo"]["max_n"] = max(result[gameKey]["metainfo"]["max_n"], int(n))
        result[gameKey][int(n)] = {
            "home": home_prob,
            "away": away_prob,
            "home_score": int(df_all.loc[idx, "H_PP"]),
            "away_score": int(df_all.loc[idx, "A_PP"]),
        }

    report_path = Path(args.model_dir) / Path(args.model_type) / 'predict_report.json'
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> {report_path}")

    save_path = Path(args.model_dir) / Path(args.model_type) / 'confusion_matrix.png'
    save_confusion_matrix(report_path, save_path)

if __name__ == "__main__":
    main()