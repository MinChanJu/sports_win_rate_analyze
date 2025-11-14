import copy, os, re
import pandas as pd
from kbl_decoder import kbl_decoder

def data_to_csv(data_path: str, csv_path: str):
    os.makedirs(csv_path, exist_ok=True)
    s = 1
    for folder in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, folder)):
            files = os.listdir(os.path.join(data_path, folder))
            files.sort(
                key=lambda x: (
                    int(re.search(r"S\d+G\d+N(\d+)\.json$", x).group(1))
                    if re.search(r"S\d+G\d+N(\d+)\.json$", x)
                    else float("inf")
                )
            )
            records = []
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(data_path, folder, file)
                    game_stats, metainfo, last_quarter = kbl_decoder(file_path, 1)
                    row = {
                        "gameKey": metainfo["gameKey"],
                        "seasonName": metainfo["seasonName"],
                        "date": metainfo["date"],
                    }
                    row["winner"] = metainfo["winner"]
                    
                    for team, team_stats in game_stats.items():
                        for stat in team_stats:
                            t = "H" if team == "home" else "A"
                            row[f"{t}_{stat}"] = team_stats[stat]
                    records.append(row)

            fill_stats = set()
            for row in records:
                for stat in row:
                    if row[stat] != 0:
                        fill_stats.add(stat)

            df = pd.DataFrame(records)
            df.to_csv(f"{csv_path}/{folder}.csv", index=False, encoding="utf-8-sig")
            print(f"{folder} 시즌")
            print(f"    필드 개수 -> {len(df.columns)}개")
            print(f"    데이터 개수 -> {len(records)}개")
            print(f"    레코드 저장 완료 -> {csv_path}/{folder}.csv")
            
    stat_list = list(records[0].keys())
    empty_stats = set(stat_list) - fill_stats
    print("전체 시즌")
    print(f"    필드 개수 (빈 필드 제외) -> {len(fill_stats)}개")
    print(f"    빈 필드 ({len(empty_stats)} 개) -> {empty_stats}")

if __name__ == "__main__":
    data_to_csv("../../../kbl_log_data", "../kbl_data_csv")
