import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, in_dim, dropout=0.1, out_dim=2):
        super().__init__()
        self.net = nn.Sequential(
            # Layer 1
            nn.Linear(in_dim, 512),
            nn.BatchNorm1d(512),
            nn.SiLU(),
            nn.Dropout(dropout),

            # Layer 2
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.SiLU(),
            nn.Dropout(dropout),

            # Layer 3
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),

            # Layer 4
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.SiLU(),
            nn.Dropout(dropout),

            # Layer 5
            nn.Linear(64, 64),
            nn.LayerNorm(64),          # BatchNorm 대신 LayerNorm 한 번 사용
            nn.GELU(),                 # 다른 활성함수로 다양화
            nn.Dropout(dropout),

            # Layer 6
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout / 2),

            # Output Layer
            nn.Linear(32, out_dim),
        )

    def forward(self, x):
        return self.net(x)