from pydantic import BaseModel

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

class GameDataResponse(BaseModel):
    game_info: GameInfo
    prediction_records: list[ProbabilityRecord]
    shooting_records: list[PlayerShootingRecord]

class GameListResponse(BaseModel):
    games: list[GameInfo]