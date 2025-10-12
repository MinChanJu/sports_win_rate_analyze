import pandas as pd

paths = [
    "../MLP/reference_study/kbl_data_quarter_csv/2021-2022.csv",
    "../MLP/reference_study/kbl_data_quarter_csv/2022-2023.csv",
    "../MLP/reference_study/kbl_data_quarter_csv/2023-2024.csv",
    "../MLP/reference_study/kbl_data_quarter_csv/2024-2025.csv",
]

merged_df = pd.concat([pd.read_csv(path) for path in paths])

def get_matchup_stats_corrected(df, team1, team2, current_season):
    
    final_games_df = df[df['quarter'] == 'Q4'].copy()
    
    # 날짜 형식 변환 및 정렬 (최근 경기 계산을 위해)
    final_games_df['date'] = pd.to_datetime(final_games_df['date'])
    final_games_df = final_games_df.sort_values(by='date')

    # --- 1. 각 팀의 이번 시즌 성적 ---
    season_df = final_games_df[final_games_df["seasonName"] == current_season]
    
    def get_team_record(team_name, games_df):
        team_games = games_df[(games_df['H_TEAM'] == team_name) | (games_df['A_TEAM'] == team_name)]
        wins = len(team_games[
            ((team_games['H_TEAM'] == team_name) & (team_games['winner'] == 'home')) |
            ((team_games['A_TEAM'] == team_name) & (team_games['winner'] == 'away'))
        ])
        losses = len(team_games) - wins
        return f"{wins}승 {losses}패"

    team1_record = get_team_record(team1, season_df)
    team2_record = get_team_record(team2, season_df)

    # --- 2. 두 팀의 이번 시즌 상대 전적 ---
    def get_head_to_head(team1_name, team2_name, games_df):
        matchup_games = games_df[
            ((games_df['H_TEAM'] == team1_name) & (games_df['A_TEAM'] == team2_name)) |
            ((games_df['H_TEAM'] == team2_name) & (games_df['A_TEAM'] == team1_name))
        ]
        if matchup_games.empty:
            return f"{team1_name} 0승 vs 0패 {team2_name}"

        team1_wins = len(matchup_games[
            ((matchup_games['H_TEAM'] == team1_name) & (matchup_games['winner'] == 'home')) |
            ((matchup_games['A_TEAM'] == team1_name) & (matchup_games['winner'] == 'away'))
        ])
        team2_wins = len(matchup_games) - team1_wins
        return f"{team1_name} {team1_wins}승 vs {team2_wins}패 {team2_name}"
    
    season_head_to_head = get_head_to_head(team1, team2, season_df)

    # --- 3. 각 팀의 최근 5경기 전적 ---
    team1_recent_record = get_team_record(team1, season_df[(season_df['H_TEAM'] == team1) | (season_df['A_TEAM'] == team1)].tail(5))
    team2_recent_record = get_team_record(team2, season_df[(season_df['H_TEAM'] == team2) | (season_df['A_TEAM'] == team2)].tail(5))
    
    # --- 4. 통산 상대 전적 (전체 시즌) ---
    all_time_head_to_head = get_head_to_head(team1, team2, final_games_df)

    # --- 결과 출력 ---
    print(f"## {team1} vs {team2} 상대 전적 비교 ##")
    print(f"분석 기준 시즌: {current_season}")
    print("-" * 40)
    print(f"1. 이번 시즌 성적")
    print(f"   - {team1}: {team1_record}")
    print(f"   - {team2}: {team2_record}\n")
    print(f"2. 최근 5경기 전적")
    print(f"   - {team1}: {team1_recent_record}")
    print(f"   - {team2}: {team2_recent_record}\n")
    print(f"3. 이번 시즌 상대 전적")
    print(f"   - {season_head_to_head}\n")
    print(f"4. 통산 상대 전적 (21-22 시즌에서 24-25 시즌까지)")
    print(f"   - {all_time_head_to_head}")
    print("-" * 40)


# --- 함수 실행 ---
get_matchup_stats_corrected(merged_df, '부산 KCC', '수원 KT', current_season="2024-2025")



# 부산 KCC 나 안양 정관장 같은 경우 가지고 있는 네 시즌의 데이터 동안 팀 이름 변경 이루어져, 이름이 바뀐 뒤의 데이터값만 환산되는 문제 수정 필요함.