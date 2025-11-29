from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def draw_win_rate_graph(result: dict, save_path: str | Path):
    gameKey = result["metainfo"]["gameKey"]
    max_n = result["metainfo"]["max_n"]
    true_winner = result["metainfo"]["winner"]

    home_win_rates = []
    ns = []
    for n in range(1, max_n + 1):
        if n in result:
            home_prob = result[n]["home"]
            away_prob = result[n]["away"]
            if home_prob + away_prob < 0.99 or home_prob + away_prob > 1.01:
                raise ValueError(f"n={n}에서 확률 합이 1이 아닙니다: home={home_prob}, away={away_prob}")
            home_win_rates.append(home_prob * 100)
            ns.append(n)
        else:
            raise ValueError(f"n={n} 데이터가 없습니다.")

    home_win_rates = np.array(home_win_rates)
    ns = np.array(ns)

    plt.figure(figsize=(11, 6))

    # 🔵 아래쪽(Home 영역)
    plt.fill_between(
        ns, home_win_rates, -50,
        color='lightblue', alpha=0.4
    )

    # 🔴 위쪽(Away 영역)
    plt.fill_between(
        ns, home_win_rates, 150,
        color='lightcoral', alpha=0.4
    )

    # 🔵 Home win rate 선
    plt.plot(ns, home_win_rates, color='blue', linewidth=2)
    
    # 상한선 및 하한선 및 중간선
    plt.hlines(0, 0, max_n, colors='blue', linestyles='dashed', alpha=0.7)
    plt.hlines(100, 0, max_n, colors='red', linestyles='dashed', alpha=0.7)
    plt.hlines(50, 0, max_n, colors='gray', linestyles='dashed', alpha=0.7)

    # 위쪽 라벨 (Away)
    plt.text(
        max_n, 100, "AWAY", color='red',
        fontsize=14, fontweight='bold', ha='center'
    )

    # 아래쪽 라벨 (Home)
    plt.text(
        max_n, 0, "HOME", color='blue',
        fontsize=14, fontweight='bold', ha='center'
    )

    plt.xlabel('n (In-Game Time Unit)')
    plt.ylabel('Win Rate (%)')
    plt.title(f'Real-Time Win Rate {gameKey} (True Winner: {true_winner})')

    plt.ylim(-5, 105)
    plt.xlim(0, max_n)
    plt.grid(True, alpha=0.4)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()