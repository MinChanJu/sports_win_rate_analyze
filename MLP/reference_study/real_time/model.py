import torch.nn as nn

class MLP(nn.Module):
  def __init__(self, in_dim, out_dim=2, layers=[(120, {'batch_norm': True, 'activation': 'sigmoid', 'dropout': 0.1}),
                                                (60, {'batch_norm': True, 'activation': 'sigmoid', 'dropout': 0.1})]):
    super().__init__()
    
    modules = []
    for i in range(len(layers)):
        hidden_dim = layers[i][0]
        params = layers[i][1]

        modules.append(nn.Linear(in_dim, hidden_dim))
        if params.get('batch_norm', False):
            modules.append(nn.BatchNorm1d(hidden_dim))
        if params.get('activation', 'relu') == 'relu':
            modules.append(nn.ReLU())
        elif params.get('activation') == 'sigmoid':
            modules.append(nn.Sigmoid())
        if params.get('dropout', 0.0) > 0.0:
            modules.append(nn.Dropout(params['dropout']))
        in_dim = hidden_dim

    modules.append(nn.Linear(in_dim, out_dim))

    self.net = nn.Sequential(*modules)

  def forward(self, x):
    return self.net(x)