import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchcision import datasets, transforms

def J_def():
    return torch.tensor([[0.0, -1.0],[1.0, 0.0]], dtype=torch.float32)

def R_def(r):
    return torch.tensor([[0.0, 0.0],[0.0, 1.0/r]], dtype=torch.float32)

def g_def(u):
    return torch.tensor([[u, 0.0]], dtype=torch.float32)

def H_def(x1, x2, l, c):
    return ((1 / (2 * l)) * (x1**2) + (1 / (2 * c)) * (x2**2))

def desired_functions(w, x):
    return w + x

def partial_derivate_H(l,c,x1,x2):
    return torch.tensor([[x1,l][x2/c]], dtype=torch.float32)
    
def desired_x(v_desired,r,l,c):
    return torch.tensor([[(l/r)*v_desired][c*v_desired]])

def desired_u(v_in,v_desired):
    return v_desired/v_in

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

modelo = HamiltonianNetwork()

print(modelo)