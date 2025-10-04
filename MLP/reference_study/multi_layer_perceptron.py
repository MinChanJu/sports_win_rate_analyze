from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import torch.nn as nn
import pandas as pd
import numpy as np
import torch

def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)

    # GPU 사용 시
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # 연산의 재현성 보장 (다만 속도는 약간 느려질 수 있음)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def combine_load(paths):
    df_list = [pd.read_csv(path) for path in paths]
    df = pd.concat(df_list, ignore_index=True)

    drop_cols = ["gameKey", "seasonName", "date", "H_TEAM", "A_TEAM", "quarter"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})

    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    return X_train, X_test, y_train, y_test
    
def load(path):
    df = pd.read_csv(path)

    drop_cols = ["gameKey", "seasonName", "date", "H_TEAM", "A_TEAM", "quarter"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)
    df["winner"] = df["winner"].map({"home": 0, "away": 1})

    X = df.drop("winner", axis=1).values.astype(np.float32)
    y = df["winner"].values.astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    return X_train, X_test, y_train, y_test

def train_model(X_train, X_test, y_train, y_test):
    
    # ----- 텐서 변환 -----
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.long)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.long)

    # ----- Dataset & DataLoader -----
    train_ds = TensorDataset(X_train_t, y_train_t)
    test_ds = TensorDataset(X_test_t, y_test_t)

    train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_dl = DataLoader(test_ds, batch_size=256)

    # ----- MLP 모델 (마지막 출력 2개) -----
    model = nn.Sequential(
        nn.Linear(X_train.shape[1], 32),
        nn.ReLU(),
        nn.Linear(32, 16),
        nn.ReLU(),
        nn.Linear(16, 2),
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    Epochs = 1000

    # ----- 학습 루프 -----
    for epoch in range(Epochs):
        # --- Train ---
        model.train()
        running_loss = 0.0
        for xb, yb in train_dl:
            logits = model(xb)
            loss = criterion(logits, yb)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(xb)

        # --- Test ---
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for xb, yb in test_dl:
                logits = model(xb)
                pred = torch.argmax(logits, dim=1)
                correct += (pred == yb).sum().item()
                total += len(yb)

        if (epoch + 1) % 100 == 0:
            print(
                f"epoch {epoch+1:2d} | train_loss {running_loss/len(train_ds):.4f} | test_acc {correct/total:.3f}"
            )


if __name__ == "__main__":
    set_seed()
    kbl_data_path = [
        "./kbl_data_quarter_csv/2021-2022.csv",
        "./kbl_data_quarter_csv/2022-2023.csv",
        "./kbl_data_quarter_csv/2023-2024.csv",
        "./kbl_data_quarter_csv/2024-2025.csv",
    ]

    for path in kbl_data_path:
        print(f"Training with data from: {path}")
        X_train, X_test, y_train, y_test = load(path)
        train_model(X_train, X_test, y_train, y_test)
    
    print("Training with combined data from all seasons.")
    X_train, X_test, y_train, y_test = combine_load(kbl_data_path)
    train_model(X_train, X_test, y_train, y_test)
