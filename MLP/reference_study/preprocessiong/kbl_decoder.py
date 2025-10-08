import json

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
    # "TEAM": 0,  # 1. 팀명
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
    "SUB": 0,  # 18. 교체
    "PP": 0,  # 23. 개인 득점
    "PA": 0,  # 24. 개인 득점 시도
    "STL": 0,  # 28. 스틸
    "TTO": 0,  # 32. 팀 턴오버
    "FTM": 0,  # 33. 자유투 성공 (중복)
    "FTA": 0,  # 34. 자유투 시도 (중복)
    "PTO": 0,  # 39. 개인 턴오버
    "MIN": 0,  # 16. 경기 시간 (전체 시간을 계산)
    "MIN_M": 0,  # 21. 플레이 시간, 분 (전체 시간을 분 단위로 환산)
    "MIN_S": 0,  # 22. 플레이 시간, 초 (전체 시간을 초 단위로 환산)
    "UF": 0,  # U - 파울 (추가)
    "TF": 0,  # 29. 테크니컬 파울
    "TOM": 0,  # 41. 턴오버에 의한 득점
    "EJ": 0,  # 36. 반칙 퇴장
    "EFF": 0,  # 7. 효율성
    
    #후처리 데이터 변수들
    #최근 10경기에 대한 Net Rating 계산 방법
    "TPS" : 0, # Total Points Scored (총 득점)
    "TOPS" : 0, # Total Opponents Points Scored (상대 팀 총 득점)
    "TPos" : 0, # Total Possessions (총 포제션 수)  TPos ≈ FGA+0.44×FTA+TO−Offensive Rebounds
    "OR" : 0, # Offensive Rating                   OR = TPS / TPos
    "DR" : 0, # Defensive Rating                   DR = TOPS / TPos 
    "TS%" : 0, # TPS x 100 / (2×(PA + 0.44 × FTA))   (True Shooting Percentage 득점 효율성)
    "eFG%" : 0, # (FGM + 0.5 × 3PM) × 100 / FGA      (Effective Field Goal Percentage 3점슛 가치를 반영한 필드골 슈팅 효율성, 자유투 제외)

     
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


def quarter_calculate(game_stats: dict, quarter: str) -> dict:
    for team in game_stats.values():
        for key, stats in team.items():
            if (key != quarter): continue
            stats["PP"] = (
                2 * stats["2PM"] + 3 * stats["3PM"] + stats["FTM"] + 2 * stats["DKM"]
            )
            stats["PA"] = stats["2PA"] + stats["3PA"] + stats["FTA"] + stats["DKA"]
            stats["PRB"] = stats["OREB"] + stats["DREB"]

            stats["FGA"] = stats["2PA"] + stats["3PA"] + stats["DKA"]
            stats["FGM"] = stats["2PM"] + stats["3PM"] + stats["DKM"]

            stats["SUB"] -= 10
        idx = ["Q1", "Q2", "Q3", "Q4", "연장"].index(quarter)
        if (idx == 0): continue
        prev_quarter = ["Q1", "Q2", "Q3", "Q4", "연장"][idx - 1]
        for stat_key in BASE_STAT:
            team[quarter][stat_key] += team[prev_quarter][stat_key]
    return game_stats


def final_calculate(game_stats: dict) -> dict:
    for team in game_stats.values():
        for stats in team.values():
            stats["SUB"] //= 2
            stats["EFF"] = (
                stats["PP"]
                + stats["PRB"]
                + stats["TRB"]
                + stats["AST"]
                + stats["STL"]
                + stats["BLK"]
                - (
                    (stats["FGA"] - stats["FGM"])
                    + (stats["FTA"] - stats["FTM"])
                    + (stats["TTO"] + stats["PTO"])
                )
            )
    return game_stats

