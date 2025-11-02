import json
from pathlib import Path
import sys

import numpy as np
from model import MLP
from predict import predict_one
from device import get_device
from data import load_state

KBL_STAT_MAP = [
    ("팀파울", {"TPF": 1}),
    ("테크니컬 파울", {"TF": 1}),
    ("U파울", {"UF": 1}),
    ("파울", {"PF": 1}),
    ("팀턴오버", {"TTO": 1}),
    ("턴오버", {"PTO": 1}),
    ("팀리바운드", {"TRB": 1}),
    ("팀속공", {"SWA": 1}),
    ("3점슛성공", {"3PM": 1, "3PA": 1}),
    ("2점슛성공", {"2PM": 1, "2PA": 1}),
    ("자유투성공", {"FTM": 1, "FTA": 1}),
    ("덩크슛성공", {"DKM": 1, "DKA": 1}),
    ("3점슛시도", {"3PA": 1}),
    ("2점슛시도", {"2PA": 1}),
    ("자유투시도", {"FTA": 1}),
    ("덩크슛시도", {"DKA": 1}),
    ("어시스트", {"AST": 1}),
    ("블록", {"BLK": 1}),
    ("수비리바운드", {"DREB": 1}),
    ("공격리바운드", {"OREB": 1}),
    ("스틸", {"STL": 1}),
    ("교체", {"SUB": 1}),
    ("굿디펜스", {}),
    ("작전시간", {}),
]

BASE_STAT = {
    # 1차 스탯
    "AST": 0,  # 2. 어시스트
    "BLK": 0,  # 3. 블록
    "DREB": 0,  # 4. 수비 리바운드
    "OREB": 0,  # 20. 공격 리바운드
    "PRB": 0,  # 26. 개인 리바운드
    "TRB": 0,  # 37. 팀 리바운드
    "2PA": 0,  # 10. 2점슛 시도
    "2PM": 0,  # 9. 2점슛 성공
    "3PA": 0,  # 31. 3점슛 시도
    "3PM": 0,  # 30. 3점슛 성공
    "DKA": 0,  # 6. 덩크슛 시도
    "DKM": 0,  # 5. 덩크슛 성공
    "FTA": 0,  # 15. 자유투 시도
    "FTM": 0,  # 14. 자유투 성공
    "SWA": 0,  # 8. 팀 속공
    "SWM": 0,  # 40. 속공에 의한 득점
    "FGA": 0,  # 11. 필드골 시도
    "FGM": 0,  # 12. 필드골 성공
    "TPF": 0,  # 13. 팀 총합 파울
    "PF": 0,  # 17. 개인 파울
    "SUB": 0,  # 18. 교체 (교체 횟수)
    "PP": 0,  # 23. 개인 득점
    "PA": 0,  # 24. 개인 득점 시도
    "STL": 0,  # 28. 스틸
    "TTO": 0,  # 32. 팀 턴오버
    "FTM": 0,  # 33. 자유투 성공 (중복)
    "FTA": 0,  # 34. 자유투 시도 (중복)
    "PTO": 0,  # 39. 개인 턴오버
    "MIN": 0,  # 16. 경기 시간 (전체 시간을 계산 초 단위로 환산)
    "UF": 0,  # U - 파울 (추가)
    "TF": 0,  # 29. 테크니컬 파울
    "EJ": 0,  # 36. 반칙 퇴장
    "TO": 0,    # 22. 총 턴오버
    
    # 2차 스탯
    "NR" : 0, # Net Rating                           NR = OR - DR
    "TS%" : 0, # TPS x 100 / (2×(PA + 0.44 × FTA))   (True Shooting Percentage 득점 효율성)
    "eFG%" : 0, # (FGM + 0.5 × 3PM) × 100 / FGA      (Effective Field Goal Percentage 3점슛 가치를 반영한 필드골 슈팅 효율성, 자유투 제외)
    "EFF": 0,  # 7. 효율성
    
    "TOV%": 0,  # 41. 턴오버 비율
    "OREB%": 0,  # 21. 공격 리바운드 비율
    "FT%": 0,  # 22. 자유투 얻는 비율
    
    "AST%": 0,  # 23. 어시스트에 의한 득점 비율
    "AST/TO%": 0,  # 24. 어시스트 대 턴오버 비율
    
    # 3차 스탯 (미구현)
    # "LC": 0,  # 47. 리드 체인지 횟수
    # "LLP": 0,  # 48. 최대 리드 점수
    
    # 지울 예정
    # "TEAM": 0,  # 1. 팀명
    # "TPS" : 0, # Total Points Scored (총 득점)
    # "TOPS" : 0, # Total Opponents Points Scored (상대 팀 총 득점)
    # "TPos" : 0, # Total Possessions (총 포제션 수)  TPos ≈ FGA+0.44×FTA+TO−Offensive Rebounds
    # "OR" : 0, # Offensive Rating                   OR = TPS / TPos
    # "DR" : 0, # Defensive Rating                   DR = TOPS / TPos 
    # "PPT": 0,  # 46. 득점 우위 시간
    # "MXS": 0,  # 44. 최다 연속 득점
    # "MXD": 0,  # 45. 최다 리드 점수
    # "DPS": 0,  # 42. 2차 찬스 득점
    # "BPF": 0,  # 35. 벤치 반칙
    # "BPS": 0,  # 43. 벤치 득점
    # "TPF_G": 0,  # 38. 팀 경기당 반칙
    # "FST": 0,  # 19. 첫 교체
    # "PPS": 0,  # 25. 선수 점수 (XX)
    # "TPS": 0,  # 27. 팀 점수 (XX)
}

