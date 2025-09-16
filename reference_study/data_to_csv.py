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
                    game_stats, metainfo = kbl_decoder(file_path)
                    row = {
                        "gameKey": metainfo["gameKey"],
                        "seasonName": metainfo["seasonName"],
                        "date": metainfo["date"],
                    }

                    for team in game_stats:
                        team_row = copy.deepcopy(row)
                        for stat in game_stats[team]:
                            team_row[f"{stat}"] = game_stats[team][stat]
                        records.append(team_row)

            df = pd.DataFrame(records)
            df.to_csv(f"{csv_path}/{folder}.csv", index=False, encoding="utf-8-sig")
            print(f"{folder} 시즌")
            print(f"    필드 개수 -> {len(df.columns)}개")
            print(f"    데이터 개수 -> {len(records)}개")
            print(f"    레코드 저장 완료 -> {csv_path}/{folder}.csv")


if __name__ == "__main__":
    data_to_csv("../kbl_data", "./kbl_data_csv")
