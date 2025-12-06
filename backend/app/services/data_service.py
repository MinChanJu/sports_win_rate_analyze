import requests
from app.core.config import settings
from app.services.decoder_service import DecoderService

class DataService:
  """게임 데이터 크롤링 및 전처리"""

  @staticmethod
  async def get_meta_data(gameKey: str) -> dict | None:
    response = requests.get(settings.META_DATA_URL(gameKey), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"메타 데이터 API 응답 오류: {response.status_code}")
      return None
    data = response.json()
    game = data.get("game")
    teamRecords = data.get("teamrecords")
    h_score = sum(
      v if isinstance(v, int) else sum(v)
      for v in teamRecords.get("home").values()
    )
    a_score = sum(
      v if isinstance(v, int) else sum(v)
      for v in teamRecords.get("away").values()
    )
    return {
      "gameKey": game.get("gmkey"),
      "gameDate": game.get("gameDate"),
      "gameStart": game.get("gameStart"),
      "isStarted": game.get("isStarted"),
      "isEnded": game.get("isEnded"),
      "seasonName": game.get("seasonName"),
      "home": {
        "code": game.get("tcodeH"),
        "name": game.get("tnameH"),
        "score": h_score,
      },
      "away": {
        "code": game.get("tcodeA"),
        "name": game.get("tnameA"),
        "score": a_score,
      }
    }

  @staticmethod
  async def get_all_logs(gameKey: str) -> list[dict] | None:
    response = requests.get(settings.ALL_LOGS_URL(gameKey), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"전체 로그 API 응답 오류: {response.status_code}")
      return None
    all_logs = response.json()
    return all_logs
  
  @staticmethod
  async def get_shoot_log(gameKey: str) -> list[dict] | None:
    response = requests.get(settings.SHOOT_LOG_URL(gameKey), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"슈팅 로그 API 응답 오류: {response.status_code}")
      return None
    shoot_logs = response.json()
    return shoot_logs.get("shootLog")

  @staticmethod
  async def get_model_input(gameKey: str) -> dict:
    all_logs = await DataService.get_all_logs(gameKey)
    if all_logs is None:
      raise ValueError("게임 데이터 크롤링 실패")
    meta_data = await DataService.get_meta_data(gameKey)
    if meta_data is None:
      raise ValueError("메타 데이터 크롤링 실패")
    total_records = DecoderService.preprocess_data({"logs": all_logs, "meta": meta_data})
    return {"meta": meta_data, "records": total_records}
  
  @staticmethod
  async def get_game_list(fromDate: str, toDate: str) -> list[dict] | None:
    response = requests.get(settings.GAME_LIST_URL(fromDate, toDate), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"게임 리스트 API 응답 오류: {response.status_code}")
      return None
    game_list = response.json()
    game_list = [{
      "gameKey": game["gmkey"],
      "gameDate": game["gameDate"],
      "gameStart": game["gameStart"],
      "isStarted": game["isStarted"],
      "isEnded": game["isEnded"],
      "seasonName": game["seasonName1"],
      "home": {
        "code": int(game["tcodeH"]),
        "name": game["tnameH"],
        "score": game["scoreH"],
      },
      "away": {
        "code": int(game["tcodeA"]),
        "name": game["tnameA"],
        "score": game["scoreA"],
      }
      } for game in game_list if game["seasonCategoryName"] == "정규시즌"]
    return game_list