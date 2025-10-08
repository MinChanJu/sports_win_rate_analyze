from data_utils import load_single_csv, load_multi_csv
from train_utils import train_model, set_seed
from config import get_args
from pathlib import Path
import sys

def main():
    args = get_args()
    set_seed()

    csv_paths = [str(Path(p)) for p in args.csv if Path(p).exists()]
    if not csv_paths:
        print("CSV 파일을 찾을 수 없습니다.")
        sys.exit(1)

    if not args.no_per_season:
        for path in csv_paths:
            print(f"\n=== Training with {path} ===")
            train_model(load_single_csv(path))

    if len(csv_paths) >= 2:
        print("\n=== Training with combined data ===")
        train_model(load_multi_csv(csv_paths))

if __name__ == "__main__":
    main()