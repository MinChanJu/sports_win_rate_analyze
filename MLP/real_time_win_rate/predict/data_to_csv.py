import json
import pandas as pd
from kbl_decoder import kbl_log_decoder

def data_to_csv(game_path: str, csv_path: str):
    with open(game_path, "r", encoding="utf-8") as f:
        game_data = json.load(f)
    
    metainfo = game_data["metainfo"]
    h_code = metainfo["home"]["code"]
    a_code = metainfo["away"]["code"]
    all_logs = game_data["logs"]
    
    records = []
    for idx in range(len(all_logs)):
        sub_logs = all_logs[:idx+1]
        game_stats = kbl_log_decoder(sub_logs, h_code, a_code)
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
    
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

def data_to_csv_multiple(data_path: str, csv_folder: str):
    import os
    from tqdm import tqdm
    os.makedirs(csv_folder, exist_ok=False)
    for season_folder in sorted(os.listdir(data_path)):
        season_path = os.path.join(data_path, season_folder)
        if not os.path.isdir(season_path):
            continue
        for file in tqdm(sorted(os.listdir(season_path)), desc=f"Processing {season_folder}"):
            if file.endswith(".json"):
                game_path = os.path.join(season_path, file)
                csv_path = os.path.join(csv_folder, season_folder)
                os.makedirs(csv_path, exist_ok=True)
                csv_path = os.path.join(csv_path, file.replace(".json", ".csv"))
                data_to_csv(game_path, csv_path)

if __name__ == "__main__":
    data_to_csv_multiple("../../../kbl_log_data", "../kbl_real_time_csv")
