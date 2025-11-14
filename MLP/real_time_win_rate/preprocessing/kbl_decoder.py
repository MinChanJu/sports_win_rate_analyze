import json
from base_stat import BASE_STAT

KBL_STAT_MAP = {
    "파울": {"TPF": 1, "PF": 1},
    "팀턴오버": {"TTO": 1},
    "턴오버": {"PTO": 1},
    "팀리바운드": {"TRB": 1},
    "팀속공": {"SWA": 1},
    "3점슛성공": {"3PM": 1, "3PA": 1},
    "2점슛성공": {"2PM": 1, "2PA": 1},
    "자유투성공": {"FTM": 1, "FTA": 1},
    "덩크슛성공": {"DKM": 1, "DKA": 1, "2PA": 1, "2PM": 1},
    "3점슛시도": {"3PA": 1},
    "2점슛시도": {"2PA": 1},
    "자유투시도": {"FTA": 1},
    "덩크슛시도": {"DKA": 1, "2PA": 1},
    "어시스트": {"AST": 1},
    "블록": {"BLK": 1},
    "수비리바운드": {"DREB": 1},
    "공격리바운드": {"OREB": 1},
    "스틸": {"STL": 1},
    "파울자유투": {"TPF": 1},
    "팀파울": {},
    "교체(IN)": {},
    "교체(OUT)": {},
    "굿디펜스": {},
    "작전타임": {},
}

def calc_possession(home, away):
    # Home Team Possession 부분
    home_missed_fg = home["FGA"] - home["FGM"]
    home_orb_factor = 1.07 * (home["OREB"] / (home["OREB"] + away["DREB"])) * home_missed_fg

    home_part = (
        home["FGA"]
        + 0.4 * home["FTA"]
        - home_orb_factor
        + home["TO"]
    )

    # Away Team Possession 부분
    away_missed_fg = away["FGA"] - away["FGM"]
    away_orb_factor = 1.07 * (away["OREB"] / (away["OREB"] + home["DREB"])) * away_missed_fg

    away_part = (
        away["FGA"]
        + 0.4 * away["FTA"]
        - away_orb_factor
        + away["TO"]
    )

    # Final Possession
    total_poss = 0.5 * (home_part + away_part)
    return total_poss

