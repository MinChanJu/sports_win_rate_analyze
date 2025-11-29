from data import load_single_csv, load_multi_csv
from train import train_model
from config import get_args
from pathlib import Path
import sys

def main() -> None:
    args = get_args()
    csv_folders = [Path(folder) for folder in args.csv_folders]
    if not csv_folders:
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
        for season_csv_folder in csv_folders:
            season = season_csv_folder.split('/')[-1]
            season_dir = save_dir / season
            season_dir.mkdir(parents=True, exist_ok=True)
            save_path = season_dir / f"best_model.pt"
            data = load_multi_csv([season_csv_folder])
            print(f"\n=== Training with {season} ===")
            print(f"총 {data['train']['X'].shape[0]}개의 학습 데이터 사용")
            train_model(save_path, data)

    if len(csv_folders) >= 2:
        season_dir = save_dir / "combined"
        season_dir.mkdir(parents=True, exist_ok=True)
        save_path = season_dir / "best_model.pt"
        data = load_multi_csv(csv_folders)
        print("\n=== Training with combined data ===")
        print(f"총 {data['train']['X'].shape[0]}개의 학습 데이터 사용")
        train_model(save_path, data)

if __name__ == "__main__":
    main()