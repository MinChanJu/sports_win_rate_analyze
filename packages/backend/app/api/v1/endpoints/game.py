from fastapi import APIRouter
from app.schemas.game import GameDataResponse, GameListResponse
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/game/{gameKey}")
async def predict_game(gameKey: str):
  raw_data = await DataService.get_model_input(gameKey)
  
  prediction_result = PredictionService.predict(raw_data["records"])

  shooting_records = await DataService.get_shoot_log(gameKey)
  
  return GameDataResponse(
    game_info=raw_data["meta"]["game"],
    team_score_record=raw_data["meta"]["team_score_record"],
    previous_stats=raw_data["meta"]["previous_stats"],
    quarter_net_ratings=raw_data["quarter_net_ratings"],
    prediction_records=prediction_result,
    shooting_records=shooting_records,
    last_game_stats=raw_data["last_game_stats"]
  )

@router.get("/list/{fromDate}/{toDate}")
async def predict_game(fromDate: str, toDate: str):
  # 1. 데이터 크롤링 및 가공
  game_list = await DataService.get_game_list(fromDate, toDate)
  return GameListResponse(
    games=game_list
  )
