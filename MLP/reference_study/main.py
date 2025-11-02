from pathlib import Path
import subprocess
import sys

def main(no_per_season: bool = False):
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
  split_seed = 42
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
  no_per_season = no_per_season     # ← 참이면 플래그 추가
  monitor = "val_loss"
  save_best = True           # ← 참이면 플래그 추가
  model_folder = "../models"

  # 인자 구성
  args = [
    "python", "main.py",
    "--csv", *train_csvs,
    "--split-seed", str(split_seed),
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
    "--model-folder", model_folder,
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

  model_dir = Path('../', save_folder)

  if (not no_per_season):
    for model_type in ['2021-2022', '2022-2023', '2023-2024', '2024-2025']:
      args = [
        "python", "main.py",
        "--model-dir", model_dir,
        "--model-type", model_type,
        "--predict-split",
        "--team-code-path", "../train/teamcode.json",
      ]
      
      print(f"running prediction for {model_type}...")
      subprocess.run(args, cwd=PREDICT_DIR, text=True)

  args = [
    "python", "main.py",
    "--model-dir", model_dir,
    "--model-type", "combined",
    "--predict-split",
    "--team-code-path", "../train/teamcode.json",
  ]

  print("running prediction for combined...")
  subprocess.run(args, cwd=PREDICT_DIR, text=True)
  
  TABLE_DIR = BASE / "table"
  
  if not no_per_season:
    for model_type in ['2021-2022', '2022-2023', '2023-2024', '2024-2025']:
      args = [
        "python", "main.py",
        "--model-dir", model_dir,
        "--model-type", model_type,
      ]
      
      print(f"generating table report for {model_type}...")
      subprocess.run(args, cwd=TABLE_DIR, text=True)
  
  args = [
    "python", "main.py",
    "--model-dir", model_dir,
    "--model-type", "combined",
  ]
  
  print("generating table report for combined...")
  subprocess.run(args, cwd=TABLE_DIR, text=True)


def train(split_seed: int = 42, no_per_season: bool = False):
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
  monitor = "val_loss"
  save_best = True           # ← 참이면 플래그 추가
  model_folder = "../models"

  # 인자 구성
  args = [
    "python", "main.py",
    "--csv", *train_csvs,
    "--split-seed", str(split_seed),
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
    "--model-folder", model_folder,
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

  model_dir = Path('../', save_folder)

  if (not no_per_season):
    for model_type in ['2021-2022', '2022-2023', '2023-2024', '2024-2025']:
      args = [
        "python", "main.py",
        "--model-dir", model_dir,
        "--model-type", model_type,
        "--predict-split",
        "--team-code-path", "../train/teamcode.json",
      ]
      
      print(f"running prediction for {model_type}...")
      subprocess.run(args, cwd=PREDICT_DIR, text=True)

  args = [
    "python", "main.py",
    "--model-dir", model_dir,
    "--model-type", "combined",
    "--predict-split",
    "--team-code-path", "../train/teamcode.json",
  ]

  print("running prediction for combined...")
  subprocess.run(args, cwd=PREDICT_DIR, text=True)
  
  TABLE_DIR = BASE / "table"
  
  if not no_per_season:
    for model_type in ['2021-2022', '2022-2023', '2023-2024', '2024-2025']:
      args = [
        "python", "main.py",
        "--model-dir", model_dir,
        "--model-type", model_type,
      ]
      
      print(f"generating table report for {model_type}...")
      subprocess.run(args, cwd=TABLE_DIR, text=True)
  
  args = [
    "python", "main.py",
    "--model-dir", model_dir,
    "--model-type", "combined",
  ]
  
  print("generating table report for combined...")
  subprocess.run(args, cwd=TABLE_DIR, text=True)

if __name__ == "__main__":
  main()