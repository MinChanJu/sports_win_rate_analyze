import json

KBL_STAT_MAP = [
    ("팀파울", {"TPF": 1}),
    ("파울", {"PPF": 1}),
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
    "TEAM": 0,  # 1. 팀명
    "AST": 0,  # 2. 어시스트
    "BLK": 0,  # 3. 블록
    "DREB": 0,  # 4. 수비 리바운드
    "DKM": 0,  # 5. 덩크슛 성공
    "DKA": 0,  # 6. 덩크슛 시도
    "SWA": 0,  # 8. 팀 속공
    "2PM": 0,  # 9. 2점슛 성공
    "2PA": 0,  # 10. 2점슛 시도
    "FGA": 0,  # 11. 필드골 시도
    "FGM": 0,  # 12. 필드골 성공
    "TPF": 0,  # 13. 팀 파울
    "FTM": 0,  # 14. 자유투 성공
    "FTA": 0,  # 15. 자유투 시도
    "PPF": 0,  # 17. 개인 파울
    "SUB": 0,  # 18. 교체
    "OREB": 0,  # 20. 공격 리바운드
    "PP": 0,  # 23. 개인 득점
    "PA": 0,  # 24. 개인 득점 시도
    "PRB": 0,  # 26. 개인 리바운드
    "STL": 0,  # 28. 스틸
    "3PM": 0,  # 30. 3점슛 성공
    "3PA": 0,  # 31. 3점슛 시도
    "TTO": 0,  # 32. 팀 턴오버
    "FTM": 0,  # 33. 자유투 성공 (중복)
    "FTA": 0,  # 34. 자유투 시도 (중복)
    "TRB": 0,  # 37. 팀 리바운드
    "PTO": 0,  # 39. 개인 턴오버
    "MIN": 0,  # 16. 경기 시간 (전체 시간으로 계싼)
    "MIN_M": 0,  # 21. 플레이 시간, 분 (전체 시간을 분 단위로 환산)
    "MIN_S": 0,  # 22. 플레이 시간, 초 (전체 시간을 초 단위로 환산)

    "BPF": 0,  # 35. 벤치 반칙
    "BPS": 0,  # 43. 벤치 득점
    "DPS": 0,  # 42. 2차 찬스 득점
    "EFF": 0,  # 7. 효율성
    "EJ": 0,  # 36. 반칙 퇴장
    "FST": 0,  # 19. 첫 교체
    "MXD": 0,  # 45. 최다 리드 점수
    "MXS": 0,  # 44. 최다 연속 득점
    "PPS": 0,  # 25. 선수 점수 (XX)
    "PPT": 0,  # 46. 득점 우위 시간
    "SWM": 0,  # 40. 속공에 의한 득점
    "TOM": 0,  # 41. 턴오버에 의한 득점
    "TPF_G": 0,  # 38. 팀 경기당 반칙
    "TPF_T": 0,  # 29. 테크니컬 파울
    "TPS": 0,  # 27. 팀 점수 (XX)
}


def play_calculate(game_stats: dict) -> dict:
    for stats in game_stats.values():
        stats["PP"] = (
            2 * stats["2PM"] + 3 * stats["3PM"] + stats["FTM"] + 2 * stats["DKM"]
        )
        stats["PA"] = stats["2PA"] + stats["3PA"] + stats["FTA"] + stats["DKA"]
        stats["PRB"] = stats["OREB"] + stats["DREB"]

        stats["FGA"] = stats["2PA"] + stats["3PA"] + stats["DKA"]
        stats["FGM"] = stats["2PM"] + stats["3PM"] + stats["DKM"]

        stats["SUB"] -= 10

    return game_stats


def final_calculate(game_stats: dict) -> dict:
    for stats in game_stats.values():
        stats["SUB"] //= 2
    return game_stats


def kbl_decoder(game_path: dict) -> tuple[dict, dict]:
    with open(game_path, "r", encoding="utf-8") as file:
        game_log_data = json.load(file)

    metainfo = game_log_data["metainfo"]

    home_players = metainfo["home"]["players"]
    away_players = metainfo["away"]["players"]

    game_stats = {"home": dict(BASE_STAT), "away": dict(BASE_STAT)}
    game_stats["home"]["TEAM"] = metainfo["home"]["name"]
    game_stats["away"]["TEAM"] = metainfo["away"]["name"]

    quarters = metainfo["quarters"]

    for quarter in quarters:
        if quarter in game_log_data:
            quarter_log = game_log_data[quarter]

            for log_entry in quarter_log:
                for team_key in ["home", "away"]:
                    event = log_entry.get(team_key)
                    if not event:
                        continue

                    event_key = False
                    event_value = False
                    for key, value in KBL_STAT_MAP:
                        if key in event:
                            event_key = key
                            event_value = value
                            break
                    if not event_key:
                        print(
                            f"Unrecognized event: {event} - {metainfo['seasonName']}.{metainfo['gameKey']} {quarter}"
                        )
                        break

                    if not ("팀" in event_key or "작전시간" in event_key):
                        players_list = (
                            home_players if team_key == "home" else away_players
                        )
                        player_key = False
                        for player in players_list:
                            if player in event:
                                player_key = player
                                break
                        if not player_key:
                            print(
                                f"Unrecognized player in event: {event} - {metainfo['seasonName']}.{metainfo['gameKey']} {quarter}"
                            )
                            break

                    stats = game_stats[team_key]
                    for stat_key in event_value:
                        stats[stat_key] += event_value[stat_key]

            time = quarter_log[-1].get("time", "00:00")
            minutes, seconds = map(int, time.split(":"))
            for team in ["home", "away"]:
                game_stats[team]["MIN"] += minutes + seconds / 60
                game_stats[team]["MIN_M"] += minutes + seconds / 60
                game_stats[team]["MIN_S"] += 60 * minutes + seconds

            game_stats = play_calculate(game_stats)

    game_stats = final_calculate(game_stats)

    return game_stats, metainfo


if __name__ == "__main__":
    game_stats, all_metainfo = kbl_decoder("../kbl_data/2024-2025/S45G01N28.json")
    home = game_stats["home"]
    away = game_stats["away"]
    print(f"home: {json.dumps(home, ensure_ascii=False)}")
    print()
    print(f"away: {json.dumps(away, ensure_ascii=False)}")
    print()

    fill_stats = []
    empty_stats = []
    for stat in BASE_STAT:
        if home[stat] == 0 and away[stat] == 0:
            empty_stats.append(f'"{stat}"')
        else:
            fill_stats.append(f'"{stat}"')
    fill_stats.sort()
    print(f"Fill Stats ({len(fill_stats)}): {', '.join(fill_stats)}")
    empty_stats.sort()
    print(f"Empty Stats ({len(empty_stats)}): {', '.join(empty_stats)}")