def kbl_decoder(game_path: dict) -> tuple[dict, dict]:
    with open(game_path, "r", encoding="utf-8") as file:
        game_log_data = json.load(file)

    metainfo = game_log_data["metainfo"]

    game_stats = {"home": {}, "away": {}}

    quarters = metainfo["quarters"]

    for quarter in sorted(quarters):
        if quarter in game_log_data:
            quarter_log = game_log_data[quarter]
            
            game_stats["home"][quarter] = dict(BASE_STAT)
            game_stats["away"][quarter] = dict(BASE_STAT)
            
            game_stats["home"][quarter]["TEAM"] = metainfo["home"]["name"]
            game_stats["away"][quarter]["TEAM"] = metainfo["away"]["name"]

            for i in range(len(quarter_log)):
                log_entry = quarter_log[i]
                for team_key in ["home", "away"]:
                    event = log_entry.get(team_key)
                    if not event:
                        continue
                    
                    if "속공" in event:
                        next_log_entry = (
                            quarter_log[i + 1] if i + 1 < len(quarter_log) else {}
                        )
                        next_event = next_log_entry.get(team_key, "")
                        if "2점슛성공" in next_event:
                            game_stats[team_key][quarter]["SWM"] += 2
                        if "3점슛성공" in next_event:
                            game_stats[team_key][quarter]["SWM"] += 3
                        if "덩크슛성공" in next_event:
                            game_stats[team_key][quarter]["SWM"] += 2
                        if "자유투성공" in next_event:
                            game_stats[team_key][quarter]["SWM"] += 1

                    if "턴오버" in event:
                        next_team = "away" if team_key == "home" else "home"
                        event_logs = ""
                        for j in range(i - 1, 0, -1):
                            prev_log_entry = quarter_log[j]
                            prev_event = prev_log_entry.get(next_team, "")
                            if not prev_event:
                                break
                            if "성공" in prev_event:
                                event_logs = prev_event
                                break
                        if "2점슛성공" in event_logs:
                            game_stats[next_team][quarter]["TOM"] += 2
                        if "3점슛성공" in event_logs:
                            game_stats[next_team][quarter]["TOM"] += 3
                        if "덩크슛성공" in event_logs:
                            game_stats[next_team][quarter]["TOM"] += 2
                        if "자유투성공" in event_logs:
                            game_stats[next_team][quarter]["TOM"] += 1

                    if "퇴장" in event:
                        game_stats[team_key][quarter]["EJ"] += 1

                    stats = game_stats[team_key][quarter]
                    for key, value in KBL_STAT_MAP:
                        if key in event:
                            for stat_key in value:
                                stats[stat_key] += value[stat_key]
                    
            time = quarter_log[-1].get("time", "00:00")
            minutes, seconds = map(int, time.split(":"))
            for team in ["home", "away"]:
                game_stats[team][quarter]["MIN"] += minutes + seconds / 60
                game_stats[team][quarter]["MIN_M"] += minutes + seconds / 60
                game_stats[team][quarter]["MIN_S"] += 60 * minutes + seconds

            game_stats = quarter_calculate(game_stats, quarter)

    game_stats = final_calculate(game_stats)

    return game_stats, metainfo


if __name__ == "__main__":
    game_stats, all_metainfo = kbl_decoder("../../../kbl_data/2021-2022/S39G01N3.json")
    home = game_stats["home"]
    away = game_stats["away"]
    print(f"home: {json.dumps(home, ensure_ascii=False)}")
    print()
    print(f"away: {json.dumps(away, ensure_ascii=False)}")
    print()

    # fill_stats = []
    # empty_stats = []
    # for stat in BASE_STAT:
    #     if home[stat] == 0 and away[stat] == 0:
    #         empty_stats.append(f'"{stat}"')
    #     else:
    #         fill_stats.append(f'"{stat}"')
    # fill_stats.sort()
    # print(f"Fill Stats ({len(fill_stats)}): {', '.join(fill_stats)}")
    # empty_stats.sort()
    # print(f"Empty Stats ({len(empty_stats)}): {', '.join(empty_stats)}")