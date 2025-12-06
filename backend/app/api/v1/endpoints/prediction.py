from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PredictionResponse, ErrorResponse
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/predict/{gameKey}/{gameDate}")
async def predict_game(gameKey: str, gameDate: str):
		"""
		게임 승률 예측 엔드포인트
		
		Parameters:
		- gameKey: 게임 식별자 (예: S43G01N183)
		- gameDate: 게임 날짜 (예: 20251206)
		
		Returns:
		- PredictionResponse
		"""

		# 1. 데이터 크롤링 및 가공
		raw_data = await DataService.get_model_input(gameKey, gameDate)
		
		# 2. 모델 예측
		prediction_result = PredictionService.predict(raw_data["records"])
		
		return PredictionResponse(
      meta_info=raw_data["meta"],
      records=prediction_result
		)
		
