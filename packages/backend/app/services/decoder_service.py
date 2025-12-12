import json
import numpy as np
from pathlib import Path
from app.core.config import settings
from app.utils.stat import BASE_STAT, KBL_STAT_MAP


class DecoderService:
  @staticmethod
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
    H_TPOS = (home_stats["FGA"] + 0.44 * home_stats["FTA"] + home_stats["PTO"] - home_stats["OREB"])
    A_TPOS = (away_stats["FGA"] + 0.44 * away_stats["FTA"] + away_stats["PTO"] - away_stats["OREB"])
    H_OR = A_DR = home_stats["PP"]*100 / H_TPOS if H_TPOS != 0 else 0
    H_DR = A_OR = away_stats["PP"]*100 / A_TPOS if A_TPOS != 0 else 0
    home_stats["NR"] = H_OR - H_DR
    away_stats["NR"] = A_OR - A_DR
    
    home_stats["PACE"] = ((H_TPOS + A_TPOS) / 2) * (2400 / home_stats["MIN"]) if home_stats["MIN"] != 0 else 0
    away_stats["PACE"] = ((H_TPOS + A_TPOS) / 2) * (2400 / away_stats["MIN"]) if away_stats["MIN"] != 0 else 0
    
    return game_stats

  @staticmethod
  def preprocess_data(raw_data: dict) -> list[dict]:
    """
    크롤링된 데이터를 모델 입력 형태로 가공합니다.

    Args:
      raw_data: 크롤링된 원본 데이터

    Returns:
      torch.Tensor: shape (1, 88) - 모델 입력용 텐서
    """
    all_logs = raw_data["logs"]
    meta = raw_data["meta"]
    h_code = int(meta["home"]["code"])
    a_code = int(meta["away"]["code"])
    
    game_stats = {"home": dict(BASE_STAT), "away": dict(BASE_STAT)}
    game_stats["home"]["TEAM"] = h_code
    game_stats["away"]["TEAM"] = a_code
    
    current_lead_team = None
    current_run = 0
    current_goal = None
    
    quarter_types = ["Q1", "Q2", "Q3", "Q4", "X1", "X2", "X3"]
    quarter_times = {"Q1": 600, "Q2": 600, "Q3": 600, "Q4": 600, "X1": 300, "X2": 300, "X3": 300}

    CODE_MAP_PATH = Path(__file__).parent.parent / settings.CODE_MAP_PATH
    key_json = json.load(open(CODE_MAP_PATH, "r", encoding="utf-8"))
  
    FEATURE_ORDER_PATH = Path(__file__).parent.parent / settings.FEATURE_ORDER_PATH
    if not FEATURE_ORDER_PATH.exists():
      raise FileNotFoundError(f"Feature order file not found: {FEATURE_ORDER_PATH}")
    feature_order = json.loads(FEATURE_ORDER_PATH.read_text(encoding="utf-8"))
  
    total_records = []
    prev_quarter = "Q1"
    quarter_net_ratings = { "home": [], "away": [], "order": [] }
    for idx, log in enumerate(all_logs):
      log_name = key_json[log["a"]] if log["a"] in key_json else None
      if log_name is None:
        continue
      
      current_quarter = log["q"]
      if current_quarter not in quarter_types:
        print(f"알수없는 쿼터 타입: {current_quarter}")
        continue
      
      if current_quarter != prev_quarter:
        # 쿼터별 Net Rating 저장
        quarter_net_ratings["home"].append(game_stats["home"]["NR"])
        quarter_net_ratings["away"].append(game_stats["away"]["NR"])
        quarter_net_ratings["order"].append(prev_quarter)
        prev_quarter = current_quarter
      
      current_time = quarter_times[current_quarter] - (log["m"] * 60 + log["s"])
      for qt in quarter_types:
        if qt == current_quarter: break
        current_time += quarter_times[qt]
      game_stats["home"]["MIN"] = current_time
      game_stats["away"]["MIN"] = current_time
      
      team_key = None
      if log["t"].isdigit():
        if int(log["t"]) == h_code: team_key = "home"
        elif int(log["t"]) == a_code: team_key = "away"
      if team_key is None:
        if log_name != "게임시작" and log_name != "게임종료": print(f"알수없는 팀 코드: '{log}', h_code: {h_code}, a_code: {a_code}, log_name: {log_name}")
        continue
      
      if log_name == '교체(OUT)':
        if 'c' in log:
          if log['c'] in ["106_0", "106_1", "106_3", "106_4", "106_5"]: game_stats[team_key]["EJ"] += 1
          elif log['c'] in ["101_0", "104_0"]: pass
      
      if log_name == "기타파울":
        if log["f"] in ["TCF", "BTB", "BTC", "DTF"]: game_stats[team_key]["TF"] += 1
        elif log["f"] in ["FRF", "UC1", "UC2", "UC3", "UC4", "UC5"]: game_stats[team_key]["UF"] += 1
        game_stats[team_key]["TPF"] += 1
      
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

        game_stats[team_key]["SWM"] += fast_break_points

      key_map = KBL_STAT_MAP[log_name] if log_name in KBL_STAT_MAP else None
      if key_map is None:
        continue
      for stat_key, increment in key_map.items():
        game_stats[team_key][stat_key] += increment
      
      next_pp = (game_stats[team_key]["2PM"] * 2) + (game_stats[team_key]["3PM"] * 3)  + game_stats[team_key]["FTM"]
      next_pa = game_stats[team_key]["2PA"] + game_stats[team_key]["3PA"] + game_stats[team_key]["FTA"]
      
      # 현재 연속 득점/실점
      if (team_key == "home") and (game_stats["home"]["PP"] < next_pp):
        if current_goal == "home": current_run += next_pp - game_stats["home"]["PP"]
        else:
          current_run = next_pp - game_stats["home"]["PP"]
          current_goal = "home"
      elif (team_key == "away") and (game_stats["away"]["PP"] < next_pp):
        if current_goal == "away": current_run += next_pp - game_stats["away"]["PP"]
        else:
          current_run = next_pp - game_stats["away"]["PP"]
          current_goal = "away"
      
      game_stats["home"]["CR"] = current_run
      game_stats["away"]["CR"] = current_run
      
      # 개인 득점
      game_stats[team_key]["PP"] = next_pp
      game_stats[team_key]["PA"] = next_pa
      
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

      game_stats = DecoderService.final_calculate(game_stats)
      row = {
        f"{'H' if team == 'home' else 'A'}_{stat}": value
        for team, stats in game_stats.items()
        for stat, value in stats.items()
      }
      DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "winner", "n"]
      array = np.array([row.get(feature, 0.0) for feature in feature_order if feature not in DEFAULT_DROP_COLS], dtype=np.float32)
      min = int(log["m"])
      sec = int(log["s"])
      quarter = log["q"]
      last_time_sec = (
          600 - (min * 60 + sec)
          if quarter.startswith("Q")
          else 300 - (min * 60 + sec)
      )
      total_time_sec = (
        ((int(quarter[1]) - 1) * 10 * 60 + last_time_sec)
        if quarter.startswith("Q")
        else (
          2400 + (int(quarter[1]) - 1) * 5 * 60 + last_time_sec
          if quarter.startswith("X")
          else None
        )
      )
      if total_time_sec is None:
        continue
      total_records.append({"total_time_sec": total_time_sec, "array": array})
    
    # 쿼터별 Net Rating 마지막 저장
    quarter_net_ratings["home"].append(game_stats["home"]["NR"])
    quarter_net_ratings["away"].append(game_stats["away"]["NR"])
    quarter_net_ratings["order"].append(prev_quarter)
    
    last_game_stats = game_stats
    return total_records, last_game_stats, quarter_net_ratings