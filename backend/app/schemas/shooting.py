from pydantic import BaseModel

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
  
class ShootingResponse(BaseModel):
    shooting_records: list[PlayerShootingRecord]