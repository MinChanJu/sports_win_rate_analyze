# config.py
import argparse

_args = None

def get_args():
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--csv", nargs="*", default=[
            "../kbl_data_quarter_csv/2021-2022.csv",
            "../kbl_data_quarter_csv/2022-2023.csv",
            "../kbl_data_quarter_csv/2023-2024.csv",
            "../kbl_data_quarter_csv/2024-2025.csv",
        ])
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--lr", type=float, default=1e-5)
        parser.add_argument("--epochs", type=int, default=500)

        parser.add_argument("--batch-train", type=int, default=64)
        parser.add_argument("--batch-test", type=int, default=256)

        parser.add_argument("--valid-size", type=float, default=0.1)
        parser.add_argument("--test-size", type=float, default=0.2)

        parser.add_argument("--print-every", type=int, default=10)
        parser.add_argument("--eval-every", type=int, default=1)
        parser.add_argument("--patience", type=int, default=20)
        parser.add_argument("--min-delta", type=float, default=0.0)

        parser.add_argument("--weight-decay", type=float, default=1e-2)
        parser.add_argument("--no-per-season", action="store_true")
        parser.add_argument("--monitor", type=str, default="val_loss", choices=["val_loss", "val_acc"])

        parser.add_argument("--save-best", type=bool, default=True)
        parser.add_argument("--ckpt-path", type=str, default="best_model.pt")
        _args = parser.parse_args()
    return _args