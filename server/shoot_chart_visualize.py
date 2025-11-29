import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Arc, Circle, Rectangle
import pandas as pd
import platform
from matplotlib import rc
import numpy as np
import os
import glob

# 1. 한글 폰트 설정
if platform.system() == 'Windows':
    rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# [NEW] 팀 코드 자동 매핑 함수
# =============================================================================
def build_team_code_map(log_dir_path):
    """
    로그 폴더 내의 모든 JSON 파일을 스캔하여 정확한 {팀명: 팀코드} 매핑을 생성합니다.
    """
    team_map = {}
    
    # 폴더가 없으면 빈 딕셔너리 반환 (기존 하드코딩된 값 사용 유도)
    if not os.path.exists(log_dir_path):
        print(f"경고: 로그 폴더({log_dir_path})를 찾을 수 없습니다.")
        return {}

    # 모든 JSON 파일 검색
    search_pattern = os.path.join(log_dir_path, "**", "*.json")
    json_files = glob.glob(search_pattern, recursive=True)
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            meta = data.get("metainfo", {})
            
            # 홈팀 정보 추출
            h_name = meta.get("home", {}).get("name")
            h_code = str(meta.get("home", {}).get("code", "")).strip()
            
            # 원정팀 정보 추출
            a_name = meta.get("away", {}).get("name")
            a_code = str(meta.get("away", {}).get("code", "")).strip()
            
            # 유효한 값만 매핑 테이블에 업데이트
            if h_name and h_code and h_code != "None":
                team_map[h_name.replace(" ", "")] = h_code
            if a_name and a_code and a_code != "None":
                team_map[a_name.replace(" ", "")] = a_code
                
        except:
            continue
            
    print(f"-> {len(team_map)}개 팀의 코드를 확보했습니다.")
    return team_map

