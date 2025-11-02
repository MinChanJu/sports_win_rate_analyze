from torch.nn.functional import softmax
from model import MLP
import numpy as np
import torch

@torch.no_grad()
def predict_one(model: MLP, x_row: np.ndarray, device: torch.device):
    """
    x_row: (F,) 형태의 1행 데이터 (학습 때와 동일한 전처리/피쳐 순서 필수)
    반환: pred(int 0/1), label(str), probs(dict: {'home': p0, 'away': p1})
    """

    # 단일 샘플 텐서화 → 예측
    xb = torch.tensor(x_row, dtype=torch.float32, device=device).unsqueeze(0)  # [1, F]
    prob = softmax(model(xb), dim=1).squeeze(0).cpu().numpy()                  # [C]
    home_prob, away_prob = float(prob[0]), float(prob[1])

    return home_prob, away_prob