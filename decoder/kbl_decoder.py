import json

KBL_STAT_MAP = {
    "3점슛성공": {"3PM": 1, "3PA": 1, "PP": 3},
    "2점슛성공": {"2PM": 1, "2PA": 1, "PP": 2},
    "자유투성공": {"FTM": 1, "FTA": 1, "PP": 1},
    "덩크슛성공": {"DK": 1, "DKA": 1},
    "3점슛시도": {"3PA": 1},
    "2점슛시도": {"2PA": 1},
    "자유투시도": {"FTA": 1},
    "덩크슛시도": {"DKA": 1},
    "어시스트": {"AST": 1},
    "블록": {"BLK": 1},
    "수비리바운드": {"DREB": 1},
    "공격리바운드": {"OREB": 1},
    "스틸": {"STL": 1},
    "턴오버": {"TO": 1},
    "파울자유투": {"PF": 1, "FTA": 1},
    "파울": {"PF": 1},
    "교체": {},
    "굿디펜스": {},
}

BASE_STAT = {
    "2PM": 0,
    "2PA": 0,
    "3PM": 0,
    "3PA": 0,
    "FTM": 0,
    "FTA": 0,
    "FGM": 0,
    "FGA": 0,
    "AST": 0,
    "BLK": 0,
    "DREB": 0,
    "OREB": 0,
    "STL": 0,
    "TO": 0,
    "PF": 0,
    "FBP": 0,
    "SCP": 0,
    "DK": 0,
    "DKA": 0,
    "PP": 0,
    "FG%": 0.0,
    "2P%": 0.0,
    "3P%": 0.0,
    "FT%": 0.0,
}


def calculate_percentages(player_stats: dict) -> dict:
    for stats in player_stats.values():
        stats["FGA"] = stats["2PA"] + stats["3PA"]
        stats["FGM"] = stats["2PM"] + stats["3PM"]

        stats["2P%"] = (
            round((stats["2PM"] / stats["2PA"]) * 100, 1) if stats["2PA"] > 0 else 0.0
        )
        stats["3P%"] = (
            round((stats["3PM"] / stats["3PA"]) * 100, 1) if stats["3PA"] > 0 else 0.0
        )
        stats["FT%"] = (
            round((stats["FTM"] / stats["FTA"]) * 100, 1) if stats["FTA"] > 0 else 0.0
        )
        stats["FG%"] = (
            round((stats["FGM"] / stats["FGA"]) * 100, 1) if stats["FGA"] > 0 else 0.0
        )

    return player_stats


def process_quarter_log(metainfo: dict, quarter_log: list[dict], quarter: str) -> dict:
    home_players = metainfo["home"]["players"]
    away_players = metainfo["away"]["players"]

    home_player_stats = {player: dict(BASE_STAT) for player in home_players}
    away_player_stats = {player: dict(BASE_STAT) for player in away_players}

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
                    match = False
                    for key, value in KBL_STAT_MAP.items():
                        if key in event:
                            for stat_key in value:
                                stats[stat_key] += value[stat_key]
                            match = True
                            break
                    if not match:
                        print(
                            f"Unrecognized event: {event} - {metainfo['seasonName']}.{metainfo['gameKey']} {quarter}"
                        )

    home_player_stats = calculate_percentages(home_player_stats)
    away_player_stats = calculate_percentages(away_player_stats)

    return {"home": home_player_stats, "away": away_player_stats}


def kbl_decoder(game_path: dict) -> tuple[dict, dict]:
    with open(game_path, "r", encoding="utf-8") as file:
        game_log_data = json.load(file)

    metainfo = game_log_data["metainfo"]
    quarters = metainfo["quarters"]

    game_stats_by_quarter = {}
    for quarter in quarters:
        if quarter in game_log_data:
            quarter_log = game_log_data[quarter]
            quarter_stats = process_quarter_log(metainfo, quarter_log, quarter)
            game_stats_by_quarter[quarter] = quarter_stats

    return game_stats_by_quarter, metainfo


if __name__ == "__main__":
    all_quarter_stats, all_metainfo = kbl_decoder(
        "../kbl_data/2024-2025/S45G01N13.json"
    )
    print(json.dumps(all_quarter_stats, indent=4, ensure_ascii=False))
