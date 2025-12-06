"""
예측 서비스 - 모델 호출 및 결과 처리
"""
import torch
from torch.nn.functional import softmax
from app.models.prediction_model import get_model, device

class PredictionService:
    """승률 예측 서비스"""
    
    @staticmethod
    def predict(total_records: list[dict]) -> list[dict]:
        """
        입력 데이터로 승률을 예측합니다.
        
        Args:
            input_data: shape (1, 88) 모델 입력 numpy 배열
            
        Returns:
            예측 결과 딕셔너리
        """
        model = get_model()
        
        total_records_probs = []
        for record in total_records:
          input_data = record["array"]
          xb = torch.tensor(input_data, dtype=torch.float32, device=device).unsqueeze(0)
          prob = softmax(model(xb), dim=1).squeeze(0).detach().cpu().numpy()
          home_prob, away_prob = float(prob[0]), float(prob[1])
          total_records_probs.append({
              "home_probability": round(home_prob * 100, 2),
              "away_probability": round(away_prob * 100, 2),
              "total_time_sec": record["total_time_sec"]
          })
        
        return total_records_probs
