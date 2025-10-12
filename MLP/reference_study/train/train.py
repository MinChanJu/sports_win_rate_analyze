from torch.utils.data import DataLoader, TensorDataset
from contextlib import nullcontext
from datetime import datetime
from model import MLP
from config import get_args
from pathlib import Path
from tqdm import tqdm
import numpy as np
import torch
import json
import os

def set_seed() -> None:
    args = get_args()
    seed = args.seed
    import numpy as np
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def get_device() -> torch.device:
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

def maybe_autocast(device: torch.device) -> torch.autocast | nullcontext:
    if device.type in {"mps", "cuda"}:
        try:
            return torch.autocast(device_type=device.type, dtype=torch.bfloat16)
        except Exception:
            return torch.autocast(device_type=device.type, dtype=torch.float16)
    return nullcontext()

def make_dataloaders(train_ds: TensorDataset, test_ds: TensorDataset, device: torch.device) -> tuple[DataLoader, DataLoader]:
    args = get_args()
    batch_train = args.batch_train
    batch_test = args.batch_test

    is_cuda = device.type == "cuda"
    pin_mem = True if is_cuda else False
    num_workers = max(1, (os.cpu_count() or 2) // 2)
    kwargs = dict(num_workers=num_workers, pin_memory=pin_mem)
    if num_workers > 0:
        kwargs.update(dict(persistent_workers=True, prefetch_factor=2))

    train_dl = DataLoader(train_ds, batch_size=batch_train, shuffle=True, **kwargs)
    test_dl = DataLoader(test_ds, batch_size=batch_test, shuffle=False, **kwargs)
    return train_dl, test_dl

def evaluate(model: MLP, data_loader: DataLoader, device: torch.device, amp_ctx: torch.autocast | nullcontext, criterion: torch.nn.Module) -> tuple[float, float]:
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for xb, yb in data_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            with amp_ctx:
                logits = model(xb)
                loss = criterion(logits, yb)
            total_loss += loss.item() * xb.size(0)
            pred = logits.argmax(dim=1)
            correct += (pred == yb).sum().item()
            total += yb.size(0)
    avg_loss = total_loss / max(total, 1)
    acc = correct / max(total, 1)
    return avg_loss, acc

def save_model(save_path: Path, best_model_state: dict, best_metrics: dict, best_optimizer_state: dict) -> None:
    args = get_args()
    payload = {
        "config": {
            "epochs": args.epochs,
            "seed": args.seed,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "patience": args.patience,
            "min_delta": args.min_delta,
            "monitor": args.monitor,
        },
        "metrics": best_metrics,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "torch_version": torch.__version__,
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "device": str(get_device()),
    }

    model_payload = dict(payload)
    model_payload["state_dict"] = best_model_state
    model_payload["optimizer_state_dict"] = best_optimizer_state

    torch.save(model_payload, save_path)
    print(f"[saved] model -> {save_path}")
    json_path = save_path.with_suffix(".json")  # .pt → .json

    json_payload = dict(payload)
    size_bytes = save_path.stat().st_size
    size_mb = round(size_bytes / (1024 * 1024), 2)  # MB 단위로 소수점 2자리
    json_payload["model"] = {
        "path": str(save_path.relative_to(json_path.parent)),
        "size_bytes": size_bytes,
        "size_mb": size_mb,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, ensure_ascii=False, indent=2)
    print(f"[saved] metadata -> {json_path}")

def train_model(save_path: Path, data: dict[str, dict[str, np.ndarray]]) -> tuple[MLP, float]:
    set_seed()

    # ----- 데이터 꺼내기 -----
    X_train, y_train = data["train"]["X"], data["train"]["y"]
    X_valid, y_valid = data["valid"]["X"], data["valid"]["y"]
    X_test,  y_test  = data["test"]["X"],  data["test"]["y"]
    
    # ----- 하이퍼파라미터/옵션 -----
    args = get_args()
    save_best    = args.save_best
    epochs       = args.epochs
    lr           = args.lr
    weight_decay = args.weight_decay
    print_every  = args.print_every
    monitor      = args.monitor          # 'val_loss' or 'val_acc'
    patience     = args.patience
    min_delta    = args.min_delta
    eval_every   = args.eval_every

    device = get_device()
    print(f"[device] {device}")

    # ----- Dataset은 CPU 유지 (MPS 멀티프로세싱 호환) -----
    X_tr_t  = torch.tensor(X_train, dtype=torch.float32)
    y_tr_t  = torch.tensor(y_train, dtype=torch.long)
    X_va_t  = torch.tensor(X_valid, dtype=torch.float32)
    y_va_t  = torch.tensor(y_valid, dtype=torch.long)
    X_te_t  = torch.tensor(X_test,  dtype=torch.float32)
    y_te_t  = torch.tensor(y_test,  dtype=torch.long)

    train_ds = TensorDataset(X_tr_t, y_tr_t)
    valid_ds = TensorDataset(X_va_t, y_va_t)
    test_ds  = TensorDataset(X_te_t, y_te_t)

    train_dl, _ = make_dataloaders(train_ds, test_ds, device)
    valid_dl, test_dl = make_dataloaders(valid_ds, test_ds, device)

    # ----- 모델/손실/옵티마이저 -----
    model = MLP(X_train.shape[1]).to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    amp_ctx = maybe_autocast(device)
    non_blocking = True if device.type == "cuda" else False

    # ----- Early Stopping 상태 -----
    best_metric = float("inf") if monitor == "val_loss" else -float("inf")
    best_model_state = None
    best_optimizer_state = None
    best_metrics = None
    no_improve = 0

    def is_better(curr, best):
        if monitor == "val_loss":
            return (best - curr) > min_delta   # 더 작으면 개선
        else:
            return (curr - best) > min_delta   # 더 크면 개선

    # ----- 학습 루프 -----
    for epoch in tqdm(range(1, epochs + 1), desc=f"{save_path.name.split('_')[0]} training", dynamic_ncols=True, unit="epoch", colour="cyan"):
        model.train()
        running_loss = 0.0

        for xb, yb in train_dl:
            xb = xb.to(device, non_blocking=non_blocking)
            yb = yb.to(device, non_blocking=non_blocking)
            with amp_ctx:
                logits = model(xb)
                loss = criterion(logits, yb)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * xb.size(0)

        # ----- 주기적 평가 -----
        if epoch % eval_every == 0 or epoch == epochs:
            train_loss = running_loss / max(len(train_ds), 1)
            val_loss,  val_acc  = evaluate(model, valid_dl, device, amp_ctx, criterion)
            test_loss, test_acc = evaluate(model, test_dl,  device, amp_ctx, criterion)

            # 얼리 스토핑 체크
            metric_now = val_loss if monitor == "val_loss" else val_acc
            if is_better(metric_now, best_metric):
                best_metric = metric_now
                no_improve = 0
                if save_best:
                    best_model_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                    best_optimizer_state = optimizer.state_dict() if optimizer else None
                    best_metrics = {
                        "epoch": epoch,
                        "train_loss": train_loss,
                        "val_acc": val_acc,
                        "val_loss": val_loss,
                        "test_acc": test_acc,
                        "test_loss": test_loss
                    }
            else:
                no_improve += 1

            if (epoch % print_every == 0) or (epoch == 1) or (epoch == epochs):
                tqdm.write(
                    f"epoch {epoch:3d} | "
                    f"train_loss {train_loss:.4f} | "
                    f"val_loss {val_loss:.4f} val_acc {val_acc:.3f} | "
                    f"test_loss {test_loss:.4f} test_acc {test_acc:.3f} | "
                    f"no_improve {no_improve}/{patience}"
                )

            if no_improve >= patience:
                tqdm.write(f"[early stop] epoch {epoch}에서 {monitor} 기준 개선 없음 → 중단")
                break

    # ----- 최고 성능 모델 저장/복원 & 최종 테스트 리포트 -----
    if save_best and best_model_state and best_metrics and best_optimizer_state:
        save_model(save_path, best_model_state, best_metrics, best_optimizer_state)
        model.load_state_dict(best_model_state)

    final_test_loss, final_test_acc = evaluate(model, test_dl, device, amp_ctx, criterion)
    print(f"[done] final test_acc = {final_test_acc:.3f} (loss {final_test_loss:.4f})")
    return model, final_test_acc