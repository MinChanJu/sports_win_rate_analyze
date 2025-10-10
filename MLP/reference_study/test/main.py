from pathlib import Path
import torch
import numpy as np
import pandas as pd
from torch.nn.functional import softmax
import sys
import json

from model import MLP
from device import get_device
from data import load_state

@torch.no_grad()
def predict_one(ckpt_path: Path, x_row: np.ndarray, out_dim: int = 2, dropout: float = 0.1):
    """
    x_row: (F,) 형태의 1행 데이터 (학습 때와 동일한 전처리/피쳐 순서 필수)
    반환: pred(int 0/1), label(str), probs(dict: {'home': p0, 'away': p1})
    """
    device = get_device()
    in_dim = x_row.shape[-1]

    # 모델 생성 & 가중치 로드
    model = MLP(in_dim=in_dim, out_dim=out_dim, dropout=dropout).to(device)
    state_dict, _ = load_state(ckpt_path)
    model.load_state_dict(state_dict)
    model.eval()

    # 단일 샘플 텐서화 → 예측
    xb = torch.tensor(x_row, dtype=torch.float32, device=device).unsqueeze(0)  # [1, F]
    prob = softmax(model(xb), dim=1).squeeze(0).cpu().numpy()                  # [C]
    pred = int(np.argmax(prob))
    label = "away" if pred == 1 else "home"   # 당신 라벨 규칙(0=home, 1=away)

    return pred, label, {"home": float(prob[0]), "away": float(prob[1])}

if __name__ == "__main__":
    ckpt = Path("../models/01/combined_best_model.pt")  # 당신이 저장한 체크포인트 경로
    if not ckpt.exists():
        print("체크포인트 파일이 없습니다:", ckpt)
        sys.exit(1)
    
    df = pd.read_csv("../kbl_data_quarter_csv/2024-2025.csv").loc[909:]  # 당신의 테스트 데이터 경로
    drop_df = df.drop(columns=["gameKey", "seasonName", "date", "H_TEAM", "A_TEAM", "quarter", "winner"])
    result = {}
    for idx in df.index:
        gameKey = df.loc[idx, "gameKey"]
        quarter = df.loc[idx, "quarter"]
        x_row = np.asarray(drop_df.loc[idx], dtype=np.float32)
        pred, label, probs = predict_one(ckpt, x_row)
        if gameKey not in result: result[gameKey] = {}
        result[gameKey][quarter] = {
            "pred": pred,
            "label": label,
            "probs": probs,
            "actual": df.loc[idx, "winner"],
        }

    with open('report.json', "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> report.json")