# =============================================================================
# 2. 풀 코트(Full Court) 그리기 함수
# =============================================================================
def draw_full_court(ax=None, color='black', lw=2):
    if ax is None:
        ax = plt.gca()

    COURT_W, COURT_H = 700, 400
    CENTER_X, CENTER_Y = COURT_W / 2, COURT_H / 2
    
    # 외곽선 & 센터 라인
    ax.add_patch(Rectangle((0, 0), COURT_W, COURT_H, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.plot([CENTER_X, CENTER_X], [0, COURT_H], color=color, linewidth=lw)
    ax.add_patch(Circle((CENTER_X, CENTER_Y), radius=60, linewidth=lw, edgecolor=color, facecolor='none'))
    
    three_pt_radius = 168
    
    # [왼쪽 골대 - Home]
    HOOP_LEFT_X = 52.5
    ax.add_patch(Circle((HOOP_LEFT_X, CENTER_Y), radius=11, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.add_patch(Rectangle((40, CENTER_Y - 30), 0, 60, linewidth=lw, edgecolor=color))
    ax.add_patch(Rectangle((0, CENTER_Y - 61), 145, 122, linewidth=lw, edgecolor=color, facecolor='none'))
    
    thetas_left = np.linspace(np.radians(-78), np.radians(78), 50)
    arc_x_left = HOOP_LEFT_X + three_pt_radius * np.cos(thetas_left)
    arc_y_left = CENTER_Y + three_pt_radius * np.sin(thetas_left)
    ax.plot(np.concatenate(([0], arc_x_left, [0])), 
            np.concatenate(([arc_y_left[0]], arc_y_left, [arc_y_left[-1]])), 
            color=color, linewidth=lw)
    
    # [오른쪽 골대 - Away]
    HOOP_RIGHT_X = COURT_W - 52.5
    ax.add_patch(Circle((HOOP_RIGHT_X, CENTER_Y), radius=11, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.add_patch(Rectangle((COURT_W - 40, CENTER_Y - 30), 0, 60, linewidth=lw, edgecolor=color))
    ax.add_patch(Rectangle((555, CENTER_Y - 61), 145, 122, linewidth=lw, edgecolor=color, facecolor='none'))
    
    thetas_right = np.linspace(np.radians(102), np.radians(258), 50)
    arc_x_right = HOOP_RIGHT_X + three_pt_radius * np.cos(thetas_right)
    arc_y_right = CENTER_Y + three_pt_radius * np.sin(thetas_right)
    ax.plot(np.concatenate(([COURT_W], arc_x_right, [COURT_W])), 
            np.concatenate(([arc_y_right[0]], arc_y_right, [arc_y_right[-1]])), 
            color=color, linewidth=lw)

    return ax

# =============================================================================
# 3. 데이터 로딩 및 전처리 (매핑 테이블 활용)
# =============================================================================
def parse_shot_data(json_file_path, team_map):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    meta = data.get('metainfo', {})
    
    # 1. 팀 이름 가져오기
    home_name_raw = meta.get('home', {}).get('name', 'Home Team')
    away_name_raw = meta.get('away', {}).get('name', 'Away Team')
    
    # 2. 팀 코드를 매핑 테이블에서 찾기 (가장 정확함)
    home_key = home_name_raw.replace(" ", "")
    away_key = away_name_raw.replace(" ", "")
    
    # 매핑 테이블에 없으면 metainfo의 코드 사용 (fallback)
    home_code = team_map.get(home_key, str(meta.get('home', {}).get('code')).strip())
    away_code = team_map.get(away_key, str(meta.get('away', {}).get('code')).strip())

    print(f"DEBUG: '{home_name_raw}' -> Code: {home_code}")
    print(f"DEBUG: '{away_name_raw}' -> Code: {away_code}")

    match_title = f"{meta.get('date', '')} {home_name_raw} vs {away_name_raw}"
    
    raw_logs = data.get('shootLog', [])
    shots = []
    COURT_W, COURT_H = 700, 400

    for player in raw_logs:
        p_tcode = str(player.get('tcode')).strip()
        p_name = player.get('pname')
        
        # 3. 팀 판별
        if p_tcode == home_code:
            target_side = "Left"
            team_label = "Home"
            is_home_team = True
        elif p_tcode == away_code:
            target_side = "Right"
            team_label = "Away"
            is_home_team = False
        else:
            # 매칭 실패 시 원정팀(오른쪽)으로 분류 (필요시 수정 가능)
            target_side = "Right"
            team_label = "Away"
            is_home_team = False

        for log in player.get('logs', []):
            x = float(log.get('x', 0))
            y = float(log.get('y', 0))
            d = str(log.get('d', '1'))
            made = log.get('o') == 'O'
            
            # 좌표 정규화
            if d == '1': # 오른쪽 코트 -> 왼쪽으로 뒤집기
                norm_x = COURT_W - x
                norm_y = COURT_H - y
            else:
                norm_x = x
                norm_y = y
            
            # 최종 배치
            if target_side == "Left":
                final_x = norm_x
                final_y = norm_y
            else: # 오른쪽 코트로 대칭 이동
                final_x = COURT_W - norm_x
                final_y = COURT_H - norm_y

            shots.append({
                'x': final_x, 
                'y': final_y, 
                'made': made, 
                'team': team_label
            })
            
    return match_title, home_name_raw, away_name_raw, pd.DataFrame(shots)

# =============================================================================
# 4. 시각화 실행
# =============================================================================
def visualize_shot_chart(json_path, team_map):
    title, home_name, away_name, df = parse_shot_data(json_path, team_map)
    
    if df.empty:
        print("데이터가 없습니다.")
        return

    # 비율 조정 
    fig, ax = plt.subplots(figsize=(15, 10))
    
    draw_full_court(ax, color='black')
    
    home_df = df[df['team'] == 'Home']
    away_df = df[df['team'] == 'Away']
    
    # 홈팀 (왼쪽) - 파랑/빨강
    ax.scatter(home_df[home_df['made']]['x'], home_df[home_df['made']]['y'], 
               facecolors='none', edgecolors='blue', marker='o', s=60, lw=1.5, label='성공', zorder=5)
    ax.scatter(home_df[~home_df['made']]['x'], home_df[~home_df['made']]['y'], 
               c='red', marker='x', s=60, label='실패', zorder=5)

    # 원정팀 (오른쪽) - 파랑/빨강 (동일 색상 사용)
    ax.scatter(away_df[away_df['made']]['x'], away_df[away_df['made']]['y'], 
               facecolors='none', edgecolors='blue', marker='o', s=60, lw=1.5, zorder=5)
    ax.scatter(away_df[~away_df['made']]['x'], away_df[~away_df['made']]['y'], 
               c='red', marker='x', s=60, zorder=5)

    # 텍스트
    ax.text(175, 430, f"HOME\n{home_name}", fontsize=14, fontweight='bold', ha='center', va='bottom', color='#333333')
    ax.text(525, 430, f"AWAY\n{away_name}", fontsize=14, fontweight='bold', ha='center', va='bottom', color='#333333')

    ax.set_xlim(0, 700)
    ax.set_ylim(-20, 450)
    ax.axis('off')
    
    plt.title(f"KBL Shot Chart: {title}", fontsize=16, fontweight='bold', pad=40)
    plt.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 1. 슛 차트 파일 경로
    target_json_file = "../kbl_chart_data/2025-2026/S47G01N48.json"
    
    # 2. 로그 데이터가 모여있는 폴더 경로 (매핑용)
    log_data_dir = "../kbl_log_data"
    
    if os.path.exists(target_json_file):
        print("팀 코드를 스캔 중입니다...")
        # (1) 팀 코드 맵 생성
        team_mapping = build_team_code_map(log_data_dir)
        
        # (2) 생성된 맵을 전달하여 시각화
        visualize_shot_chart(target_json_file, team_mapping)
    else:
        print(f"파일을 찾을 수 없습니다: {target_json_file}")