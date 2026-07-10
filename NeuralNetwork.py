import os
import torch 
import numpy as np
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Definmos H(x),J(x,u),R,g(u)

#Estructura de condición de preservación, sera constante
def J_def():
    return [[0,-1],[1,0]]

def R_def(r):
    return [[0,0],[0,1/r]]

def g_def(u):
    return [[u,0]]

def H_def(ic,vc,l,c):
    return ((1/2*l)*np.pow(ic)+(1/2*c)*np.pow(vc) )

def desire_functions(w,x):
    return w+x
    
    

class HamiltonianNetwork(nn.Module):
    def __init__(self,in_data=2,out_data=3,layers=64):
        super().__init__() 
        self.HNN = nn.Sequential(
            nn.Linear(in_data,layers),
            nn.Tanh(),
            nn.Linear(layers,layers),
            nn.Tanh(),
            nn.Linear(layers,layers),
            nn.Tanh(),
            nn.Linear(layers,out_data)
        )
    
    def forward(self,x):
        data_a = self.HNN(x)
        H_a = data_a[:,0]
        u_a = data_a[:,1]
        R_a = data_a[:,2]
        
        return H_a,u_a,R_a

modelo = HamiltonianNetwork()

print(modelo)