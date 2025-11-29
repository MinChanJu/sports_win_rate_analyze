import argparse

_args = None

def get_args() -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--model-dir", type=str, default="../models/03")
        parser.add_argument("--model-type", type=str, default="combined")
        parser.add_argument("--predict-split", action="store_true", default=True)
        parser.add_argument("--seed", type=int, default=42)
        
        _args = parser.parse_args()
    return _args