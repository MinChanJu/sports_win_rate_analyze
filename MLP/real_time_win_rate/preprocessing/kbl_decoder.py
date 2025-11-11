import json

KBL_STAT_MAP = {
    "팀파울": {"TPF": 1},
    "테크니컬 파울": {"TF": 1},
    "U파울": {"UF": 1},
    "파울": {"PF": 1},
    "팀턴오버": {"TTO": 1},
    "턴오버": {"PTO": 1},
    "팀리바운드": {"TRB": 1},
    "팀속공": {"SWA": 1},
    "3점슛성공": {"3PM": 1, "3PA": 1},
    "2점슛성공": {"2PM": 1, "2PA": 1},
    "자유투성공": {"FTM": 1, "FTA": 1},
    "덩크슛성공": {"DKM": 1, "DKA": 1},
    "3점슛시도": {"3PA": 1},
    "2점슛시도": {"2PA": 1},
    "자유투시도": {"FTA": 1},
    "덩크슛시도": {"DKA": 1},
    "어시스트": {"AST": 1},
    "블록": {"BLK": 1},
    "수비리바운드": {"DREB": 1},
    "공격리바운드": {"OREB": 1},
    "스틸": {"STL": 1},
    "기타파울": {}, # 기타파울은 추후에 분석 필요
    "파울자유투": {}, # 파울자유투는 추후에 분석 필요
    "교체(IN)": {},
    "교체(OUT)": {},
    "굿디펜스": {},
    "작전타임": {},
}

