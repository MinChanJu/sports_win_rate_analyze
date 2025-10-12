import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, in_dim, dropout=0.1, out_dim=2):
        super().__init__()
        self.net = nn.Sequential(
            # Layer 1
            nn.Linear(in_dim, 120),
            nn.BatchNorm1d(120),
            nn.Sigmoid(),
            nn.Dropout(dropout),

            # Layer 2
            nn.Linear(120, 60),
            nn.BatchNorm1d(60),
            nn.Sigmoid(),
            nn.Dropout(dropout),

            # Output Layer
            nn.Linear(60, out_dim),
        )

    def forward(self, x):
        return self.net(x)