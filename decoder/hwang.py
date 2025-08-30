import json
import os
import csv

def parse_quarter_data(quarter_events, home_players, away_players):
    """지정된 쿼터의 경기 기록을 분석하여 선수별 스탯을 집계합니다."""
    
    stats = {player: { 'PTS': 0, '2PM': 0, '2PA': 0, '3PM': 0, '3PA': 0, 'FTM': 0, 'FTA': 0, 'OREB': 0, 'DREB': 0, 'AST': 0, 'STL': 0, 'BLK': 0, 'TO': 0, 'PF': 0, 'GD': 0, 'DK': 0 } for player in home_players + away_players}
    for event in quarter_events:
        for team_key, player_list in [('home', home_players), ('away', away_players)]:
            action = event[team_key]
            if not action or action.startswith("팀"): continue
            for player in player_list:
                if player in action:
                    if "덩크슛성공" in action: stats[player]['PTS'] += 2; stats[player]['2PM'] += 1; stats[player]['2PA'] += 1; stats[player]['DK'] += 1
                    elif "2점슛성공" in action: stats[player]['PTS'] += 2; stats[player]['2PM'] += 1; stats[player]['2PA'] += 1
                    elif "2점슛시도" in action: stats[player]['2PA'] += 1
                    elif "3점슛성공" in action: stats[player]['PTS'] += 3; stats[player]['3PM'] += 1; stats[player]['3PA'] += 1
                    elif "3점슛시도" in action: stats[player]['3PA'] += 1
                    if "자유투성공" in action: stats[player]['PTS'] += 1; stats[player]['FTM'] += 1; stats[player]['FTA'] += 1
                    elif "자유투시도" in action: stats[player]['FTA'] += 1
                    if "공격리바운드" in action: stats[player]['OREB'] += 1
                    elif "수비리바운드" in action: stats[player]['DREB'] += 1
                    elif "어시스트" in action: stats[player]['AST'] += 1
                    elif "스틸" in action: stats[player]['STL'] += 1
                    elif "블록" in action: stats[player]['BLK'] += 1
                    elif "턴오버" in action: stats[player]['TO'] += 1
                    elif "파울" in action: stats[player]['PF'] += 1
                    elif "굿디펜스" in action: stats[player]['GD'] += 1
                    break
    return stats

def calculate_final_stats(stats, player_list):
    """집계된 스탯을 바탕으로 성공률, 총합 등 최종 스탯을 계산합니다."""
    final_stats = {}
    for player in player_list:
        player_stats = stats[player]
        def get_percentage(made, attempted): return round((made / attempted) * 100, 1) if attempted > 0 else 0.0
        fgm = player_stats['2PM'] + player_stats['3PM']; fga = player_stats['2PA'] + player_stats['3PA']
        final_stats[player] = {
            '선수명': player, 'PTS': player_stats['PTS'], '2PM': player_stats['2PM'], '2PA': player_stats['2PA'], '2P%': get_percentage(player_stats['2PM'], player_stats['2PA']),
            '3PM': player_stats['3PM'], '3PA': player_stats['3PA'], '3P%': get_percentage(player_stats['3PM'], player_stats['3PA']),
            'FGM': fgm, 'FGA': fga, 'FG%': get_percentage(fgm, fga), 'FTM': player_stats['FTM'], 'FTA': player_stats['FTA'], 'FT%': get_percentage(player_stats['FTM'], player_stats['FTA']),
            'OREB': player_stats['OREB'], 'DREB': player_stats['DREB'], 'REB': player_stats['OREB'] + player_stats['DREB'],
            'AST': player_stats['AST'], 'STL': player_stats['STL'], 'BLK': player_stats['BLK'], 'GD': player_stats['GD'], 'DK': player_stats['DK'], 'TO': player_stats['TO'], 'PF': player_stats['PF']
        }
    return final_stats

