import h5py
import pandas as pd
import matplotlib.pyplot as plt
with h5py.File("simulaciones.h5","r") as f:

    def mostrar(nombre,objeto):
        print(nombre)

    f.visititems(mostrar)
    
    vc  = f['/salidas'][:,0]
    ic  = f['/salidas'][:,1]
    
    vc_start = vc[:,1]
    ic_start = ic[:,1]
    
    vc_end = vc[:,-1]
    ic_end = ic[:,-1]
    
    print('Valores vc\n')
    print(len(vc))
    print(vc)
    
    
    print('Valores ic\n')
    print(len(ic))
    print(ic)
    
    print('Valores iniciales de todas las simulaciones\n')
    
    print(vc_start)
    print(ic_start)
    
    print('\nValores finales de todas las simulaciones\n')
    
    print(vc_end)
    print(ic_end)
    

data = {
    'ic final': ic_end,
    'vc final': vc_end
}

df = pd.DataFrame(data)

print(df)

    