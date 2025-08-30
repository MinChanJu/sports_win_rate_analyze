import json

# KBL 공식 데이터 변수명을 매핑하는 딕셔너리입니다.
KBL_VARS_MAP = {
    "어시스트": "AST",
    "블록": "BLK",
    "수비리바운드": "DREB",
    "공격리바운드": "OREB",
    "덩크슛성공": "DK",
    "덩크슛시도": "DKA",
    "2점슛성공": "2PM",
    "2점슛시도": "2PA",
    "자유투성공": "FTM",
    "자유투시도": "FTA",
    "3점슛성공": "3PM",
    "3점슛시도": "3PA",
    "스틸": "STL",
    "턴오버": "TO",
    "파울": "PF",
    "속공": "FBP",
    "2차 찬스 득점": "SCP",
    "최다 연속 득점": "MCP",
    "팀리바운드": "TeamReb",
    "팀파울": "TeamF"
}

def calculate_percentages(player_stats: dict) -> dict:
    """
    선수별 raw 데이터를 기반으로 슈팅 성공률을 계산합니다.
    """
    for stats in player_stats.values():
        stats["FGA"] = stats["2PA"] + stats["3PA"]
        stats["FGM"] = stats["2PM"] + stats["3PM"]
        
        stats["2P%"] = round((stats["2PM"] / stats["2PA"]) * 100, 1) if stats["2PA"] > 0 else 0.0
        stats["3P%"] = round((stats["3PM"] / stats["3PA"]) * 100, 1) if stats["3PA"] > 0 else 0.0
        stats["FT%"] = round((stats["FTM"] / stats["FTA"]) * 100, 1) if stats["FTA"] > 0 else 0.0
        stats["FG%"] = round((stats["FGM"] / stats["FGA"]) * 100, 1) if stats["FGA"] > 0 else 0.0
            
    return player_stats

def process_quarter_log(metainfo: dict, quarter_log: list) -> dict:
    """
    한 쿼터의 로그 데이터를 처리하여 선수별 지표를 계산하고, 팀별로 구분하여 반환합니다.
    """
    home_players = metainfo["home"]["players"]
    away_players = metainfo["away"]["players"]
    home_team_name = metainfo["home"]["name"]
    away_team_name = metainfo["away"]["name"]
    
    home_player_stats = {player: {
        "2PM": 0, "2PA": 0, "FGM": 0, "FGA": 0, "FTM": 0, "FTA": 0,
        "3PM": 0, "3PA": 0, "AST": 0, "BLK": 0, "DREB": 0, "OREB": 0,
        "STL": 0, "TO": 0, "PF": 0, "FBP": 0, "SCP": 0, "DK": 0, "DKA": 0,
        "PP": 0, "FG%": 0.0, "2P%": 0.0, "3P%": 0.0, "FT%": 0.0
    } for player in home_players}
    
    away_player_stats = {player: {
        "2PM": 0, "2PA": 0, "FGM": 0, "FGA": 0, "FTM": 0, "FTA": 0,
        "3PM": 0, "3PA": 0, "AST": 0, "BLK": 0, "DREB": 0, "OREB": 0,
        "STL": 0, "TO": 0, "PF": 0, "FBP": 0, "SCP": 0, "DK": 0, "DKA": 0,
        "PP": 0, "FG%": 0.0, "2P%": 0.0, "3P%": 0.0, "FT%": 0.0
    } for player in away_players}

    for log_entry in quarter_log:
        for team_key in ["home", "away"]:
            event = log_entry.get(team_key)
            if not event:
                continue
            
            players_list = home_players if team_key == "home" else away_players
            stats_dict = home_player_stats if team_key == "home" else away_player_stats
            
            for player in players_list:
                if player in event:
                    stats = stats_dict[player]
                    
                    if "3점슛성공" in event:
                        stats["3PM"] += 1; stats["3PA"] += 1; stats["PP"] += 3
                    elif "2점슛성공" in event:
                        stats["2PM"] += 1; stats["2PA"] += 1; stats["PP"] += 2
                    elif "자유투성공" in event:
                        stats["FTM"] += 1; stats["FTA"] += 1; stats["PP"] += 1
                    elif "덩크슛성공" in event:
                        stats["DK"] += 1; stats["DKA"] += 1
                    elif "3점슛시도" in event:
                        stats["3PA"] += 1
                    elif "2점슛시도" in event:
                        stats["2PA"] += 1
                    elif "자유투시도" in event:
                        stats["FTA"] += 1
                    elif "덩크슛시도" in event:
                        stats["DKA"] += 1
                    elif "어시스트" in event:
                        stats["AST"] += 1
                    elif "블록" in event:
                        stats["BLK"] += 1
                    elif "수비리바운드" in event:
                        stats["DREB"] += 1
                    elif "공격리바운드" in event:
                        stats["OREB"] += 1
                    elif "스틸" in event:
                        stats["STL"] += 1
                    elif "턴오버" in event:
                        stats["TO"] += 1
                    elif "파울자유투" in event:
                        stats["PF"] += 1; stats["FTA"] += 1
                    elif "파울" in event:
                        stats["PF"] += 1
    
    home_player_stats = calculate_percentages(home_player_stats)
    away_player_stats = calculate_percentages(away_player_stats)
    
    return {
        home_team_name: home_player_stats,
        away_team_name: away_player_stats
    }


def process_game_log(game_log_data: dict) -> dict:
    """
    전체 경기 로그 데이터를 받아 메타 정보와 쿼터별 선수 기록을 반환합니다.
    """
    metainfo = game_log_data.get("metainfo", {})
    quarters = metainfo.get("quarters", [])
    
    game_stats_by_quarter = {}
    
    for quarter in quarters:
        if quarter in game_log_data:
            quarter_log = game_log_data[quarter]
            quarter_stats = process_quarter_log(metainfo, quarter_log)
            game_stats_by_quarter[quarter] = quarter_stats
            
    # 최종 결과 딕셔너리 생성
    final_result = {
        "metainfo": metainfo,
        "quarterly_stats": game_stats_by_quarter
    }
            
    return final_result

# 예시 JSON 데이터를 파이썬 딕셔너리로 직접 정의
game_data = {
    "metainfo": {
        "url": "https://www.kbl.or.kr/match/record/S45G01N13/20241025", "seasonName": "2024-2025", "gameKey": "S45G01N13", "date": "20241025",
        "home": {"name": "수원 KT", "score": 77, "players": ["한희원", "최창진", "문성곤", "이현석", "허훈", "박준영", "최진광", "이두원", "고찬혁", "문정현", "제레미아 틸먼", "레이션 해먼즈"]},
        "away": {"name": "서울 SK", "score": 75, "players": ["김선형", "오세근", "최부경", "최원혁", "장문호", "안영준", "자밀 워니", "김형빈", "아이재아 힉스", "박민우", "오재현", "고메즈 델 리아노"]},
        "winner": "home", "quarters": ["Q1", "Q2", "Q3", "Q4"]},
}
# 함수를 호출하여 전체 쿼터별 선수 기록을 얻습니다.
all_quarter_stats = process_game_log(game_data)

# 최종 결과 딕셔너리를 출력합니다.
print(json.dumps(all_quarter_stats, indent=4, ensure_ascii=False))