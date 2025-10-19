import argparse

_args = None

def get_args() -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ckpt-path", type=str, default="../models/13")
        parser.add_argument("--report-filename", type=str, default="predict_report.json")
        parser.add_argument("--output-filename", type=str, default="table_report.md")
        _args = parser.parse_args()
    return _args