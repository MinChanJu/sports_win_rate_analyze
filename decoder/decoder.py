#메타인포도 같이 반환
import json

# KBL 공식 데이터 변수명을 매핑하는 딕셔너리입니다.
# 로그 데이터의 한국어 명칭을 미리 정의한 영어 변수명으로 변환하는 데 사용됩니다.
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
        # 필드골(야투) 성공/시도 합산
        stats["FGA"] = stats["2PA"] + stats["3PA"]
        stats["FGM"] = stats["2PM"] + stats["3PM"]
        
        # 2점슛 성공률 (2P%)
        stats["2P%"] = round((stats["2PM"] / stats["2PA"]) * 100, 1) if stats["2PA"] > 0 else 0.0
        # 3점슛 성공률 (3P%)
        stats["3P%"] = round((stats["3PM"] / stats["3PA"]) * 100, 1) if stats["3PA"] > 0 else 0.0
        # 자유투 성공률 (FT%)
        stats["FT%"] = round((stats["FTM"] / stats["FTA"]) * 100, 1) if stats["FTA"] > 0 else 0.0
        # 필드골 성공률 (FG%)
        stats["FG%"] = round((stats["FGM"] / stats["FGA"]) * 100, 1) if stats["FGA"] > 0 else 0.0
            
    return player_stats

def process_quarter_log(metainfo: dict, quarter_log: list) -> dict:
    """
    한 쿼터의 로그 데이터를 처리하여 선수별 지표를 계산하고 반환합니다.
    """
    home_players = metainfo["home"]["players"]
    away_players = metainfo["away"]["players"]
    all_players = home_players + away_players

    player_stats = {}
    for player_name in all_players:
        player_stats[player_name] = {
            "2PM": 0, "2PA": 0, "FGM": 0, "FGA": 0, "FTM": 0, "FTA": 0,
            "3PM": 0, "3PA": 0, "AST": 0, "BLK": 0, "DREB": 0, "OREB": 0,
            "STL": 0, "TO": 0, "PF": 0, "FBP": 0, "SCP": 0, "DK": 0, "DKA": 0,
            "PP": 0, "FG%": 0.0, "2P%": 0.0, "3P%": 0.0, "FT%": 0.0
        }

    for log_entry in quarter_log:
        for team_key in ["home", "away"]:
            event = log_entry.get(team_key)
            if not event:
                continue
            
            players_list = home_players if team_key == "home" else away_players
            for player in players_list:
                if player in event:
                    # 이벤트 종류에 따라 지표를 업데이트합니다.
                    stats = player_stats[player]
                    
                    if "3점슛성공" in event:
                        stats["3PM"] += 1
                        stats["3PA"] += 1
                        stats["PP"] += 3
                    elif "2점슛성공" in event:
                        stats["2PM"] += 1
                        stats["2PA"] += 1
                        stats["PP"] += 2
                    elif "자유투성공" in event:
                        stats["FTM"] += 1
                        stats["FTA"] += 1
                        stats["PP"] += 1
                    elif "덩크슛성공" in event:
                        stats["DK"] += 1
                        stats["DKA"] += 1
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
                        stats["PF"] += 1
                        stats["FTA"] += 1
                    elif "파울" in event:
                        stats["PF"] += 1
    
    return calculate_percentages(player_stats)

def process_game_log(game_log_data: dict) -> dict:
    """
    전체 경기 로그 데이터를 받아 쿼터별 선수 기록을 반환합니다.
    """
    metainfo = game_log_data.get("metainfo", {})
    quarters = metainfo.get("quarters", [])
    
    game_stats_by_quarter = {}
    
    for quarter in quarters:
        if quarter in game_log_data:
            quarter_log = game_log_data[quarter]
            quarter_stats = process_quarter_log(metainfo, quarter_log)
            game_stats_by_quarter[quarter] = quarter_stats
            
    return game_stats_by_quarter

