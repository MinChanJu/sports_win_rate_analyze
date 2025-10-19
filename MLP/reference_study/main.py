from pathlib import Path
import subprocess
import sys

def main():
  # 경로 설정
  BASE = Path(__file__).resolve().parent
  TRAIN_DIR = BASE / "train"

  train_csvs = [
    "../kbl_data_csv/2021-2022.csv",
    "../kbl_data_csv/2022-2023.csv",
    "../kbl_data_csv/2023-2024.csv",
    "../kbl_data_csv/2024-2025.csv",
  ]

  # 하이퍼파라미터
  seed = 42
  lr = 1e-4
  epochs = 500
  batch_train = 32
  batch_test = 128
  valid_size = 0.1
  test_size = 0.2
  print_every = 10
  eval_every = 1
  patience = 20
  min_delta = 0.0
  weight_decay = 1e-2
  no_per_season = False     # ← 참이면 플래그 추가
  monitor = "val_loss"
  save_best = True           # ← 참이면 플래그 추가
  ckpt_folder = "../models"

  # 인자 구성
  args = [
    "python", "main.py",
    "--csv", *train_csvs,
    "--seed", str(seed),
    "--lr", str(lr),
    "--epochs", str(epochs),
    "--batch-train", str(batch_train),
    "--batch-test", str(batch_test),
    "--valid-size", str(valid_size),
    "--test-size", str(test_size),
    "--print-every", str(print_every),
    "--eval-every", str(eval_every),
    "--patience", str(patience),
    "--min-delta", str(min_delta),
    "--weight-decay", str(weight_decay),
    "--monitor", monitor,
    "--ckpt-folder", ckpt_folder,
  ]
  if no_per_season:
    args += ["--no-per-season"]
  if save_best:
    args += ["--save-best"]

  print("running training...")
  subprocess.run(args, cwd=TRAIN_DIR, text=True)
  
  PREDICT_DIR = BASE / "predict"
  
  subdirs = [d for d in Path("./models").iterdir() if d.is_dir() and d.name.isdigit()]
    
  if not subdirs:
    print("저장된 모델 폴더가 없습니다.")
    sys.exit(1)
    
  save_folder = sorted(subdirs, key=lambda x: int(x.name))[-1]
  print("저장된 폴더:", save_folder)

  ckpt_folder = Path('../', save_folder)

  args = [
    "python", "main.py",
    "--ckpt-path", ckpt_folder,
    "--model-filename", "combined_best_model.pt",
    "--predict-csv", "../kbl_data_quarter_csv/2023-2024.csv",
    "--predict-range", ":",
    "--report-path", (ckpt_folder / "predict_report.json").as_posix(),
    "--team-code-path", "../train/teamcode.json",
  ]
  
  print("running prediction...")
  subprocess.run(args, cwd=PREDICT_DIR, text=True)
  
  TABLE_DIR = BASE / "table"
  
  args = [
    "python", "main.py",
    "--ckpt-path", ckpt_folder,
    "--report-filename", "predict_report.json",
    "--output-filename", "table_report.md",
  ]
  
  print("generating table report...")
  subprocess.run(args, cwd=TABLE_DIR, text=True)

if __name__ == "__main__":
  main()