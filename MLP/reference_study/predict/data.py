import torch

def load_state(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"], {k: v for k, v in ckpt.items() if k != "state_dict"}
    return ckpt, {}