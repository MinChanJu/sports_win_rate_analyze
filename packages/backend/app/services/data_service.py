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
    
    gameInfo = {
      "gameKey": game.get("gmkey"),
      "gameDate": game.get("gameDate"),
      "weekDay": game.get("weekDay"),
      "gameStart": game.get("gameStart"),
      "isStarted": game.get("isStarted"),
      "isEnded": game.get("isEnded"),
      "seasonName": game.get("seasonName"),
      "stadiumName": game.get("stadiumnameF"),
      "home": {
        "code": game.get("tcodeH"),
        "name": game.get("tnameH"),
        "score": h_score,
        "logo": game.get("tlogoH"),
      },
      "away": {
        "code": game.get("tcodeA"),
        "name": game.get("tnameA"),
        "score": a_score,
        "logo": game.get("tlogoA"),
      }
    }
    
    team_score_record = teamRecords
    
    response = requests.get(settings.TEAM_STATS_URL(gameKey, gameInfo["home"]["code"], gameInfo["away"]["code"]), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"메타 데이터 API 응답 오류: {response.status_code}")
      return None
    data = response.json()
    home_stats = data.get("a")
    away_stats = data.get("b")
    previous_stats = {
      "home": {
        "thisSeasonWin": home_stats.get("win"),
        "thisSeasonLose": home_stats.get("loss"),
        "headToHeadWin": home_stats.get("vsWin"),
        "headToHeadLose": home_stats.get("vsLoss"),
        "last5gamesWin": home_stats.get("rntWin"),
        "last5gamesLose": home_stats.get("rntLoss"),
        "allTimeHeadToHeadWin": home_stats.get("totWin"),
        "allTimeHeadToHeadLose": home_stats.get("totLoss"),
        "logo": home_stats.get("team").get("teamLogoClass"),
      },
      "away": {
        "thisSeasonWin": away_stats.get("win"),
        "thisSeasonLose": away_stats.get("loss"),
        "headToHeadWin": away_stats.get("vsWin"),
        "headToHeadLose": away_stats.get("vsLoss"),
        "last5gamesWin": away_stats.get("rntWin"),
        "last5gamesLose": away_stats.get("rntLoss"),
        "allTimeHeadToHeadWin": away_stats.get("totWin"),
        "allTimeHeadToHeadLose": away_stats.get("totLoss"),
        "logo": away_stats.get("team").get("teamLogoClass"),
      }
    }
    
    return {"game": gameInfo, "team_score_record": team_score_record, "previous_stats": previous_stats}

  @staticmethod
  async def get_all_logs(gameKey: str) -> list[dict] | None:
    response = requests.get(settings.ALL_LOGS_URL(gameKey), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"전체 로그 API 응답 오류: {response.status_code}")
      return None
    all_logs = response.json()
    return all_logs
  
  @staticmethod
  async def get_match_chart(gameKey: str) -> list[dict] | None:
    response = requests.get(settings.MATCH_CHART_URL(gameKey), headers=settings.HEADERS, timeout=5)
    if response.status_code != 200:
      print(f"매치 차트 API 응답 오류: {response.status_code}")
      return None
    shoot_logs = response.json()
    return shoot_logs.get("shootLog"), shoot_logs.get("scoreChart")

  @staticmethod
  async def get_model_input(gameKey: str) -> dict:
    all_logs = await DataService.get_all_logs(gameKey)
    if all_logs is None:
      raise ValueError("게임 데이터 크롤링 실패")
    meta_data = await DataService.get_meta_data(gameKey)
    if meta_data is None:
      raise ValueError("메타 데이터 크롤링 실패")
    total_records, last_game_stats, quarter_net_ratings = DecoderService.preprocess_data({"logs": all_logs, "meta": meta_data["game"]})
    return {"meta": meta_data, "records": total_records, "last_game_stats": last_game_stats, "quarter_net_ratings": quarter_net_ratings}
  
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
      "weekDay": game["weekDay"],
      "gameStart": game["gameStart"],
      "isStarted": game["isStarted"],
      "isEnded": game["isEnded"],
      "seasonName": game["seasonName1"],
      "stadiumName": game["stadiumnameF"],
      "home": {
        "code": int(game["tcodeH"]),
        "name": game["tnameH"],
        "score": game["scoreH"],
        "logo": game["logoH"],
      },
      "away": {
        "code": int(game["tcodeA"]),
        "name": game["tnameA"],
        "score": game["scoreA"],
        "logo": game["logoA"],
      }
      } for game in game_list if game["seasonCategoryName"] == "정규시즌"]
    return game_list