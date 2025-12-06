from pydantic import BaseModel

class TeamInfo(BaseModel):
    code: int
    name: str
    score: int

class metaInfo(BaseModel):
    gameKey: str
    gameDate: str
    finished: bool
    home: TeamInfo
    away: TeamInfo

class ProbabilityRecord(BaseModel):
    home_probability: float
    away_probability: float
    total_time_sec: int

class PredictionResponse(BaseModel):
    meta_info: metaInfo
    records: list[ProbabilityRecord]

class ErrorResponse(BaseModel):
    error: str
    gameKey: str
    gameDate: str