def final_calculate(game_stats: dict) -> dict:
    for team, team_stat in game_stats.items():
        # 필드골
        team_stat["FGA"] = team_stat["2PA"] + team_stat["3PA"]
        team_stat["FGM"] = team_stat["2PM"] + team_stat["3PM"]
        
        # 총 턴오버
        team_stat["TO"] = team_stat["PTO"] + team_stat["TTO"]
        
        # 개인 리바운드
        team_stat["PRB"] = team_stat["OREB"] + team_stat["DREB"]
        
        # 2차 스탯
        # 슈팅 효율성
        team_stat["TS%"] = (
            team_stat["PP"] * 100 / (2 * (team_stat["FGA"] + 0.44 * team_stat["FTA"]))
            if (team_stat["FGA"] + 0.44 * team_stat["FTA"]) != 0
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
            team_stat["PTO"] * 100 / (team_stat["FGA"] + 0.44 * team_stat["FTA"] + team_stat["PTO"])
            if (team_stat["FGA"] + 0.44 * team_stat["FTA"] + team_stat["PTO"]) != 0
            else 0
        )
        
        # 자유투 성공 비율
        team_stat["FT%"] = (
            team_stat["FTM"] * 100 / team_stat["FTA"]
            if team_stat["FTA"] != 0
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
            team_stat["AST"] / team_stat["PTO"]
            if team_stat["PTO"] != 0
            else 0
        )
        
        # 공격 리바운드 비율
        opp_stats = game_stats["away"] if team == "home" else game_stats["home"]
        team_stat["OREB%"] = (
            team_stat["OREB"] * 100 / (team_stat["OREB"] + opp_stats["DREB"])
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
    H_TPOS = 0.96 * (home_stats["FGA"] + 0.44 * home_stats["FTA"] + home_stats["PTO"] - home_stats["OREB"])
    A_TPOS = 0.96 * (away_stats["FGA"] + 0.44 * away_stats["FTA"] + away_stats["PTO"] - away_stats["OREB"])
    TPOS = (H_TPOS + A_TPOS) / 2
    print("Total Possessions Calculation:", f"H_TPOS={H_TPOS}, A_TPOS={A_TPOS}, TPOS={TPOS}")
    H_OR = A_DR = home_stats["PP"]*100 / H_TPOS if H_TPOS != 0 else 0
    H_DR = A_OR = away_stats["PP"]*100 / A_TPOS if A_TPOS != 0 else 0
    home_stats["NR"] = H_OR - H_DR
    away_stats["NR"] = A_OR - A_DR
    
    home_stats["PACE"] = ((H_TPOS + A_TPOS) / 2) * (2400 / home_stats["MIN"]) if home_stats["MIN"] != 0 else 0
    away_stats["PACE"] = ((H_TPOS + A_TPOS) / 2) * (2400 / away_stats["MIN"]) if away_stats["MIN"] != 0 else 0
    
    return game_stats

def kbl_decoder(game_path: dict, verbose: int = 0) -> tuple[dict, dict]:
    with open(game_path, "r", encoding="utf-8") as file:
        game_log_data = json.load(file)

    metainfo = game_log_data["metainfo"]
    
    print_url = False

    game_stats = {"home": dict(BASE_STAT), "away": dict(BASE_STAT)}

    game_stats["home"]["TEAM"] = metainfo["home"]["code"]
    game_stats["away"]["TEAM"] = metainfo["away"]["code"]
    
    not_mapping_logs = {}
    do_not_understand_logs = {}
    do_not_understand_teams = {}
    
    current_lead_team = None

    all_logs = game_log_data["logs"]
    key_json = json.load(open("./code_map.json", "r", encoding="utf-8"))
    for idx, log in enumerate(all_logs):
        log_name = key_json[log["a"]] if log["a"] in key_json else None
        if log_name is None:
            if log["a"] not in do_not_understand_logs: do_not_understand_logs[log["a"]] = json.dumps(log, ensure_ascii=False)
            continue
        if log_name == "게임시작":
            game_stats["home"]["MIN"] += log["m"] * 60
            game_stats["away"]["MIN"] += log["m"] * 60
            continue
        if log_name in ["게임종료", "미정의"]: continue
        
        team_key = None
        if log["t"].isdigit():
            if int(log["t"]) == metainfo["home"]["code"]: team_key = "home"
            elif int(log["t"]) == metainfo["away"]["code"]: team_key = "away"
        if team_key is None:
            if log["t"] not in do_not_understand_teams: do_not_understand_teams[log["t"]] = json.dumps(log, ensure_ascii=False)
            continue
        
        if log_name == '교체(OUT)':
            if 'c' in log:
                if log['c'] in ["106_0", "106_1", "106_3", "106_4", "106_5"]: game_stats[team_key]["EJ"] += 1
                elif log['c'] in ["101_0", "104_0"]: pass
                else: do_not_understand_logs[log["a"]+log['c']] = json.dumps(log, ensure_ascii=False)
            continue
        
        if log_name == "기타파울":
            if log["f"] in ["TCF", "BTB", "BTC", "DTF"]: game_stats[team_key]["TF"] += 1
            elif log["f"] in ["FRF", "UC1", "UC2", "UC3", "UC4", "UC5"]: game_stats[team_key]["UF"] += 1
            else: do_not_understand_logs[log["a"]+log["f"]] = json.dumps(log, ensure_ascii=False)
            game_stats[team_key]["TPF"] += 1
            continue
        
        if log_name == "팀속공":
            fast_break_logs = []
            for fb_idx_back in range(idx-1, -1, -1):
                if all_logs[fb_idx_back]["q"] != log["q"] or all_logs[fb_idx_back]["t"] != log["t"]: break
                fast_break_logs.append(all_logs[fb_idx_back])
            
            for fb_idx_forward in range(idx+1, len(all_logs)):
                if all_logs[fb_idx_forward]["q"] != log["q"] or all_logs[fb_idx_forward]["t"] != log["t"]: break
                fast_break_logs.append(all_logs[fb_idx_forward])
            
            fast_break_points = 0
            for fb_log in fast_break_logs:
                fb_log_name = key_json[fb_log["a"]] if fb_log["a"] in key_json else None
                if fb_log_name is None: continue
                
                if fb_log_name == "자유투성공": fast_break_points += 1
                elif fb_log_name == "2점슛성공": fast_break_points += 2
                elif fb_log_name == "3점슛성공": fast_break_points += 3
                elif fb_log_name == "덩크슛성공": fast_break_points += 2

            if fast_break_points == 0 and verbose > 5:
                print(f"뭔가 이상: {json.dumps(log, ensure_ascii=False)}")
            game_stats[team_key]["SWM"] += fast_break_points

        key_map = KBL_STAT_MAP[log_name] if log_name in KBL_STAT_MAP else None
        if key_map is None:
            if log_name not in not_mapping_logs: not_mapping_logs[log_name] = json.dumps(log, ensure_ascii=False)
            continue
        for stat_key, increment in key_map.items():
            game_stats[team_key][stat_key] += increment
        
        # 개인 득점
        game_stats[team_key]["PP"] = (game_stats[team_key]["2PM"] * 2) + (game_stats[team_key]["3PM"] * 3)  + game_stats[team_key]["FTM"]
        game_stats[team_key]["PA"] = game_stats[team_key]["2PA"] + game_stats[team_key]["3PA"] + game_stats[team_key]["FTA"]
        
        next_lead_team = None
        if game_stats["home"]["PP"] > game_stats["away"]["PP"]: next_lead_team = "home"
        elif game_stats["home"]["PP"] < game_stats["away"]["PP"]: next_lead_team = "away"
        else: next_lead_team = current_lead_team
        
        if current_lead_team != next_lead_team:
            game_stats['home']["LC"] += 1
            game_stats['away']["LC"] += 1
            current_lead_team = next_lead_team
        
        if game_stats["home"]["PP"] - game_stats["away"]["PP"] > game_stats["home"]["LLP"]:
            game_stats["home"]["LLP"] = game_stats["home"]["PP"] - game_stats["away"]["PP"]
        if game_stats["away"]["PP"] - game_stats["home"]["PP"] > game_stats["away"]["LLP"]:
            game_stats["away"]["LLP"] = game_stats["away"]["PP"] - game_stats["home"]["PP"]

    game_stats = final_calculate(game_stats)
    
    if do_not_understand_logs and verbose > 0:
        if print_url == False:
            print(f"Decoding game log: {metainfo['url']}")
            print_url = True
        print("Do not understand logs:")
        for k, v in do_not_understand_logs.items():
            print(f"  Code: {k} -> Log: {v}")
    if do_not_understand_teams and verbose > 1:
        if print_url == False:
            print(f"Decoding game log: {metainfo['url']}")
            print_url = True
        print("Do not understand teams:")
        for k, v in do_not_understand_teams.items():
            print(f"  Team: {k} -> Log: {v}")
    if not_mapping_logs and verbose > 2:
        if print_url == False:
            print(f"Decoding game log: {metainfo['url']}")
            print_url = True
        print("Not mapping logs:")
        for k, v in not_mapping_logs.items():
            print(f"  Log Name: {k} -> Log: {v}")
    
    empty_stats = []
    for stat_key in game_stats["home"].keys():
        if game_stats["home"][stat_key] == 0 and game_stats["away"][stat_key] == 0:
            empty_stats.append(stat_key)

    if empty_stats and verbose > 5:
        if print_url == False:
            print(f"Decoding game log: {metainfo['url']}")
            print_url = True
        print("Empty stats:")
        for stat in empty_stats:
            print(f"  Stat: {stat}")
    last_quarter = all_logs[-1]["q"]
    return game_stats, metainfo, last_quarter

if __name__ == "__main__":
    game_stats, all_metainfo, last_quarter = kbl_decoder("../../../kbl_log_data/2024-2025/S45G01N260.json", 100)
    print(f"{'':10} {all_metainfo['home']['name']:10} - {all_metainfo['away']['name']:10}")
    for stat_key in BASE_STAT.keys():
        print(f"{stat_key:10}: {game_stats['home'][stat_key]:10.3f} - {game_stats['away'][stat_key]:10.3f}")