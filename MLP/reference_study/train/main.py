from data import load_single_csv, load_multi_csv
from train import train_model
from config import get_args
from pathlib import Path
import sys

def main() -> None:
    args = get_args()
    csv_paths = [str(Path(p)) for p in args.csv if Path(p).exists()]
    if not csv_paths:
        print("CSV 파일을 찾을 수 없습니다.")
        sys.exit(1)

    model_folder = args.model_folder
    idx = 1
    while (Path(f"{model_folder}/{idx:02d}").exists()):
        idx += 1

    save_dir = Path(f"{model_folder}/{idx:02d}")
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"모델 체크포인트가 저장될 폴더: {save_dir}")

    if not args.no_per_season:
        for path in csv_paths:
            season = path.split('/')[-1].split('.')[0]
            season_dir = save_dir / season
            season_dir.mkdir(parents=True, exist_ok=True)
            save_path = season_dir / f"best_model.pt"
            print(f"\n=== Training with {season} ===")
            train_model(save_path, load_single_csv(path))

    if len(csv_paths) >= 2:
        print("\n=== Training with combined data ===")
        season_dir = save_dir / "combined"
        season_dir.mkdir(parents=True, exist_ok=True)
        save_path = season_dir / "best_model.pt"
        train_model(save_path, load_multi_csv(csv_paths))

if __name__ == "__main__":
    main()