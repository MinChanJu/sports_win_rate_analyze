from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd

df = pd.read_csv("./kbl_data_csv/2021-2022.csv")

drop_cols = ["gameKey", "seasonName", "date", "H_TEAM", "A_TEAM"]
drop_cols = [c for c in drop_cols if c in df.columns]
df = df.drop(columns=drop_cols)
df["winner"] = df["winner"].map({"home": 0, "away": 1})

X = df.drop("winner", axis=1).values.astype(np.float32)
y = df["winner"].values.astype(np.int64)

N, D = X.shape

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ----- 7) 텐서 변환 -----
X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long)
X_test_t  = torch.tensor(X_test,  dtype=torch.float32)
y_test_t  = torch.tensor(y_test,  dtype=torch.long)

# ----- 8) Dataset & DataLoader -----
train_ds = TensorDataset(X_train_t, y_train_t)
test_ds  = TensorDataset(X_test_t,  y_test_t)

train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
test_dl  = DataLoader(test_ds,  batch_size=256)

# ----- MLP 모델 (마지막 출력 2개) -----
model = nn.Sequential(
    nn.Linear(D, 32), nn.ReLU(),
    nn.Linear(32, 16), nn.ReLU(),
    nn.Linear(16, 2)   # <- 출력 2개 (클래스별 로짓)
)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
Epochs = 100

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
        running_loss += loss.item()*len(xb)
    
    # --- Test ---
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for xb, yb in test_dl:
            logits = model(xb)
            pred = torch.argmax(logits, dim=1)
            correct += (pred == yb).sum().item()
            total   += len(yb)

    if ((epoch+1) % 10 == 0): print(f"epoch {epoch+1:2d} | train_loss {running_loss/len(train_ds):.4f} | test_acc {correct/total:.3f}")