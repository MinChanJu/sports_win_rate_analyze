import json
import platform
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic' if platform.system() == 'Darwin' else 'Malgun Gothic'  # ✅ 운영체제에 따른 한글 폰트 설정
plt.rcParams['font.size'] = 5  # ✅ 폰트 크기 설정
plt.rcParams['axes.unicode_minus'] = False # ✅ 마이너스 기호 깨짐 방지

DEFAULT_DROP_COLS = ["gameKey", "seasonName", "date", "quarter"]
csv_path = Path(__file__).parent / "../kbl_data_csv/2021-2022.csv"
save_path = Path(__file__).parent / "."

def main():
  df = pd.read_csv(csv_path)
  
  drop_cols = [c for c in DEFAULT_DROP_COLS if c in df.columns]
  df = df.drop(columns=drop_cols)
  df["winner"] = df["winner"].map({"home": 0, "away": 1})
  numeric_df = df.select_dtypes(include=["number"])
  
  corr = numeric_df.corr()
  plt.figure(figsize=(24, 20))
  sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
  plt.title("전체 변수 간 상관관계 Heatmap")
  plt.savefig(save_path / "full_correlation_heatmap.png", bbox_inches='tight', dpi=300)

  winner_corr = corr["winner"]
  
  filtered_vars = winner_corr[abs(winner_corr) > 0.2].index
  filtered_corr = numeric_df[filtered_vars].corr()
  plt.figure(figsize=(12, 10))
  sns.heatmap(filtered_corr, annot=True, fmt=".2f", cmap="coolwarm")
  plt.title("‘winner’와 |r| > 0.1 변수들 간 Heatmap")
  plt.savefig(save_path / "winner_correlation_heatmap.png", bbox_inches='tight', dpi=300)

  winner_corr_sorted = winner_corr.sort_values(ascending=False)
  plt.figure(figsize=(6, 10))
  sns.barplot(
    x=winner_corr_sorted.values,
    y=winner_corr_sorted.index,
    palette="coolwarm",
    hue=winner_corr_sorted.index,
  )
  plt.title("‘winner’ 변수와의 상관관계")
  plt.xlabel("상관계수 (Correlation)")
  plt.ylabel("변수명")
  plt.savefig(save_path / "winner_correlation_barplot.png", bbox_inches='tight', dpi=300)

if __name__ == "__main__":
  main()