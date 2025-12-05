from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# 처음 한 번만 실행
plt.ion()
fig, ax = plt.subplots(figsize=(11, 6))

def draw_win_rate_graph(record: dict, URL: str):
    gameKey = URL.split("/")[-2]

    home_win_rates = []
    secs = []

    for entry in record:
        sec = entry["total_time_sec"]
        home_prob = entry["home_win_rate"]
        away_prob = entry["away_win_rate"]
        
        if home_prob + away_prob < 0.99 or home_prob + away_prob > 1.01:
            raise ValueError("승률의 합이 1이 아닙니다.")

        home_win_rates.append(home_prob * 100)
        secs.append(sec)

    home_win_rates = np.array(home_win_rates)
    secs = np.array(secs)

    # 🔥 기존 그래프 지우기
    ax.cla()

    # 🔵 Home 영역
    ax.fill_between(secs, home_win_rates, -50, color='lightblue', alpha=0.4)

    # 🔴 Away 영역
    ax.fill_between(secs, home_win_rates, 150, color='lightcoral', alpha=0.4)

    # 🔵 Home win rate 선
    ax.plot(secs, home_win_rates, color='blue', linewidth=2)

    # 기준선들
    ax.hlines(0, 0, secs[-1], colors='blue', linestyles='dashed', alpha=0.7)
    ax.hlines(50, 0, secs[-1], colors='gray', linestyles='dashed', alpha=0.7)
    ax.hlines(100, 0, secs[-1], colors='red', linestyles='dashed', alpha=0.7)

    ax.text(secs[-1], 0, "HOME", color='blue', fontsize=14, fontweight='bold', ha='center')
    ax.text(secs[-1], 100, "AWAY", color='red', fontsize=14, fontweight='bold', ha='center')

    ax.set_xlabel("Game Time (sec)")
    ax.set_ylabel("Win Rate (%)")
    ax.set_title(f"Real-Time Win Rate {gameKey}")

    ax.set_ylim(-5, 105)
    labels = [100, 90, 80, 70, 60, 50, 60, 70, 80, 90, 100]
    ax.set_yticks(ticks=range(0, 101, 10), labels=labels)
    last_time = max(secs[-1], 2400)
    ax.set_xlim(-60, last_time + 60)
    ax.set_xticks(np.arange(0, last_time + 1, 300))
    ax.grid(True, alpha=0.4)

    # 🔥 그래프 갱신
    fig.canvas.draw()
    fig.canvas.flush_events()