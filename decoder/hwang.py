import json

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
            if not action:
                continue

            # 팀 기록은 건너뛰기
            if action.startswith("팀"):
                continue

            for player in player_list:
                if player in action:
                    # 득점 및 슛 시도
                    if "덩크슛성공" in action:
                        stats[player]['PTS'] += 2
                        stats[player]['2PM'] += 1
                        stats[player]['2PA'] += 1
                        stats[player]['DK'] += 1
                    elif "2점슛성공" in action:
                        stats[player]['PTS'] += 2
                        stats[player]['2PM'] += 1
                        stats[player]['2PA'] += 1
                    elif "2점슛시도" in action:
                        stats[player]['2PA'] += 1
                    elif "3점슛성공" in action:
                        stats[player]['PTS'] += 3
                        stats[player]['3PM'] += 1
                        stats[player]['3PA'] += 1
                    elif "3점슛시도" in action:
                        stats[player]['3PA'] += 1
                    
                    # 자유투
                    if "자유투성공" in action:
                        stats[player]['PTS'] += 1
                        stats[player]['FTM'] += 1
                        stats[player]['FTA'] += 1
                    elif "자유투시도" in action:
                        stats[player]['FTA'] += 1
                    
                    # 기타 기록
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
                    elif "파울" in action: # '파울'과 '파울자유투' 모두 포함
                        stats[player]['PF'] += 1
                    elif "굿디펜스" in action:
                        stats[player]['GD'] += 1
                    
                    break # 해당 이벤트에서 선수 식별 완료
    return stats

def calculate_final_stats(stats, player_list):
    """집계된 스탯을 바탕으로 성공률, 총합 등 최종 스탯을 계산합니다."""
    
    final_stats = {}
    for player in player_list:
        player_stats = stats[player]
        
        # 성공률 계산 함수
        def get_percentage(made, attempted):
            return round((made / attempted) * 100, 1) if attempted > 0 else 0.0

        fgm = player_stats['2PM'] + player_stats['3PM']
        fga = player_stats['2PA'] + player_stats['3PA']

        final_stats[player] = {
            '선수명': player,
            'PTS': player_stats['PTS'],
            '2PM': player_stats['2PM'],
            '2PA': player_stats['2PA'],
            '2P%': get_percentage(player_stats['2PM'], player_stats['2PA']),
            '3PM': player_stats['3PM'],
            '3PA': player_stats['3PA'],
            '3P%': get_percentage(player_stats['3PM'], player_stats['3PA']),
            'FGM': fgm,
            'FGA': fga,
            'FG%': get_percentage(fgm, fga),
            'FTM': player_stats['FTM'],
            'FTA': player_stats['FTA'],
            'FT%': get_percentage(player_stats['FTM'], player_stats['FTA']),
            'OREB': player_stats['OREB'],
            'DREB': player_stats['DREB'],
            'REB': player_stats['OREB'] + player_stats['DREB'],
            'AST': player_stats['AST'],
            'STL': player_stats['STL'],
            'BLK': player_stats['BLK'],
            'GD': player_stats['GD'],
            'DK': player_stats['DK'],
            'TO': player_stats['TO'],
            'PF': player_stats['PF']
        }
    return final_stats

def print_box_score(team_name, final_stats, player_list):
    """선수별 최종 스탯을 표 형태로 출력합니다."""
    print(f"\n[ {team_name} ]")
    
    # 헤더 출력
    headers = [
        "선수명", "PTS", "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", 
        "FTM", "FTA", "FT%", "OREB", "DREB", "REB", "AST", "STL", "BLK", "GD", "DK", "TO", "PF"
    ]
    header_str = (
        f"{headers[0]:<12}" + "".join([f"{h:<6}" for h in headers[1:14]]) +
        "".join([f"{h:<5}" for h in headers[14:]])
    )
    print(header_str)
    print("-" * len(header_str))

    # 선수 기록 출력
    for player in player_list:
        s = final_stats[player]
        print(
            f"{s['선수명']:<12}"
            f"{s['PTS']:<6}{s['2PM']:<6}{s['2PA']:<6}{s['2P%']:<6.1f}"
            f"{s['3PM']:<6}{s['3PA']:<6}{s['3P%']:<6.1f}"
            f"{s['FGM']:<6}{s['FGA']:<6}{s['FG%']:<6.1f}"
            f"{s['FTM']:<6}{s['FTA']:<6}{s['FT%']:<6.1f}"
            f"{s['OREB']:<5}{s['DREB']:<5}{s['REB']:<5}"
            f"{s['AST']:<5}{s['STL']:<5}{s['BLK']:<5}"
            f"{s['GD']:<5}{s['DK']:<5}{s['TO']:<5}{s['PF']:<5}"
        )

