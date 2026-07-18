import torch
import pandas as pd
from torch.utils.data import Dataset

class ConvertidorDataset(Dataset):
    def __init__(self, ruta_archivo):
        self.df = pd.read_hdf(ruta_archivo)
        
        self.x = self.df[['flujo_x1', 'carga_x2']].values

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return torch.tensor(self.x[idx], dtype=torch.float32)