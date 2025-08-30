import json
import os
import csv

def parse_quarter_data(quarter_events, home_players, away_players):
    """지정된 쿼터의 경기 기록을 분석하여 선수별 스탯을 집계합니다."""
    
    # 선수별 스탯 초기화
    stats = {player: {
        'PTS': 0, '2PM': 0, '2PA': 0, '3PM': 0, '3PA': 0, 
        'FTM': 0, 'FTA': 0, 'OREB': 0, 'DREB': 0, 'AST': 0, 
        'STL': 0, 'BLK': 0, 'TO': 0, 'PF': 0, 'GD': 0, 'DK': 0
    } for player in home_players + away_players} 

    # 이벤트 기록을 순회하며 스탯 집계
    for event in quarter_events:
        for team_key, player_list in [('home', home_players), ('away', away_players)]:
            action = event[team_key]
            if not action or action.startswith("팀"):
                continue

            for player in player_list:
                if player in action:
                    if "덩크슛성공" in action:
                        stats[player]['PTS'] += 2; stats[player]['2PM'] += 1; stats[player]['2PA'] += 1; stats[player]['DK'] += 1
                    elif "2점슛성공" in action:
                        stats[player]['PTS'] += 2; stats[player]['2PM'] += 1; stats[player]['2PA'] += 1
                    elif "2점슛시도" in action:
                        stats[player]['2PA'] += 1
                    elif "3점슛성공" in action:
                        stats[player]['PTS'] += 3; stats[player]['3PM'] += 1; stats[player]['3PA'] += 1
                    elif "3점슛시도" in action:
                        stats[player]['3PA'] += 1
                    if "자유투성공" in action:
                        stats[player]['PTS'] += 1; stats[player]['FTM'] += 1; stats[player]['FTA'] += 1
                    elif "자유투시도" in action:
                        stats[player]['FTA'] += 1
                    if "공격리바운드" in action:
                        stats[player]['OREB'] += 1
                    elif "수비리바운드" in action:
                        stats[player]['DREB'] += 1
                    elif "어시스트" in action:
                        stats[player]['AST'] += 1
                    elif "스틸" in action:
                        stats[player]['STL'] += 1
                    elif "블록" in action:
                        stats[player]['BLK'] += 1
                    elif "턴오버" in action:
                        stats[player]['TO'] += 1
                    elif "파울" in action:
                        stats[player]['PF'] += 1
                    elif "굿디펜스" in action:
                        stats[player]['GD'] += 1
                    break
    return stats

def calculate_final_stats(stats, player_list):
    """집계된 스탯을 바탕으로 성공률, 총합 등 최종 스탯을 계산합니다."""
    
    final_stats = {}
    for player in player_list:
        player_stats = stats[player]
        
        def get_percentage(made, attempted):
            return round((made / attempted) * 100, 1) if attempted > 0 else 0.0

        fgm = player_stats['2PM'] + player_stats['3PM']
        fga = player_stats['2PA'] + player_stats['3PA']

        final_stats[player] = {
            '선수명': player, 'PTS': player_stats['PTS'],
            '2PM': player_stats['2PM'], '2PA': player_stats['2PA'],
            '2P%': get_percentage(player_stats['2PM'], player_stats['2PA']),
            '3PM': player_stats['3PM'], '3PA': player_stats['3PA'],
            '3P%': get_percentage(player_stats['3PM'], player_stats['3PA']),
            'FGM': fgm, 'FGA': fga, 'FG%': get_percentage(fgm, fga),
            'FTM': player_stats['FTM'], 'FTA': player_stats['FTA'],
            'FT%': get_percentage(player_stats['FTM'], player_stats['FTA']),
            'OREB': player_stats['OREB'], 'DREB': player_stats['DREB'],
            'REB': player_stats['OREB'] + player_stats['DREB'],
            'AST': player_stats['AST'], 'STL': player_stats['STL'],
            'BLK': player_stats['BLK'], 'GD': player_stats['GD'],
            'DK': player_stats['DK'], 'TO': player_stats['TO'], 'PF': player_stats['PF']
        }
    return final_stats

