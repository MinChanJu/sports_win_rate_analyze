from fastapi import APIRouter, HTTPException
from app.schemas.shooting import ShootingResponse
from app.services.data_service import DataService

router = APIRouter()

@router.get("/shoot/{gameKey}/{gameDate}")
async def predict_game(gameKey: str, gameDate: str):
    """
    게임 슈팅 위치 엔드포인트
    
    Parameters:
    - gameKey: 게임 식별자 (예: S43G01N183)
    - gameDate: 게임 날짜 (예: 20251206)
    
    Returns:
    - PredictionResponse
    """

    # 1. 데이터 크롤링 및 가공
    raw_data = await DataService.crawl_kbl_match_chart(gameKey, gameDate)
    if raw_data is None:
      raise HTTPException(status_code=500, detail="데이터 크롤링 실패")
    
    return ShootingResponse(
      shooting_records=raw_data
    )
    
