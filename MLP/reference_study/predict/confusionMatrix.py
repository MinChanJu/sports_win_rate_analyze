from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import platform
import json

plt.rcParams['font.family'] = 'AppleGothic' if platform.system() == 'Darwin' else 'Malgun Gothic'  # ✅ 운영체제에 따른 한글 폰트 설정

SAVE_SIZE = (6, 4)
SAVE_DPI  = 300

def save_confusion_matrix(report_path: Path, save_path: Path):
  if not report_path.exists():
    print(f"Report file does not exist: {report_path}")
    return
  
  data = json.loads(report_path.read_text())
  y_true = []
  y_pred = []
  for _, gameData in data.items():
    true = gameData["metainfo"]["winner"]
    last_quarter = "연장" if "연장" in gameData else "Q4"
    home = gameData[last_quarter]["home"]
    away = gameData[last_quarter]["away"]
    pred = "home" if home > away else "away"
    y_true.append(true + " win")
    y_pred.append(pred + " win")

  labels = ["home win", "away win"]
  cm = confusion_matrix(y_true, y_pred, labels=labels)
  plt.figure(figsize=SAVE_SIZE)
  sns.heatmap(
      cm,
      annot=True,
      fmt="d",
      cmap="Blues",
      xticklabels=labels,
      yticklabels=labels
  )
  plt.xlabel("예측값 (Predicted)")
  plt.ylabel("실제값 (True)")
  plt.title("Confusion Matrix")
  plt.savefig(save_path, bbox_inches="tight", dpi=SAVE_DPI)
  print(f"[saved] confusion matrix -> {save_path}")

if __name__ == "__main__":
  report_path = Path(__file__).parent / "../models/01/combined_best_model_predict_report.json"
  save_path = Path(__file__).parent / "../models/01/combined_best_model_confusion_matrix.png"
  save_confusion_matrix(report_path, save_path)
