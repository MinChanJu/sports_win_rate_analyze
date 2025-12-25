BASE_STAT = {
    # 1차 스탯
    "TEAM": 0,  # 1. 팀명
    "PP": 0,  # 23. 개인 득점
    "PA": 0,  # 24. 개인 득점 시도
    "MIN": 0,  # 16. 경기 시간 (전체 시간을 계산 초 단위로 환산)
    
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
    "FGA": 0,  # 11. 필드골 시도
    "FGM": 0,  # 12. 필드골 성공
    "SWA": 0,  # 8. 팀 속공
    "SWM": 0,  # 40. 속공에 의한 득점
    
    "UF": 0,  # U - 파울 (추가)
    "TF": 0,  # 29. 테크니컬 파울
    "TPF": 0,  # 13. 팀 총합 파울
    "PF": 0,  # 17. 개인 파울
    "EJ": 0,  # 36. 반칙 퇴장
    
    "TTO": 0,  # 32. 팀 턴오버
    "PTO": 0,  # 39. 개인 턴오버
    "TO": 0,    # 22. 총 턴오버
    "STL": 0,  # 28. 스틸
    
    # 2차 스탯
    "NR" : 0, # Net Rating                           NR = OR - DR
    "TS%" : 0, # PP x 100 / (2×(FGA + 0.44 × FTA))   (True Shooting Percentage 득점 효율성)
    "eFG%" : 0, # (FGM + 0.5 × 3PM) × 100 / FGA      (Effective Field Goal Percentage 3점슛 가치를 반영한 필드골 슈팅 효율성, 자유투 제외)
    "EFF": 0,  # 7. 효율성
    
    "TOV%": 0,  # 41. 턴오버 비율
    "OREB%": 0,  # 21. 공격 리바운드 비율
    "FT%": 0,  # 22. 자유투 얻는 비율
    
    "AST%": 0,  # 23. 어시스트에 의한 득점 비율
    "AST/TO%": 0,  # 24. 어시스트 대 턴오버 비율
    
    # 3차 스탯 (미구현) 3차 지표는 선수의 종합적인 기여도와 영향력을 하나의 숫자로 요약하려는 통계 지표이다. 2차 지표가 어떻게 이기는지를 보여준다면, 3차 지표는 누가 이기게 만들었는지를 분석하는 데 사용된다.
    "CR": 0, # 49. current run 현재 연속득점/실점
    "LC": 0,  # 47. 리드 체인지 횟수
    "LLP": 0,  # 48. 최대 리드 점수차
    "PACE": 0, # 50. 경기 페이스  {(H_TPOS + A_TPOS)/2} * (2400/MIN)
    
    # 지울 예정
    # "SUB": 0,  # 18. 교체 (교체 횟수)
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

print(f"Base stat keys count: {len(BASE_STAT)}")