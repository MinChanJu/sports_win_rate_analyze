import argparse

_args = None

def get_args() -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ckpt-path", type=str, default="../models/13")
        parser.add_argument("--model-filename", type=str, default="combined_best_model.pt")
        parser.add_argument("--predict-csv", type=str, default="../kbl_data_quarter_csv/2023-2024.csv")
        parser.add_argument("--predict-range", type=str, default=":")  # 예: "0:100" 또는 "909:"
        parser.add_argument("--report-path", type=str, default="report.json")
        parser.add_argument("--team-code-path", type=str, default="../train/teamcode.json")
        
        _args = parser.parse_args()
    return _args