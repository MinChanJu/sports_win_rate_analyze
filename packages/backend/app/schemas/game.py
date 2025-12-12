from pydantic import BaseModel, Field

class TeamInfo(BaseModel):
  code: int
  name: str
  score: int | None
  logo: str | None

class GameInfo(BaseModel):
  gameKey: str
  gameDate: str
  weekDay: str
  gameStart: str
  isStarted: int
  isEnded: int
  seasonName: str
  stadiumName: str
  home: TeamInfo
  away: TeamInfo

class ProbabilityRecord(BaseModel):
  home_probability: float
  away_probability: float
  total_time_sec: int

class ShootLog(BaseModel):
  q: str
  x: int
  y: int
  o: str
  d: str

class PlayerShootingRecord(BaseModel):
  pcode: str
  pname: str
  ename: str
  tcode: str
  logs: list[ShootLog]

class TeamStats(BaseModel):
  TEAM: float
  AST: float
  BLK: float
  DREB: float
  OREB: float
  PRB: float
  TRB: float
  TWO_PA: float = Field(alias="2PA")
  TWO_PM: float = Field(alias="2PM")
  THREE_PA: float = Field(alias="3PA")
  THREE_PM: float = Field(alias="3PM")
  DKA: float
  DKM: float
  FTA: float
  FTM: float
  SWA: float
  SWM: float
  FGA: float
  FGM: float
  TPF: float
  PF: float
  PP: float
  PA: float
  STL: float
  TTO: float
  PTO: float
  MIN: float
  UF: float
  TF: float
  EJ: float
  TO: float
  NR: float
  TS_PCT: float = Field(alias="TS%")
  EFG_PCT: float = Field(alias="eFG%")
  EFF: float
  TOV_PCT: float = Field(alias="TOV%")
  OREB_PCT: float = Field(alias="OREB%")
  FT_PCT: float = Field(alias="FT%")
  AST_PCT: float = Field(alias="AST%")
  AST_TO_PCT: float = Field(alias="AST/TO%")
  CR: float
  LC: float
  LLP: float
  PACE: float
  
  class Config:
    populate_by_name = True

class GameStats(BaseModel):
  home: TeamStats
  away: TeamStats

class ScoreRecord(BaseModel):
  scoreq1: int
  scoreq2: int
  scoreq3: int
  scoreq4: int
  scoreeq: list[int]

class TeamScoreRecord(BaseModel):
  home: ScoreRecord
  away: ScoreRecord

class PreviousTeamStats(BaseModel):
  thisSeasonWin: int
  thisSeasonLose: int
  headToHeadWin: int
  headToHeadLose: int
  last5gamesWin: int
  last5gamesLose: int
  allTimeHeadToHeadWin: int
  allTimeHeadToHeadLose: int
  logo: str

class TotalPreviousStats(BaseModel):
  home: PreviousTeamStats
  away: PreviousTeamStats

class QuarterNetRatings(BaseModel):
  home: list[float]
  away: list[float]
  order: list[str]

class GameDataResponse(BaseModel):
  game_info: GameInfo
  team_score_record: TeamScoreRecord
  previous_stats: TotalPreviousStats
  quarter_net_ratings: QuarterNetRatings
  prediction_records: list[ProbabilityRecord]
  shooting_records: list[PlayerShootingRecord]
  last_game_stats: GameStats

class GameListResponse(BaseModel):
  games: list[GameInfo]