# --- 메인 코드 실행 ---
try:
    with open('kbl_quarters_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 데이터 정제 및 기본 정보 설정
    home_players_raw = data['metainfo']['home']['players']
    home_players = []
    for p in home_players_raw:
        cleaned_players = p.strip().split('\n')
        home_players.extend(player.strip('"') for player in cleaned_players if player)
        
    away_players = data['metainfo']['away']['players']
    home_team_name = data['metainfo']['home']['name']
    away_team_name = data['metainfo']['away']['name']
    quarters = data['metainfo']['quarters']

    # *** 누적 스탯을 저장할 변수 초기화 ***
    cumulative_raw_stats = {player: {
        'PTS': 0, '2PM': 0, '2PA': 0, '3PM': 0, '3PA': 0, 
        'FTM': 0, 'FTA': 0, 'OREB': 0, 'DREB': 0, 'AST': 0, 
        'STL': 0, 'BLK': 0, 'TO': 0, 'PF': 0, 'GD': 0, 'DK': 0
    } for player in home_players + away_players}
    
    processed_quarters = [] # 누적 쿼터 이름을 저장할 리스트

    # 각 쿼터별로 반복
    for q in quarters:
        processed_quarters.append(q)
        quarter_events = data[q]
        
        # 1. 해당 쿼터의 개별 기록 계산 및 출력
        print(f"\n==================== {q} BOX SCORE ====================")
        quarter_raw_stats = parse_quarter_data(quarter_events, home_players, away_players)
        
        home_quarter_final_stats = calculate_final_stats(quarter_raw_stats, home_players)
        away_quarter_final_stats = calculate_final_stats(quarter_raw_stats, away_players)
        
        print_box_score(home_team_name, home_quarter_final_stats, home_players)
        print_box_score(away_team_name, away_quarter_final_stats, away_players)

        # 2. 누적 기록 계산 및 출력
        # 현재 쿼터 기록을 누적 기록에 더하기
        for player in home_players + away_players:
            for stat_key in cumulative_raw_stats[player]:
                cumulative_raw_stats[player][stat_key] += quarter_raw_stats[player][stat_key]

        # 누적 기록을 바탕으로 최종 스탯(성공률 등) 다시 계산
        home_cumulative_final_stats = calculate_final_stats(cumulative_raw_stats, home_players)
        away_cumulative_final_stats = calculate_final_stats(cumulative_raw_stats, away_players)

        # 누적 기록 테이블 출력
        cumulative_title_str = "-".join(processed_quarters)
        print(f"\n---------- {cumulative_title_str} 누적 BOX SCORE ----------")
        print_box_score(f"{home_team_name} ({cumulative_title_str} 누적)", home_cumulative_final_stats, home_players)
        print_box_score(f"{away_team_name} ({cumulative_title_str} 누적)", away_cumulative_final_stats, away_players)


except FileNotFoundError:
    print("kbl_quarters_data.json 파일을 찾을 수 없습니다. 파이썬 스크립트와 같은 폴더에 있는지 확인해주세요.")
except json.JSONDecodeError:
    print("kbl_quarters_data.json 파일의 형식이 올바르지 않습니다. 파일 내용을 확인해주세요.")
except Exception as e:
    print(f"알 수 없는 오류가 발생했습니다: {e}")