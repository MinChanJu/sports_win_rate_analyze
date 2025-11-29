import os
import json
import shutil
import pandas as pd
from tqdm import tqdm
from kbl_decoder import kbl_log_decoder

def data_to_csv(game_path: str, records: list):
    with open(game_path, "r", encoding="utf-8") as f:
        game_data = json.load(f)
    
    metainfo = game_data["metainfo"]
    h_code = metainfo["home"]["code"]
    a_code = metainfo["away"]["code"]
    all_logs = game_data["logs"]
    
    game_stats = kbl_log_decoder(all_logs, h_code, a_code)
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

def data_to_csv_multiple(data_path: str, csv_folder: str):
    if os.path.exists(csv_folder):
        shutil.rmtree(csv_folder)
        
    os.makedirs(csv_folder)
    for season_folder in sorted(os.listdir(data_path)):
        season_path = os.path.join(data_path, season_folder)
        if not os.path.isdir(season_path):
            continue
        records = []
        for file in tqdm(sorted(os.listdir(season_path)), desc=f"Processing {season_folder}"):
            if file.endswith(".json"):
                game_path = os.path.join(season_path, file)
                csv_path = os.path.join(csv_folder, season_folder)
                os.makedirs(csv_path, exist_ok=True)
                csv_path = os.path.join(csv_path, file.replace(".json", ".csv"))
                data_to_csv(game_path, records)
        
        csv_path = os.path.join(csv_folder, f"{season_folder}.csv")
        df = pd.DataFrame(records)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    data_to_csv_multiple("../../../kbl_log_data", "../kbl_data_csv")