def main():
    output_filename = 'kbl_cumulative_box_scores_with_winner_corrected.csv'
    series_directories = {
        'S39': '../kbl_data/2021-2022', 'S41': '../kbl_data/2022-2023',
        'S43': '../kbl_data/2023-2024', 'S45': '../kbl_data/2024-2025'
    }

    headers = [
        "시즌", "경기ID", "누적쿼터", "팀명", "구분", "선수명", "최종승리팀(1=홈승)",
        "PTS", "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", 
        "OREB", "DREB", "REB", "AST", "STL", "BLK", "GD", "DK", "TO", "PF"
    ]

    with open(output_filename, 'w', encoding='utf-8-sig', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers)

        print(f"정확한 승리팀 정보가 포함된 CSV 파일 생성을 시작합니다: {output_filename}")

        for prefix, directory in series_directories.items():
            print(f"\n--- {prefix} 시리즈 처리 시작 ---")
            for i in range(1, 271):
                game_id = f"{prefix}G01N{i}"; file_path = os.path.join(directory, f"{game_id}.json")
                if not os.path.exists(file_path): continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
                    print(f"처리 중: {game_id}")

                    home_players = [p.strip() for p in data['metainfo']['home']['players']]; away_players = [p.strip() for p in data['metainfo']['away']['players']]
                    home_team_name = data['metainfo']['home']['name']; away_team_name = data['metainfo']['away']['name']
                    
                    # --- *** 승리팀 계산 로직 수정 *** ---
                    # 1. 먼저 경기 전체의 최종 스탯을 계산
                    full_game_stats_raw = {p: {k: 0 for k in ['PTS', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'GD', 'DK']} for p in home_players + away_players}
                    for q in data['metainfo']['quarters']:
                        quarter_raw_stats = parse_quarter_data(data[q], home_players, away_players)
                        for p in home_players + away_players:
                            for stat_key in full_game_stats_raw[p]: full_game_stats_raw[p][stat_key] += quarter_raw_stats[p][stat_key]
                    
                    # 2. 최종 스코어 합산
                    home_total_pts = sum(full_game_stats_raw[player]['PTS'] for player in home_players)
                    away_total_pts = sum(full_game_stats_raw[player]['PTS'] for player in away_players)

                    # 3. 최종 승리팀 결정 (1: 홈팀 승, 0: 어웨이팀 승)
                    winner_info = 1 if home_total_pts > away_total_pts else 0
                    
                    # --- 쿼터별 누적 데이터 기록 (계산된 winner_info 사용) ---
                    cumulative_raw_stats = {p: {k: 0 for k in ['PTS', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'GD', 'DK']} for p in home_players + away_players}
                    processed_quarters = []
                    
                    for q in data['metainfo']['quarters']:
                        processed_quarters.append(q); cumulative_quarter_label = "-".join(processed_quarters)
                        quarter_raw_stats = parse_quarter_data(data[q], home_players, away_players)
                        for p in home_players + away_players:
                            for stat_key in cumulative_raw_stats[p]: cumulative_raw_stats[p][stat_key] += quarter_raw_stats[p][stat_key]
                        
                        home_cumulative_stats = calculate_final_stats(cumulative_raw_stats, home_players)
                        away_cumulative_stats = calculate_final_stats(cumulative_raw_stats, away_players)

                        # 홈팀 선수 기록 쓰기
                        for player in home_players:
                            s = home_cumulative_stats[player]
                            row_data = list(s.values())
                            row = [directory, game_id, cumulative_quarter_label, home_team_name, 'Home', s['선수명'], winner_info] + row_data[1:]
                            writer.writerow(row)
                        
                        # 어웨이팀 선수 기록 쓰기
                        for player in away_players:
                            s = away_cumulative_stats[player]
                            row_data = list(s.values())
                            row = [directory, game_id, cumulative_quarter_label, away_team_name, 'Away', s['선수명'], winner_info] + row_data[1:]
                            writer.writerow(row)

                except Exception as e: print(f"오류: {game_id} 처리 중 오류 발생: {e}")
        print(f"\n완료! {output_filename} 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
    
    

import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import warnings

warnings.filterwarnings('ignore')

# 1. 데이터 불러오기
file_path = 'kbl_cumulative_box_scores_with_winner_corrected.csv'
df = pd.read_csv(file_path)

# 2. 팀별 스탯으로 데이터 가공 (기존 방식)
stat_columns = ['PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF']
team_stats_pivot = df.pivot_table(
    index=['경기ID', '누적쿼터', '최종승리팀(1=홈승)'],
    columns='구분', values=stat_columns, aggfunc='sum'
)
team_stats_pivot.columns = [f'{stat}_{team}' for stat, team in team_stats_pivot.columns]
team_stats_pivot.reset_index(inplace=True)


# 3. ★★★ 개인별 영향을 고려한 신규 특성 생성 ★★★
print("개인별 영향을 고려한 신규 특성(최다 득점, 득점 표준편차)을 생성합니다...")

# 경기-쿼터별, 팀별로 그룹화하여 개인 스탯 요약
individual_features = df.groupby(['경기ID', '누적쿼터', '구분']).agg(
    Max_PTS=('PTS', 'max'),       # 최다 득점
    PTS_StdDev=('PTS', 'std')    # 득점 표준편차
).reset_index()

# 결측치(선수가 1명일 경우 std가 NaN)를 0으로 채움
individual_features.fillna(0, inplace=True)

# Home/Away로 분리하기 위해 pivot 사용
individual_pivot = individual_features.pivot_table(
    index=['경기ID', '누적쿼터'],
    columns='구분',
    values=['Max_PTS', 'PTS_StdDev']
)
individual_pivot.columns = [f'{stat}_{team}' for stat, team in individual_pivot.columns]
individual_pivot.reset_index(inplace=True)

# 4. 기존 팀 스탯 데이터와 신규 개인 요약 스탯 데이터 병합
team_stats = pd.merge(team_stats_pivot, individual_pivot, on=['경기ID', '누적쿼터'])

# 5. 특성 공학 (Feature Engineering)
print("종합적인 특성 공학을 적용합니다...")
# 5-1. 기존 스탯 차이
for stat in stat_columns:
    if '%' not in stat:
        team_stats[f'{stat}_Diff'] = team_stats[f'{stat}_Home'] - team_stats[f'{stat}_Away']

# 5-2. 신규 개인 요약 스탯 차이
team_stats['Max_PTS_Diff'] = team_stats['Max_PTS_Home'] - team_stats['Max_PTS_Away']
team_stats['PTS_StdDev_Diff'] = team_stats['PTS_StdDev_Home'] - team_stats['PTS_StdDev_Away']
        
# 5-3. eFG% 특성
team_stats['eFG%_Home'] = (team_stats['FGM_Home'] + 0.5 * team_stats['3PM_Home']) / team_stats['FGA_Home']
team_stats['eFG%_Away'] = (team_stats['FGM_Away'] + 0.5 * team_stats['3PM_Away']) / team_stats['FGA_Away']
team_stats['eFG%_Diff'] = team_stats['eFG%_Home'] - team_stats['eFG%_Away']

# 5-4. '쿼터' 정보 특성화
team_stats['Quarter_Num'] = team_stats['누적쿼터'].str.count('-') + 1
quarter_dummies = pd.get_dummies(team_stats['누적쿼터'], prefix='Quarter')
team_stats = pd.concat([team_stats, quarter_dummies], axis=1)

team_stats.fillna(0, inplace=True)
team_stats.replace([float('inf'), -float('inf')], 0, inplace=True)

# 6. 시즌 기반 데이터 분리
print("시즌 기반으로 학습/테스트 데이터를 분리합니다.")
team_stats['시즌ID'] = team_stats['경기ID'].str.slice(0, 3)
train_df = team_stats[team_stats['시즌ID'].isin(['S39', 'S41', 'S43'])]
test_df = team_stats[team_stats['시즌ID'].isin(['S45'])]

X_train = train_df.drop(columns=['경기ID', '누적쿼터', '최종승리팀(1=홈승)', '시즌ID'])
y_train = train_df['최종승리팀(1=홈승)']
X_test = test_df.drop(columns=['경기ID', '누적쿼터', '최종승리팀(1=홈승)', '시즌ID'])
y_test = test_df['최종승리팀(1=홈승)']

# 7. 데이터 불균형 처리 및 모델 학습
scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
print(f"\nscale_pos_weight 값: {scale_pos_weight:.2f}")

print("하이퍼파라미터 튜닝을 시작합니다...")
param_grid = {
    'n_estimators': [200, 300, 400], 'max_depth': [4, 5, 6],
    'learning_rate': [0.01, 0.05, 0.1], 'subsample': [0.8, 0.9],
    'colsample_bytree': [0.8, 0.9]
}
xgb = XGBClassifier(
    objective='binary:logistic', eval_metric='logloss',
    use_label_encoder=False, scale_pos_weight=scale_pos_weight, random_state=42
)
random_search = RandomizedSearchCV(
    estimator=xgb, param_distributions=param_grid, n_iter=50,
    cv=3, scoring='accuracy', verbose=1, random_state=42, n_jobs=-1
)
random_search.fit(X_train, y_train)

# 8. 최종 평가
print(f"\n최적 하이퍼파라미터: {random_search.best_params_}")
best_model = random_search.best_estimator_
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n개인별 영향력을 고려한 모델의 최종 테스트 정확도: {accuracy * 100:.2f}%")
print("\n최종 평가 리포트:")
print(classification_report(y_test, y_pred, target_names=['Away Win', 'Home Win']))