BASE_STAT = {
    # 1차 스탯
    "TEAM": 0,  # 1. 팀명
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
    
    # 3차 스탯 (미구현) 3차 지표는 선수의 종합적인 기여도와 영향력을 하나의 숫자로 요약하려는 통계 지표이다. 2차 지표가 어떻게 이기는지를 보여준다면, 3차 지표는 누가 이기게 만들었는지를 분석하는 데 사용된다.
    # "CR": 0, # 49. current run 현재 연속득점/실점
    # "LC": 0,  # 47. 리드 체인지 횟수
    # "LLP": 0,  # 48. 최대 리드 점수
    # "Pace": 0, # 50. 경기 페이스  {(H_TPOS + A_TPOS)/2} * (2400/MIN)
    
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

def final_calculate(game_stats: dict) -> dict:
    for team, team_stat in game_stats.items():
        # 필드골
        team_stat["FGA"] = team_stat["2PA"] + team_stat["3PA"] + team_stat["DKA"]
        team_stat["FGM"] = team_stat["2PM"] + team_stat["3PM"] + team_stat["DKM"]
        
        # 개인 득점
        team_stat["PP"] = (team_stat["2PM"] * 2) + (team_stat["3PM"] * 3) + (team_stat["DKM"] * 2) + team_stat["FTM"]
        team_stat["PA"] = team_stat["2PA"] + team_stat["3PA"] + team_stat["DKA"] + team_stat["FTA"]
        
        # 총 턴오버
        team_stat["TO"] = team_stat["PTO"] + team_stat["TTO"]
        
        # 개인 리바운드
        team_stat["PRB"] = team_stat["OREB"] + team_stat["DREB"]
        
        # 2차 스탯
        # 슈팅 효율성
        team_stat["TS%"] = (
            team_stat["PP"] * 100 / (2 * (team_stat["PA"] + 0.44 * team_stat["FTA"]))
            if (team_stat["PA"] + 0.44 * team_stat["FTA"]) != 0
            else 0
        )
        
        # 유효 필드골 비율
        team_stat["eFG%"] = (
            (team_stat["FGM"] + 0.5 * team_stat["3PM"]) * 100 / team_stat["FGA"]
            if team_stat["FGA"] != 0
            else 0
        )
        
        # 턴오버 비율
        team_stat["TOV%"] = (
            team_stat["TO"] * 100 / (team_stat["FGA"] + 0.44 * team_stat["FTA"] + team_stat["TO"])
            if (team_stat["FGA"] + 0.44 * team_stat["FTA"] + team_stat["TO"]) != 0
            else 0
        )
        
        # 자유투 성공 비율
        team_stat["FT%"] = (
            team_stat["FTA"] * 100 / team_stat["FGA"]
            if team_stat["FGA"] != 0
            else 0
        )
        
        # 어시스트 에 의한 득점 비율
        team_stat["AST%"] = (
            team_stat["AST"] * 100 / (team_stat["FGM"])
            if team_stat["FGM"] != 0
            else 0
        )
        
        # 어시스트 대 턴오버 비율
        team_stat["AST/TO%"] = (
            team_stat["AST"] / team_stat["TO"]
            if team_stat["TO"] != 0
            else 0
        )
        
        # 공격 리바운드 비율
        opp_stats = game_stats["away"] if team == "home" else game_stats["home"]
        team_stat["OREB%"] = (
            team_stat["OREB"] * 100 / (team_stat["OREB"] + team_stat["DREB"])
            if (team_stat["OREB"] + opp_stats["DREB"]) > 0
            else 0
        )
        
        # 효율성
        team_stat["EFF"] = team_stat["PP"] + team_stat["PRB"] + team_stat["TRB"] + team_stat["AST"] + team_stat["STL"] + team_stat["BLK"] - (
            (team_stat["FGA"] - team_stat["FGM"])
            + (team_stat["FTA"] - team_stat["FTM"])
            + (team_stat["TTO"] + team_stat["PTO"])
        )
    
    # Net Rating 계산
    home_stats = game_stats["home"]
    away_stats = game_stats["away"]
    H_TPOS = home_stats["FGA"] + 0.44 * home_stats["FTA"] + home_stats["PTO"] - home_stats["OREB"]
    A_TPOS = away_stats["FGA"] + 0.44 * away_stats["FTA"] + away_stats["PTO"] - away_stats["OREB"]
    H_OR = A_DR = home_stats["PP"]*100 / H_TPOS if H_TPOS != 0 else 0
    H_DR = A_OR = away_stats["PP"]*100 / A_TPOS if A_TPOS != 0 else 0
    home_stats["NR"] = H_OR - H_DR
    away_stats["NR"] = A_OR - A_DR
    
    return game_stats

def kbl_decoder(game_path: dict) -> tuple[dict, dict]:
    with open(game_path, "r", encoding="utf-8") as file:
        game_log_data = json.load(file)

    metainfo = game_log_data["metainfo"]

    game_stats = {"home": dict(BASE_STAT), "away": dict(BASE_STAT)}

    game_stats["home"]["TEAM"] = metainfo["home"]["code"]
    game_stats["away"]["TEAM"] = metainfo["away"]["code"]
    
    not_mapping_logs = {}
    do_not_understand_logs = {}
    do_not_understand_teams = {}

    all_logs = game_log_data["logs"]
    total_min = 2400 if all_logs[-1]["q"] == "Q4" else 2700
    for idx, log in enumerate(all_logs):
        key_json = {
            "001": "게임시작",
            "003": "작전타임",
            "009": "게임종료",
            "101": "교체(IN)",
            "102": "교체(OUT)",
            "201": "2점슛성공",
            "202": "2점슛시도",
            "203": "자유투성공",
            "204": "자유투시도",
            "205": "3점슛성공",
            "206": "3점슛시도",
            "207": "덩크슛성공",
            "209": "공격리바운드",
            "210": "수비리바운드",
            "211": "어시스트",
            "212": "스틸",
            "213": "블록",
            "214": "턴오버",
            "215": "파울자유투",
            "216": "파울",
            "217": "팀속공",
            "218": "팀리바운드",
            "221": "굿디펜스",
            "223": "팀턴오버",
            "224": "기타파울",
            "225": "팀파울",
            "226": "스크린어시스트",
            "227": "디플렉션"
        }
        log_name = key_json[log["a"]] if log["a"] in key_json else None
        if log_name is None:
            if log["a"] not in do_not_understand_logs: do_not_understand_logs[log["a"]] = json.dumps(log, ensure_ascii=False)
            continue
        if log_name == "게임시작" or log_name == "게임종료":
            continue
        
        team_key = None
        if log["t"].isdigit():
            if int(log["t"]) == metainfo["home"]["code"]: team_key = "home"
            elif int(log["t"]) == metainfo["away"]["code"]: team_key = "away"
        if team_key is None:
            if log["t"] not in do_not_understand_teams: do_not_understand_teams[log["t"]] = json.dumps(log, ensure_ascii=False)
            continue
        
        if log_name == "팀속공":
            fast_break_logs = []
            for fb_idx_back in range(idx-1, -1, -1):
                if all_logs[fb_idx_back]["q"] != log["q"] or all_logs[fb_idx_back]["t"] != log["t"]:
                    break
                fast_break_logs.append(all_logs[fb_idx_back])
            
            for fb_idx_forward in range(idx+1, len(all_logs)):
                if all_logs[fb_idx_forward]["q"] != log["q"] or all_logs[fb_idx_forward]["t"] != log["t"]:
                    break
                fast_break_logs.append(all_logs[fb_idx_forward])
            
            fast_break_points = 0
            for fb_log in fast_break_logs:
                if fb_log["a"] == "203":  # 자유투성공
                    fast_break_points += 1
                elif fb_log["a"] == "201":  # 2점슛성공
                    fast_break_points += 2
                elif fb_log["a"] == "205":  # 3점슛성공
                    fast_break_points += 3
                elif fb_log["a"] == "207":  # 덩크슛성공
                    fast_break_points += 2
            if fast_break_points == 0:
                print(f"뭔가 이상: {json.dumps(log, ensure_ascii=False)}")
            game_stats[team_key]["SWM"] += fast_break_points
        
        key_map = KBL_STAT_MAP[log_name] if log_name in KBL_STAT_MAP else None
        if key_map is None:
            if log_name not in not_mapping_logs: not_mapping_logs[log_name] = json.dumps(log, ensure_ascii=False)
            continue
        for stat_key, increment in key_map.items():
            game_stats[team_key][stat_key] += increment

    game_stats = final_calculate(game_stats)
    game_stats["home"]["MIN"] = total_min
    game_stats["away"]["MIN"] = total_min
    
    if do_not_understand_logs:
        print("Do not understand logs:")
        for k, v in do_not_understand_logs.items():
            print(f"  Code: {k} -> Log: {v}")
    if do_not_understand_teams:
        print("Do not understand teams:")
        for k, v in do_not_understand_teams.items():
            print(f"  Team: {k} -> Log: {v}")
    if not_mapping_logs:
        print("Not mapping logs:")
        for k, v in not_mapping_logs.items():
            print(f"  Log Name: {k} -> Log: {v}")
    
    empty_stats = []
    for stat_key in game_stats["home"].keys():
        if game_stats["home"][stat_key] == 0 and game_stats["away"][stat_key] == 0:
            empty_stats.append(stat_key)

    last_quarter = all_logs[-1]["q"]
    return game_stats, metainfo, last_quarter


if __name__ == "__main__":
    game_stats, all_metainfo, last_quarter = kbl_decoder("kbl_quarters_data.json")
    print(json.dumps(all_metainfo, ensure_ascii=False, indent=2))
    print(json.dumps(game_stats, ensure_ascii=False, indent=2))