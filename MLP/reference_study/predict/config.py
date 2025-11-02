import argparse

_args = None

def get_args() -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--model-dir", type=str, default="../models/01")
        parser.add_argument("--model-type", type=str, default="combined")
        parser.add_argument("--predict-split", action="store_true", default=True)
        parser.add_argument("--team-code-path", type=str, default="../train/teamcode.json")
        
        _args = parser.parse_args()
    return _args