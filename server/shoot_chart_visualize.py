import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Arc, Circle, Rectangle
from matplotlib.widgets import CheckButtons
import pandas as pd
import platform
from matplotlib import rc
import numpy as np
import os

# 1. 한글 폰트 설정
if platform.system() == 'Windows':
    rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 2. 풀 코트 그리기
# =============================================================================
def draw_full_court(ax=None, color='black', lw=2):
    if ax is None: ax = plt.gca()
    COURT_W, COURT_H = 700, 400
    CENTER_X, CENTER_Y = COURT_W / 2, COURT_H / 2
    
    ax.add_patch(Rectangle((0, 0), COURT_W, COURT_H, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.plot([CENTER_X, CENTER_X], [0, COURT_H], color=color, linewidth=lw)
    ax.add_patch(Circle((CENTER_X, CENTER_Y), radius=60, linewidth=lw, edgecolor=color, facecolor='none'))
    
    three_pt_radius = 168
    
    # Left (Home)
    HOOP_LEFT_X = 52.5
    ax.add_patch(Circle((HOOP_LEFT_X, CENTER_Y), radius=11, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.add_patch(Rectangle((40, CENTER_Y - 30), 0, 60, linewidth=lw, edgecolor=color))
    ax.add_patch(Rectangle((0, CENTER_Y - 61), 145, 122, linewidth=lw, edgecolor=color, facecolor='none'))
    
    thetas_left = np.linspace(np.radians(-78), np.radians(78), 50)
    arc_x_left = HOOP_LEFT_X + three_pt_radius * np.cos(thetas_left)
    arc_y_left = CENTER_Y + three_pt_radius * np.sin(thetas_left)
    ax.plot(np.concatenate(([0], arc_x_left, [0])), np.concatenate(([arc_y_left[0]], arc_y_left, [arc_y_left[-1]])), color=color, linewidth=lw)
    
    # Right (Away)
    HOOP_RIGHT_X = COURT_W - 52.5
    ax.add_patch(Circle((HOOP_RIGHT_X, CENTER_Y), radius=11, linewidth=lw, edgecolor=color, facecolor='none'))
    ax.add_patch(Rectangle((COURT_W - 40, CENTER_Y - 30), 0, 60, linewidth=lw, edgecolor=color))
    ax.add_patch(Rectangle((555, CENTER_Y - 61), 145, 122, linewidth=lw, edgecolor=color, facecolor='none'))
    
    thetas_right = np.linspace(np.radians(102), np.radians(258), 50)
    arc_x_right = HOOP_RIGHT_X + three_pt_radius * np.cos(thetas_right)
    arc_y_right = CENTER_Y + three_pt_radius * np.sin(thetas_right)
    ax.plot(np.concatenate(([COURT_W], arc_x_right, [COURT_W])), np.concatenate(([arc_y_right[0]], arc_y_right, [arc_y_right[-1]])), color=color, linewidth=lw)
    return ax

# =============================================================================
# 3. 데이터 로딩
# =============================================================================
def parse_shot_data(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    meta = data.get('metainfo', {})
    home_name = meta.get('home', {}).get('name', 'Home')
    home_code = str(meta.get('home', {}).get('code', '')).strip()
    away_name = meta.get('away', {}).get('name', 'Away')
    away_code = str(meta.get('away', {}).get('code', '')).strip()
    
    match_title = f"{meta.get('date', '')} {home_name} vs {away_name}"
    raw_logs = data.get('shootLog', [])
    shots = []
    COURT_W, COURT_H = 700, 400

    for player in raw_logs:
        p_tcode = str(player.get('tcode')).strip()
        
        if p_tcode == home_code: target_side, team_label = "Left", "Home"
        elif p_tcode == away_code: target_side, team_label = "Right", "Away"
        else: target_side, team_label = "Right", "Away"

        for log in player.get('logs', []):
            x, y = float(log.get('x', 0)), float(log.get('y', 0))
            d = str(log.get('d', '1'))
            made = log.get('o') == 'O'
            q = log.get('q')
            
            if d == '1': norm_x = COURT_W - x; norm_y = COURT_H - y
            else: norm_x = x; norm_y = y
            
            if target_side == "Left": final_x, final_y = norm_x, norm_y
            else: final_x, final_y = COURT_W - norm_x, COURT_H - norm_y

            shots.append({'x': final_x, 'y': final_y, 'made': made, 'team': team_label, 'quarter': q})
            
    return match_title, home_name, away_name, pd.DataFrame(shots)

# =============================================================================
# 4. 시각화 실행
# =============================================================================
def visualize_shot_chart(json_path):
    title, home_name, away_name, df = parse_shot_data(json_path)
    if df.empty:
        print("데이터가 없습니다.")
        return

    # 1. 캔버스 설정
    fig, ax = plt.subplots(figsize=(16, 10)) 
    plt.subplots_adjust(left=0.25, bottom=0.1) 

    draw_full_court(ax, color='black')
    
    # 2. 산점도 객체 저장소
    scatter_dict = {}
    teams = ['Home', 'Away']
    quarters = ['Q1', 'Q2', 'Q3', 'Q4'] 
    results = [True, False] 
    
    for team in teams:
        for q in quarters:
            for made in results:
                subset = df[(df['team'] == team) & (df['quarter'] == q) & (df['made'] == made)]
                if made: 
                    plot = ax.scatter(subset['x'], subset['y'], 
                                      facecolors='none', edgecolors='blue', marker='o', s=60, lw=1.5, zorder=5)
                else: 
                    plot = ax.scatter(subset['x'], subset['y'], 
                                      c='red', marker='x', s=60, zorder=5)
                scatter_dict[(team, q, made)] = plot

    # 3. 통계 텍스트 객체
    home_stat_text = ax.text(175, -50, "", fontsize=16, fontweight='bold', ha='center', va='top', color='black')
    away_stat_text = ax.text(525, -50, "", fontsize=16, fontweight='bold', ha='center', va='top', color='black')

    # 팀 이름 및 타이틀
    ax.text(175, 430, f"HOME\n{home_name}", fontsize=14, fontweight='bold', ha='center', va='bottom', color='#333333')
    ax.text(525, 430, f"AWAY\n{away_name}", fontsize=14, fontweight='bold', ha='center', va='bottom', color='#333333')
    
    ax.set_xlim(0, 700)
    ax.set_ylim(-100, 450)
    ax.axis('off')
    plt.title(f"KBL Shot Chart: {title}", fontsize=16, fontweight='bold', pad=40)

    # =========================================================================
    # 컨트롤러
    # =========================================================================
    
    rax_q = plt.axes([0.02, 0.65, 0.15, 0.2]) 
    available_qs = sorted(df['quarter'].unique())
    available_qs.sort(key=lambda x: x if x[0]=='Q' else 'Z')
    q_check = CheckButtons(rax_q, available_qs, [True]*len(available_qs))
    rax_q.set_title("쿼터 필터")

    rax_t = plt.axes([0.02, 0.45, 0.15, 0.12])
    t_check = CheckButtons(rax_t, [home_name, away_name], [True, True])
    rax_t.set_title("팀 필터")
    
    rax_r = plt.axes([0.02, 0.28, 0.15, 0.12])
    r_check = CheckButtons(rax_r, ["성공 (O)", "실패 (X)"], [True, True])
    rax_r.set_title("결과 필터")

    # --- [핵심] 통합 업데이트 함수 ---
    def update(label):
        active_qs = [l for l, a in zip(available_qs, q_check.get_status()) if a]
        
        t_status = t_check.get_status()
        active_teams = []
        if t_status[0]: active_teams.append('Home')
        if t_status[1]: active_teams.append('Away')
        
        r_status = r_check.get_status()
        active_results = []
        if r_status[0]: active_results.append(True)
        if r_status[1]: active_results.append(False)
        
        # 1. 그래프 Visibility
        for (team, q, made), plot_obj in scatter_dict.items():
            if (team in active_teams) and (q in active_qs) and (made in active_results):
                plot_obj.set_visible(True)
            else:
                plot_obj.set_visible(False)
        
        # 2. 통계 텍스트 업데이트 (수정된 부분)
        def calculate_stat(team_key):
            # (A) 팀이 체크 해제되어 있어도 0/0으로 표시
            if team_key not in active_teams:
                return "0.0% (0/0)"
            
            # (B) 팀은 켜져 있으나, 데이터 필터링
            subset = df[
                (df['team'] == team_key) & 
                (df['quarter'].isin(active_qs)) &
                (df['made'].isin(active_results))
            ]
            
            total = len(subset)
            # (C) 쿼터가 다 꺼지거나 해서 슛이 0개인 경우도 0/0으로 표시
            if total == 0:
                return "0.0% (0/0)"

            made_count = len(subset[subset['made'] == True])
            pct = (made_count / total * 100)
            return f"{pct:.1f}% ({made_count}/{total})"

        # 텍스트 갱신
        home_stat_text.set_text(calculate_stat('Home'))
        away_stat_text.set_text(calculate_stat('Away'))

        plt.draw()

    # 이벤트 연결 및 초기화
    q_check.on_clicked(update)
    t_check.on_clicked(update)
    r_check.on_clicked(update)
    update(None)

    plt.show()

if __name__ == "__main__":
    target_json_file = "../kbl_chart_data/2025-2026/S47G01N48.json"
    if os.path.exists(target_json_file):
        visualize_shot_chart(target_json_file)
    else:
        print(f"파일을 찾을 수 없습니다: {target_json_file}")