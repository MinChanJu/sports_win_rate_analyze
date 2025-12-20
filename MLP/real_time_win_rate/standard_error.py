import json
from pathlib import Path
import matplotlib.pyplot as plt
import subprocess
import sys

def train(split_seed: int = 42, no_per_season: bool = False, save_folder: str = "../models"):
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
  print_every = 100
  eval_every = 1
  patience = 20
  min_delta = 0.0
  weight_decay = 1e-2
  monitor = "val_loss"
  save_best = True          # ← 참이면 플래그 추가
  model_folder = save_folder

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

def draw_learning_curve(save_path: Path, train_history: list[float], val_history: list[float], test_history: list[float], name: str) -> None:
  epochs = range(1, len(train_history) + 1)
  plt.figure()
  plt.plot(epochs, train_history, label=f"Train {name}")
  plt.plot(epochs, val_history, label=f"Validation {name}")
  plt.plot(epochs, test_history, label=f"Test {name}")
  plt.xlabel("Epoch")
  plt.ylabel(f"{name}")
  plt.title(f"{name} Curve")
  plt.legend()
  plt.grid(True)
  plt.ylim(0, 1.1)
  plt.savefig(save_path, dpi=200)
  plt.close()
  print(f"[saved] {name} learning curve -> {save_path}")
  
  history = {
    "train": train_history,
    "validation": val_history,
    "test": test_history
  }

  json_path = save_path.with_name(f"{name.lower().replace(' ', '_')}_history.json")

  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)
  print(f"[saved] {name} history -> {json_path}")
  
def standard_error(n: int, save_folder: str, seeds: list[int]) -> None:
  subdirs = [d for d in Path(save_folder[1:]).iterdir() if d.is_dir() and d.name.isdigit()]
  if not subdirs:
    print("저장된 모델 폴더가 없습니다.")
    sys.exit(1)
    
  save_folder_sorted = sorted(subdirs, key=lambda x: int(x.name))
  save_folders = save_folder_sorted[-n:]
  if len(save_folders) < n:
    print(f"충분한 모델 폴더가 없습니다: {len(save_folders)}개 발견, {n}개 필요")
    sys.exit(1)
  
  print(f"{len(save_folders)}개의 모델 폴더를 사용합니다: {[d.name for d in save_folders]}\n")
  print(f"seeds: {seeds}\n")
  standard_save_folder = Path(save_folder[1:], f"standard_error_{save_folders[0].name}~{save_folders[-1].name}")
  print(f"표준 오차 저장 폴더: {standard_save_folder}\n")
  
  for model_type in ['2021-2022', '2022-2023', '2023-2024', '2024-2025', 'combined']:
    if (Path(save_folders[0], model_type).exists() == False):
      print(f"모델 폴더가 없습니다: {Path(save_folders[0], model_type)}")
      continue
  
    print(f"\n표준 오차 계산 중... 모델 유형: {model_type}")
  
    standard_loss_history = {
      'train': [],
      'validation': [],
      'test': [],
    }

    standard_accuracy_history = {
      'train': [],
      'validation': [],
      'test': [],
    }
    
    for save_folder in save_folders:
      model_dir = Path(save_folder, model_type)
      loss_history_path = model_dir / "loss_history.json"
      accuracy_history_path = model_dir / "accuracy_history.json"
      
      if not loss_history_path.exists():
        print(f"손실 기록 파일이 없습니다: {loss_history_path}")
        continue
      if not accuracy_history_path.exists():
        print(f"정확도 기록 파일이 없습니다: {accuracy_history_path}")
        continue

      with open(loss_history_path, 'r') as f:
        loss_history = json.load(f)
        for key in ["train", "validation", "test"]:
          for idx, value in enumerate(loss_history[key]):
            if len(standard_loss_history[key]) <= idx:
              standard_loss_history[key].append((0, 0))
            standard_loss_history[key][idx] = (
              standard_loss_history[key][idx][0] + value,
              standard_loss_history[key][idx][1] + 1
            )

      with open(accuracy_history_path, 'r') as f:
        accuracy_history = json.load(f)
        for key in ["train", "validation", "test"]:
          for idx, value in enumerate(accuracy_history[key]):
            if len(standard_accuracy_history[key]) <= idx:
              standard_accuracy_history[key].append((0, 0))
            standard_accuracy_history[key][idx] = (
              standard_accuracy_history[key][idx][0] + value,
              standard_accuracy_history[key][idx][1] + 1
            )
    
    for key in ["train", "validation", "test"]:
      for idx in range(len(standard_loss_history[key])):
        if standard_loss_history[key][idx][1] < n:
          standard_loss_history[key] = standard_loss_history[key][:idx]
          break
        standard_loss_history[key][idx] = standard_loss_history[key][idx][0] / standard_loss_history[key][idx][1]
      for idx in range(len(standard_accuracy_history[key])):
        if standard_accuracy_history[key][idx][1] < n:
          standard_accuracy_history[key] = standard_accuracy_history[key][:idx]
          break
        standard_accuracy_history[key][idx] = standard_accuracy_history[key][idx][0] / standard_accuracy_history[key][idx][1]

    print(f"\n=== Standard Error for model type: {model_type} ===")
    Path(standard_save_folder, model_type).mkdir(parents=True, exist_ok=True)
    draw_learning_curve(
      save_path=Path(standard_save_folder, model_type, "standard_loss_curve.png"),
      train_history=standard_loss_history['train'],
      val_history=standard_loss_history['validation'],
      test_history=standard_loss_history['test'],
      name="Standard Loss"
    )
    draw_learning_curve(
      save_path=Path(standard_save_folder, model_type, "standard_accuracy_curve.png"),
      train_history=standard_accuracy_history['train'],
      val_history=standard_accuracy_history['validation'],
      test_history=standard_accuracy_history['test'],
      name="Standard Accuracy"
    )
    print()

if __name__ == "__main__":
  import random
  random.seed(42)
  
  n = 50
  save_folder="../standard_models"
  seeds = random.sample(range(1000), n)

  # for i, seed in enumerate(seeds):
  #   print(f"\n=== {i+1}th Running with split seed: {seed} ===")
  #   train(split_seed=seed, no_per_season=True, save_folder=save_folder)
  
  standard_error(n, save_folder, seeds)