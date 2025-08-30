import copy, json, os, re
import pandas as pd

def decoder(file_path):
  stats = ['PTS', '2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'GD', 'DK', 'TO', 'PF']
  total_stats = {}

  with open(file_path, 'r') as f:
    data = json.load(f)
    metainfo = data['metainfo']
    home_players = metainfo['home']['players']
    away_players = metainfo['away']['players']
    quarters = metainfo['quarters']
    for quarter in quarters:
      total_stats[quarter] = {"home": {}, "away": {}}
      for player in home_players:
        total_stats[quarter]["home"][player] = {stat: 0 for stat in stats}
      for player in away_players:
        total_stats[quarter]["away"][player] = {stat: 0 for stat in stats}

  return total_stats, metainfo

def data_to_csv(data_path, csv_path):
  os.makedirs(csv_path, exist_ok=True)
  
  for folder in os.listdir(data_path):
    if os.path.isdir(os.path.join(data_path, folder)):
      files = os.listdir(os.path.join(data_path, folder))
      files.sort(key=lambda x: (int(re.search(r'S\d+G\d+N(\d+)\.json$', x).group(1)) if re.search(r'S\d+G\d+N(\d+)\.json$', x) else float('inf')))
      records = []
      for file in files:
        if file.endswith('.json'):
          file_path = os.path.join(data_path, folder, file)
          total_stats, metainfo = decoder(file_path)
          row = {
              "gameKey": metainfo['gameKey'],
              "seasonName": metainfo['seasonName'],
              "date": metainfo['date'],
              "home_name": metainfo['home']['name'],
              "away_name": metainfo['away']['name'],
          }

          for quarter in total_stats:
            quarter_row = copy.deepcopy(row)
            quarter_row["quarter"] = quarter
            for team in total_stats[quarter]:
              for player_idx, player in enumerate(total_stats[quarter][team]):
                quarter_row[f'{team}_player_{player_idx+1}_name'] = player
                for stat in total_stats[quarter][team][player]:
                  quarter_row[f'{team}_player_{player_idx+1}_{stat}'] = total_stats[quarter][team][player][stat]
            records.append(quarter_row)
              
      df = pd.DataFrame(records)
      df.to_csv(f"{csv_path}/{folder}.csv", index=False, encoding="utf-8-sig")
      print(f"{folder} 시즌")
      print(f"    필드 개수 -> {len(df.columns)}개")
      print(f"    데이터 개수 -> {len(records)}개")
      print(f"    레코드 저장 완료 -> {csv_path}/{folder}.csv")

if __name__ == "__main__":
  data_to_csv('../kbl_data', '../kbl_data_csv')