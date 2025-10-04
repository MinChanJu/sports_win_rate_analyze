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
                    total_stats, metainfo = kbl_decoder(file_path)
                    row = {
                        "gameKey": metainfo["gameKey"],
                        "seasonName": metainfo["seasonName"],
                        "date": metainfo["date"],
                        "home_name": metainfo["home"]["name"],
                        "away_name": metainfo["away"]["name"],
                    }

                    for quarter in total_stats:
                        quarter_row = copy.deepcopy(row)
                        quarter_row["quarter"] = quarter
                        for team in total_stats[quarter]:
                            for player_idx, player in enumerate(
                                total_stats[quarter][team]
                            ):
                                quarter_row[f"{team}_player_{player_idx+1}_name"] = (
                                    player
                                )
                                for stat in total_stats[quarter][team][player]:
                                    quarter_row[
                                        f"{team}_player_{player_idx+1}_{stat}"
                                    ] = total_stats[quarter][team][player][stat]
                        records.append(quarter_row)

            df = pd.DataFrame(records)
            df.to_csv(f"{csv_path}/{folder}.csv", index=False, encoding="utf-8-sig")
            print(f"{folder} 시즌")
            print(f"    필드 개수 -> {len(df.columns)}개")
            print(f"    데이터 개수 -> {len(records)}개")
            print(f"    레코드 저장 완료 -> {csv_path}/{folder}.csv")


if __name__ == "__main__":
    data_to_csv("../kbl_data", "../kbl_data_csv")
