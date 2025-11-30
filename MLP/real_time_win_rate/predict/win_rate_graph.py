from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def draw_win_rate_graph(result: dict, save_path: str | Path):
    gameKey = result["metainfo"]["gameKey"]
    max_n = result["metainfo"]["max_n"]
    true_winner = result["metainfo"]["winner"]

    home_win_rates = []
    secs = []
    for n in range(1, max_n + 1):
        if n in result:
            sec = result[n]["total_sec"]
            home_prob = result[n]["home"]
            away_prob = result[n]["away"]
            if home_prob + away_prob < 0.99 or home_prob + away_prob > 1.01:
                raise ValueError(f"n={n}에서 확률 합이 1이 아닙니다: home={home_prob}, away={away_prob}")
            
            if secs and secs[-1] == sec:
                # 동일한 sec 값이 있을 경우 덮어쓰기
                home_win_rates[-1] = home_prob * 100
            else:
                home_win_rates.append(home_prob * 100)
                secs.append(sec)
        else:
            raise ValueError(f"n={n} 데이터가 없습니다.")

    home_win_rates = np.array(home_win_rates)
    secs = np.array(secs)

    plt.figure(figsize=(11, 6))

    # 🔵 아래쪽(Home 영역)
    plt.fill_between(
        secs, home_win_rates, -50,
        color='lightblue', alpha=0.4
    )

    # 🔴 위쪽(Away 영역)
    plt.fill_between(
        secs, home_win_rates, 150,
        color='lightcoral', alpha=0.4
    )

    # 🔵 Home win rate 선
    plt.plot(secs, home_win_rates, color='blue', linewidth=2)
    
    # 상한선 및 하한선 및 중간선
    plt.hlines(0, 0, secs[-1], colors='blue', linestyles='dashed', alpha=0.7)
    plt.hlines(100, 0, secs[-1], colors='red', linestyles='dashed', alpha=0.7)
    plt.hlines(50, 0, secs[-1], colors='gray', linestyles='dashed', alpha=0.7)

    # 위쪽 라벨 (Away)
    plt.text(
        secs[-1], 100, "AWAY", color='red',
        fontsize=14, fontweight='bold', ha='center'
    )

    # 아래쪽 라벨 (Home)
    plt.text(
        secs[-1], 0, "HOME", color='blue',
        fontsize=14, fontweight='bold', ha='center'
    )

    plt.xlabel('Game Time (sec)')
    plt.ylabel('Win Rate (%)')
    plt.title(f'Real-Time Win Rate {gameKey} (True Winner: {true_winner})')

    plt.ylim(-5, 105)
    # 표시하고 싶은 값(라벨)
    labels = [100, 90, 80, 70, 60, 50, 60, 70, 80, 90, 100]

    # 실제 위치(0~100)는 그대로지만
    plt.yticks(ticks=range(0, 101, 10), labels=labels)
    plt.xlim(-60, secs[-1]+60)
    plt.xticks(np.arange(0, secs[-1]+1, 300))
    plt.grid(True, alpha=0.4)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()