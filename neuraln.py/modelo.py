import torch
from torch import nn

class HamiltonianNetwork(nn.Module):
    def __init__(self, in_data=2, out_data=3, layers=64):
        super().__init__() 
        self.HNN = nn.Sequential(
            nn.Linear(in_data, layers),
            nn.Tanh(),
            nn.Linear(layers, layers),
            nn.Tanh(),
            nn.Linear(layers, layers),
            nn.Tanh(),
            nn.Linear(layers, out_data)
        )
    
    def forward(self, x):
        data_a = self.HNN(x)
        

        H_a = data_a[:, 0].view(-1, 1)
        u_a = data_a[:, 1].view(-1, 1)
        R_a = data_a[:, 2].view(-1, 1)
        
        return H_a, u_a, R_a