import torch
from torch.utils.data import DataLoader
from fisica import J_def, R_def, g_def, H_def, desired_functions, desired_x
from modelo import HamiltonianNetwork
from datos import ConvertidorDataset

def calcular_perdidas_pinn(batch_x, L, C, r, Vin, v_desired, modelo):
    batch_x.requires_grad_(True)
    
    #predicciones
    H_a, u_hat, R_a = modelo(batch_x)
    H_natural = H_def(batch_x[:, 0], batch_x[:, 1], L, C).view(-1, 1)
    H_d = desired_functions(H_a, H_natural)
    
    R_natural = R_def(r).to(batch_x.device)
    R_d = torch.zeros((batch_x.shape[0], 2, 2), dtype=torch.float32, device=batch_x.device)
    for i in range(batch_x.shape[0]):
        R_d[i] = R_natural.clone()
        R_d[i, 1, 1] += R_a[i, 0]
        
    # gradiente
    grad_Hd = torch.autograd.grad(
        outputs=H_d, inputs=batch_x, grad_outputs=torch.ones_like(H_d), 
        create_graph=True, retain_graph=True
    )[0]
    grad_Hd_vector = grad_Hd.unsqueeze(2)
    
    #matching equation
    J_matrix = J_def().to(batch_x.device)
    f_me_loss = 0
    for i in range(batch_x.shape[0]):
        g_mat = g_def(u_hat[i, 0].item()).unsqueeze(1).to(batch_x.device)
        dinamica = torch.matmul(J_matrix - R_d[i], grad_Hd_vector[i])
        puerto = g_mat * Vin
        residual_i = dinamica + puerto
        f_me_loss += torch.nn.functional.mse_loss(residual_i, torch.zeros_like(residual_i))
    f_me_loss = f_me_loss / batch_x.shape[0]

    #equilibrio
    x_star = desired_x(v_desired, r, L, C).view(1, 2).to(batch_x.device)
    x_star.requires_grad_(True)
    H_a_star, _, _ = modelo(x_star)
    H_nat_star = H_def(x_star[:, 0], x_star[:, 1], L, C).view(-1, 1)
    H_d_star = desired_functions(H_a_star, H_nat_star)

    grad_Hd_star = torch.autograd.grad(
        outputs=H_d_star, inputs=x_star, grad_outputs=torch.ones_like(H_d_star), 
        create_graph=True
    )[0]
    f_eq_loss = torch.nn.functional.mse_loss(grad_Hd_star, torch.zeros_like(grad_Hd_star))
    
    # lyapunov
    hessiana_Hd = torch.autograd.grad(
        outputs=grad_Hd, inputs=batch_x, grad_outputs=torch.ones_like(grad_Hd), 
        create_graph=True
    )[0]
    f_lyap_loss = torch.relu(-hessiana_Hd).mean()

    # estructura
    f_struct_loss = torch.relu(-R_a).mean()

    return f_me_loss + f_eq_loss + f_lyap_loss + f_struct_loss

def main():
    dispositivo = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nIniciando entorno en: {dispositivo}")

    modelo = HamiltonianNetwork().to(dispositivo)
    optimizador = torch.optim.Adam(modelo.parameters(), lr=0.001)

    
    L_val, C_val, r_val = 0.01, 0.001, 5.0
    Vin_val, V_deseado_val = 24.0, 12.0
    epocas = 100





if __name__ == "__main__":
    main()