log_history = []
H_TEAM = "서울 SK"
A_TEAM = "창원 LG"

game_stats = {"home": {}, "away": {}}
quarter = "Q1"  # Example quarter, in practice this would be dynamic
game_stats["home"][quarter] = BASE_STAT.copy()
game_stats["away"][quarter] = BASE_STAT.copy()

def calculate_log(log: str, team: str = 'H'):
  if ("쿼터 시작" in log) or ("연장 시작" in log):
    global quarter
    quarter = "Q1" if "1쿼터" in log else "Q2" if "2쿼터" in log else "Q3" if "3쿼터" in log else "Q4" if "4쿼터" in log else "연장"
    log_history.insert(0, log)
    return

  if quarter not in game_stats["home"]:
    game_stats["home"][quarter] = BASE_STAT.copy()
    game_stats["away"][quarter] = BASE_STAT.copy()
  
  team_key = "home" if team == 'H' else "away"
    
  if "속공" in log:
    next_log_entry = log_history[0] if 0 < len(log_history) else {}
    next_event = next_log_entry.get(team_key, "")
    if "2점슛성공" in next_event: game_stats[team_key][quarter]["SWM"] += 2
    if "3점슛성공" in next_event: game_stats[team_key][quarter]["SWM"] += 3
    if "덩크슛성공" in next_event: game_stats[team_key][quarter]["SWM"] += 2
    if "자유투성공" in next_event: game_stats[team_key][quarter]["SWM"] += 1

  if "퇴장" in log: game_stats[team_key][quarter]["EJ"] += 1

  stats = game_stats[team_key][quarter]
  for key, value in KBL_STAT_MAP:
    if key in log:
      for stat_key in value:
        stats[stat_key] += value[stat_key]
  
  log_history.insert(0, {team_key: log})

def main():
  team_code_path = Path('../train/teamcode.json')
  if not team_code_path.exists():
      print(f"teamcode.json 파일이 없습니다. 먼저 학습을 수행하세요. 경로: {team_code_path}")
      sys.exit(1)
          
  data = json.loads(team_code_path.read_text())
  team_code = data.get("team_code", {})
    
  best_model_path = Path("../models/01/combined/best_model.pt")
  if not best_model_path.exists():
      print(f"체크포인트 파일이 없습니다: {best_model_path}")
      sys.exit(1)
      
  device = get_device()
  in_dim = len(BASE_STAT) * 2 + 2  # Home and Away stats + team codes
  
  model = MLP(in_dim).to(device)
  state_dict, _ = load_state(best_model_path)
  model.load_state_dict(state_dict)
  model.eval()
  
  while True:
    log = input("Enter your log message: ")
    if log.lower() == "exit":
      break
    team = 'H' if "H" in log or "홈" in log else 'A' if "A" in log or "어웨이" in log else 'H'
    calculate_log(log, team)
    row = {}
    for team in game_stats:
      for stat in game_stats[team][quarter]:
        t = "H" if team == "home" else "A"
        row[f"{t}_{stat}"] = game_stats[team][quarter][stat]
    row["H_TEAM"] = team_code.get(H_TEAM, -1)
    row["A_TEAM"] = team_code.get(A_TEAM, -1)
    x_row = np.asarray([row[key] for key in sorted(row.keys())], dtype=np.float32)
    home_prob, away_prob = predict_one(model, x_row, device)
    print(f"Predicted Home Win Rate: home-{home_prob*100:.1f}%, away-{away_prob*100:.1f}%")
  
if __name__ == "__main__":
  main()