# --- 메인 코드 실행 ---
def main():
    output_filename = 'kbl_cumulative_box_scores.csv'

    # --- 처리할 시리즈와 해당 폴더 경로 목록 ---
    series_directories = {
        'S39': '../kbl_data/2021-2022',
        'S41': '../kbl_data/2022-2023',
        'S43': '../kbl_data/2023-2024',
        'S45': '../kbl_data/2024-2025'
    }

    # CSV 파일 헤더 정의 (누적쿼터 열 추가)
    headers = [
        "시즌", "경기ID", "누적쿼터", "팀명", "구분", "선수명", "PTS", "2PM", "2PA", "2P%", 
        "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", 
        "OREB", "DREB", "REB", "AST", "STL", "BLK", "GD", "DK", "TO", "PF"
    ]

    # 결과를 저장할 CSV 파일을 열기
    with open(output_filename, 'w', encoding='utf-8-sig', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers) # 헤더 작성

        print(f"모든 경기 기록 분석을 시작합니다. 결과는 {output_filename} 파일에 저장됩니다.")

        # 지정된 모든 시리즈에 대해 반복
        for prefix, directory in series_directories.items():
            print(f"\n--- {prefix} 시리즈 처리 시작 (폴더: {directory}) ---")

            # N1부터 N270까지 반복
            for i in range(1, 271):
                game_id = f"{prefix}G01N{i}"
                json_filename = f"{game_id}.json"
                file_path = os.path.join(directory, json_filename)

                if not os.path.exists(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"처리 중: {json_filename}")

                    # 기본 정보 설정
                    home_players = [p.strip() for p in data['metainfo']['home']['players']]
                    away_players = [p.strip() for p in data['metainfo']['away']['players']]
                    home_team_name = data['metainfo']['home']['name']
                    away_team_name = data['metainfo']['away']['name']
                    
                    # 경기별 누적 스탯 변수 초기화
                    cumulative_raw_stats = {p: {k: 0 for k in ['PTS', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'GD', 'DK']} for p in home_players + away_players}
                    processed_quarters = []

                    # 각 쿼터별로 반복하며 스탯 누적 및 CSV 작성
                    for q in data['metainfo']['quarters']:
                        processed_quarters.append(q)
                        cumulative_quarter_label = "-".join(processed_quarters)

                        # 현재 쿼터 스탯 계산
                        quarter_raw_stats = parse_quarter_data(data[q], home_players, away_players)
                        
                        # 누적 스탯에 더하기
                        for p in home_players + away_players:
                            for stat_key in cumulative_raw_stats[p]:
                                cumulative_raw_stats[p][stat_key] += quarter_raw_stats[p][stat_key]

                        # 현재까지의 누적 스탯으로 최종 스탯 계산
                        home_cumulative_stats = calculate_final_stats(cumulative_raw_stats, home_players)
                        away_cumulative_stats = calculate_final_stats(cumulative_raw_stats, away_players)

                        # 홈팀 선수들 기록을 CSV에 쓰기
                        for player in home_players:
                            s = home_cumulative_stats[player]
                            row = [
                                directory, game_id, cumulative_quarter_label, home_team_name, 'Home', s['선수명'], s['PTS'],
                                s['2PM'], s['2PA'], s['2P%'], s['3PM'], s['3PA'], s['3P%'],
                                s['FGM'], s['FGA'], s['FG%'], s['FTM'], s['FTA'], s['FT%'],
                                s['OREB'], s['DREB'], s['REB'], s['AST'], s['STL'],
                                s['BLK'], s['GD'], s['DK'], s['TO'], s['PF']
                            ]
                            writer.writerow(row)
                        
                        # 어웨이팀 선수들 기록을 CSV에 쓰기
                        for player in away_players:
                            s = away_cumulative_stats[player]
                            row = [
                                directory, game_id, cumulative_quarter_label, away_team_name, 'Away', s['선수명'], s['PTS'],
                                s['2PM'], s['2PA'], s['2P%'], s['3PM'], s['3PA'], s['3P%'],
                                s['FGM'], s['FGA'], s['FG%'], s['FTM'], s['FTA'], s['FT%'],
                                s['OREB'], s['DREB'], s['REB'], s['AST'], s['STL'],
                                s['BLK'], s['GD'], s['DK'], s['TO'], s['PF']
                            ]
                            writer.writerow(row)

                except Exception as e:
                    print(f"오류: {json_filename} 처리 중 오류 발생: {e}. 건너뜁니다.")
        
        print(f"\n모든 시리즈의 기록 분석이 완료되었습니다. 결과를 {output_filename} 파일에서 확인하세요.")

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    


