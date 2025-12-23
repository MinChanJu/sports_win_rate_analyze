from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  PROJECT_NAME: str = "Sports Win Rate Analysis API"
  API_V1_STR: str = "/api/v1"
  MODEL_PATH: str = "data/best_model.pt"
  FEATURE_ORDER_PATH: str = "data/feature_order.json"
  CODE_MAP_PATH: str = "data/code_map.json"
  @staticmethod
  def META_DATA_URL(gameKey: str) -> str:
    return f"https://api.kbl.or.kr/match/{gameKey}"
  @staticmethod
  def ALL_LOGS_URL(gameKey: str) -> str:
    return f"https://api.kbl.or.kr/match/{gameKey}/text-cast?quarterList=Q1,Q2,Q3,Q4,X1,X2,X3,X4,X5"
  @staticmethod
  def MATCH_CHART_URL(gameKey: str) -> str:
    return f"https://api.kbl.or.kr/match/{gameKey}/match-chart"
  @staticmethod
  def GAME_LIST_URL(fromDate: str, toDate: str) -> str:
    return f"https://api.kbl.or.kr/match/list?fromDate={fromDate}&toDate={toDate}"
  @staticmethod
  def TEAM_STATS_URL(gameKey: str, teamA: int, teamB: int) -> str:
    return f"https://api.kbl.or.kr/league/{gameKey}/vs/team-statsByGmKey?teamA={teamA}&teamB={teamB}"
  HEADERS: dict = {
    "channel": "WEB",
    "teamcode": "XX",
  }
  
  class Config:
    case_sensitive = True

settings = Settings()