# 예시 JSON 데이터를 파이썬 딕셔너리로 직접 정의
game_data = {
    "metainfo": {
        "url": "https://www.kbl.or.kr/match/record/S45G01N13/20241025", "seasonName": "2024-2025", "gameKey": "S45G01N13", "date": "20241025",
        "home": {"name": "수원 KT", "score": 77, "players": ["한희원", "최창진", "문성곤", "이현석", "허훈", "박준영", "최진광", "이두원", "고찬혁", "문정현", "제레미아 틸먼", "레이션 해먼즈"]},
        "away": {"name": "서울 SK", "score": 75, "players": ["김선형", "오세근", "최부경", "최원혁", "장문호", "안영준", "자밀 워니", "김형빈", "아이재아 힉스", "박민우", "오재현", "고메즈 델 리아노"]},
        "winner": "home", "quarters": ["Q1", "Q2", "Q3", "Q4"]},
    "Q1": [{"home": "", "away": "", "time": "1쿼터 시작"}, {"home": "", "away": "아이재아 힉스 교체(OUT)", "time": "0:00"}, {"home": "", "away": "김형빈 교체(OUT)", "time": "0:00"}, {"home": "", "away": "고메즈 델 리아노 교체(OUT)", "time": "0:00"}, {"home": "", "away": "안영준 교체(OUT)", "time": "0:00"}, {"home": "", "away": "최원혁 교체(OUT)", "time": "0:00"}, {"home": "제레미아 틸먼 교체(OUT)", "away": "", "time": "0:00"}, {"home": "박준영 교체(OUT)", "away": "", "time": "0:00"}, {"home": "문정현 교체(OUT)", "away": "", "time": "0:00"}, {"home": "이현석 교체(OUT)", "away": "", "time": "0:00"}, {"home": "허훈 교체(OUT)", "away": "", "time": "0:00"}, {"home": "", "away": "", "time": "게임종료"}, {"home": "이현석 공격리바운드", "away": "", "time": "0:01"}, {"home": "허훈 3점슛시도", "away": "", "time": "0:01"}, {"home": "허훈 교체(IN)", "away": "", "time": "0:07"}, {"home": "최창진 교체(OUT)", "away": "", "time": "0:07"}, {"home": "팀리바운드", "away": "", "time": "0:07"}, {"home": "", "away": "안영준 3점슛시도", "time": "0:08"}, {"home": "", "away": "안영준 공격리바운드", "time": "0:09"}, {"home": "제레미아 틸먼 블록", "away": "", "time": "0:10"}, {"home": "", "away": "김형빈 2점슛시도", "time": "0:12"}, {"home": "문정현 자유투성공", "away": "", "time": "0:27"}, {"home": "박준영 어시스트", "away": "", "time": "0:27"}, {"home": "문정현 자유투성공", "away": "", "time": "0:27"}, {"home": "최창진 교체(IN)", "away": "", "time": "0:27"}, {"home": "허훈 교체(OUT)", "away": "", "time": "0:27"}, {"home": "이현석 교체(IN)", "away": "", "time": "0:27"}, {"home": "한희원 교체(OUT)", "away": "", "time": "0:27"}, {"home": "", "away": "김형빈 교체(IN)", "time": "0:27"}, {"home": "", "away": "오세근 교체(OUT)", "time": "0:27"}, {"home": "", "away": "고메즈 델 리아노 교체(IN)", "time": "0:27"}, {"home": "", "away": "김선형 교체(OUT)", "time": "0:27"}, {"home": "제레미아 틸먼 교체(IN)", "away": "", "time": "0:27"}, {"home": "레이션 해먼즈 교체(OUT)", "away": "", "time": "0:27"}, {"home": "", "away": "팀파울", "time": "0:27"}, {"home": "", "away": "오세근 파울자유투", "time": "0:27"}, {"home": "박준영 스틸", "away": "", "time": "0:29"}, {"home": "", "away": "최원혁 턴오버", "time": "0:30"}, {"home": "팀속공", "away": "", "time": "0:53"}, {"home": "허훈 어시스트", "away": "", "time": "0:53"}, {"home": "레이션 해먼즈 2점슛성공", "away": "", "time": "0:53"}, {"home": "한희원 스틸", "away": "", "time": "0:57"}, {"home": "", "away": "김선형 턴오버", "time": "0:59"}, {"home": "문정현 2점슛성공", "away": "", "time": "1:12"}, {"home": "", "away": "팀파울", "time": "1:21"}, {"home": "", "away": "김선형 파울", "time": "1:21"}, {"home": "박준영 수비리바운드", "away": "", "time": "1:21"}, {"home": "", "away": "김선형 2점슛시도", "time": "1:21"}, {"home": "", "away": "오세근 수비리바운드", "time": "1:27"}, {"home": "한희원 2점슛시도", "away": "", "time": "1:29"}, {"home": "레이션 해먼즈 수비리바운드", "away": "", "time": "1:43"}, {"home": "", "away": "안영준 자유투시도", "time": "1:47"}, {"home": "", "away": "아이재아 힉스 교체(IN)", "time": "1:47"}, {"home": "", "away": "자밀 워니 교체(OUT)", "time": "1:47"}, {"home": "팀파울", "away": "", "time": "1:47"}, {"home": "허훈 파울자유투", "away": "", "time": "1:47"}, {"home": "", "away": "팀속공", "time": "1:47"}, {"home": "", "away": "자밀 워니 어시스트", "time": "1:47"}, {"home": "", "away": "안영준 2점슛성공", "time": "1:47"}, {"home": "", "away": "자밀 워니 스틸", "time": "1:49"}, {"home": "허훈 턴오버", "away": "", "time": "1:50"}, {"home": "", "away": "자밀 워니 어시스트", "time": "2:04"}, {"home": "", "away": "안영준 3점슛성공", "time": "2:04"}, {"home": "한희원 2점슛성공", "away": "", "time": "2:21"}, {"home": "", "away": "김선형 어시스트", "time": "2:39"}, {"home": "", "away": "안영준 2점슛성공", "time": "2:39"}, {"home": "레이션 해먼즈 2점슛성공", "away": "", "time": "2:48"}, {"home": "한희원 스틸", "away": "", "time": "2:54"}, {"home": "", "away": "안영준 턴오버", "time": "2:55"}, {"home": "", "away": "안영준 스틸", "time": "3:00"}, {"home": "허훈 턴오버", "away": "", "time": "3:01"}, {"home": "", "away": "팀파울", "time": "3:11"}, {"home": "", "away": "최원혁 파울", "time": "3:11"}, {"home": "박준영 공격리바운드", "away": "", "time": "3:11"}, {"home": "문정현 2점슛시도", "away": "", "time": "3:11"}, {"home": "한희원 수비리바운드", "away": "", "time": "3:18"}, {"home": "", "away": "안영준 3점슛시도", "time": "3:20"}, {"home": "", "away": "팀리바운드", "time": "3:33"}, {"home": "레이션 해먼즈 3점슛시도", "away": "", "time": "3:33"}, {"home": "", "away": "안영준 자유투성공", "time": "3:49"}, {"home": "", "away": "안영준 자유투성공", "time": "3:49"}, {"home": "박준영 교체(IN)", "away": "", "time": "3:49"}, {"home": "이두원 교체(OUT)", "away": "", "time": "3:49"}, {"home": "팀파울", "away": "", "time": "3:49"}, {"home": "이두원 파울자유투", "away": "", "time": "3:49"}, {"home": "레이션 해먼즈 3점슛성공", "away": "", "time": "3:58"}, {"home": "레이션 해먼즈 수비리바운드", "away": "", "time": "4:09"}, {"home": "", "away": "오세근 2점슛시도", "time": "4:10"}, {"home": "", "away": "자밀 워니 수비리바운드", "time": "4:23"}, {"home": "한희원 3점슛시도", "away": "", "time": "4:25"}, {"home": "이두원 공격리바운드", "away": "", "time": "4:27"}, {"home": "한희원 2점슛시도", "away": "", "time": "4:28"}, {"home": "한희원 공격리바운드", "away": "", "time": "4:29"}, {"home": "이두원 2점슛시도", "away": "", "time": "4:32"}, {"home": "", "away": "팀속공", "time": "4:51"}, {"home": "", "away": "자밀 워니 어시스트", "time": "4:51"}, {"home": "", "away": "김선형 2점슛성공", "time": "4:51"}, {"home": "", "away": "자밀 워니 수비리바운드", "time": "4:54"}, {"home": "허훈 2점슛시도", "away": "", "time": "4:56"}, {"home": "", "away": "최원혁 교체(IN)", "time": "5:03"}, {"home": "", "away": "오재현 교체(OUT)", "time": "5:03"}, {"home": "", "away": "팀파울", "time": "5:03"}, {"home": "", "away": "오재현 파울", "time": "5:03"}, {"home": "", "away": "자밀 워니 2점슛성공", "time": "5:12"}, {"home": "팀속공", "away": "", "time": "5:33"}, {"home": "레이션 해먼즈 자유투성공", "away": "", "time": "5:33"}, {"home": "레이션 해먼즈 자유투시도", "away": "", "time": "5:33"}, {"home": "", "away": "팀파울", "time": "5:33"}, {"home": "", "away": "오재현 파울자유투", "time": "5:33"}, {"home": "레이션 해먼즈 수비리바운드", "away": "", "time": "5:36"}, {"home": "", "away": "오세근 2점슛시도", "time": "5:38"}, {"home": "", "away": "오재현 공격리바운드", "time": "5:42"}, {"home": "", "away": "오세근 3점슛시도", "time": "5:43"}, {"home": "", "away": "오재현 공격리바운드", "time": "5:47"}, {"home": "", "away": "안영준 3점슛시도", "time": "5:48"}, {"home": "", "away": "오세근 스틸", "time": "5:54"}, {"home": "허훈 턴오버", "away": "", "time": "5:55"}, {"home": "", "away": "오재현 자유투성공", "time": "6:13"}, {"home": "팀파울", "away": "", "time": "6:13"}, {"home": "레이션 해먼즈 파울자유투", "away": "", "time": "6:13"}, {"home": "", "away": "자밀 워니 어시스트", "time": "6:13"}, {"home": "", "away": "오재현 2점슛성공", "time": "6:13"}, {"home": "", "away": "자밀 워니 수비리바운드", "time": "6:18"}, {"home": "허훈 2점슛시도", "away": "", "time": "6:19"}]
}

# 함수를 호출하여 쿼터 선수별 기록을 얻습니다.
all_quarter_stats = process_game_log(game_data)
q1_stats = all_quarter_stats["Q1"]
