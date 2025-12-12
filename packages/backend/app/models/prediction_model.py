import logging
import torch
import torch.nn as nn
from pathlib import Path
from app.core.config import settings

class PredictionModel(nn.Module):
  def __init__(self, in_dim, out_dim=2, layers=[(120, {'batch_norm': True, 'activation': 'sigmoid', 'dropout': 0.1}),
                                                (60, {'batch_norm': True, 'activation': 'sigmoid', 'dropout': 0.1})]):
    super().__init__()
    
    modules = []
    for i in range(len(layers)):
      hidden_dim = layers[i][0]
      params = layers[i][1]

      modules.append(nn.Linear(in_dim, hidden_dim))
      if params.get('batch_norm', False):
        modules.append(nn.BatchNorm1d(hidden_dim))
      if params.get('activation', 'relu') == 'relu':
        modules.append(nn.ReLU())
      elif params.get('activation') == 'sigmoid':
        modules.append(nn.Sigmoid())
      if params.get('dropout', 0.0) > 0.0:
        modules.append(nn.Dropout(params['dropout']))
      in_dim = hidden_dim

    modules.append(nn.Linear(in_dim, out_dim))

    self.net = nn.Sequential(*modules)

  def forward(self, x):
    return self.net(x)

def get_device() -> torch.device:
  if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    return torch.device("mps")
  elif torch.cuda.is_available():
    return torch.device("cuda")
  return torch.device("cpu")

def load_state(ckpt_path: Path):
  ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
  if isinstance(ckpt, dict) and "state_dict" in ckpt:
    return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
  return ckpt, {}

# 모델 로드
device = get_device()
model = None

logger = logging.getLogger("uvicorn.error")

try:
  MODEL_PATH = Path(__file__).parent.parent / settings.MODEL_PATH
  in_dim = 88
  model = PredictionModel(in_dim).to(device)
  state_dict, _ = load_state(MODEL_PATH)
  model.load_state_dict(state_dict)
  model.eval()
  logger.info("✅ 모델 로드 성공")
except Exception as e:
  logger.error(f"❌ 모델 로드 실패: {e}")

def get_model():
  return model
