clear; clc;

modelo    = 'Circuito_SM_I';
set_param(modelo, 'ReturnWorkspaceOutputs', 'on');
set_param(modelo, 'SignalLogging', 'on');
N         = 125000;     
tamLote   = 1250;
nWorkers  = 8;
tiempo_total = 0.1;
saltos = 20e-6; % 20 microsegundos confirmado 🦐

% Empezamos en 0 y avanzamos en saltos hasta llegar al tiempo total
pasos = (0:saltos:tiempo_total)';                

%% Tabla para los datos 
muestras = 2/(N-1);
valores  = 1 - (0:N-1)' * muestras;  
puntos_tomados = length(pasos);
valores_constantes = nan(N, 2);

valores_constantes(:,1) = (1:N)';
valores_constantes(:,2) = valores;

%% Look-Up 4 Sim Err, buscaremos las simulaciones que tienen errores, es decir 0 en la posición (i,1,2) del H5 

simErr = [];
pos = 1;

for i = 1:N
    p_err = h5read('simulaciones.h5','/salidas', [2,1,i],[1,1,1]);
    if p_err == 0
        simErr(pos) = i;    
        pos = pos + 1;
    end
    
end

errN = length(simErr);

%% Creación de los workers
% Solo crea los workers con la cantidad de nworkers asignada
p = gcp('nocreate');
if isempty(p)
    p = parpool(nWorkers);
elseif p.NumWorkers < nWorkers
    delete(p); p = parpool(nWorkers);
end
fprintf('Workers: %d\n', p.NumWorkers);

tTotal = tic;

%% Simulando las Simulaciones que tuvieron errores



% Genera las simulaciones y asigna los valores de u2av
simIn(1:errN) = Simulink.SimulationInput(modelo);
for j = 1:errN
    simIn(j) = simIn(j).setVariable('u2av', valores(simErr(j)));
    simIn(j) = simIn(j).setModelParameter('SimulationMode', 'rapid-accelerator');
end

% Ejecución de las simulaciones en paralelo
ticLote = tic;
simOut = parsim(simIn, 'ShowProgress', 'on');
tL = toc(ticLote)

% Crea un bloque temporal para el lote
    
for i = 1:errN
bloque_lote = zeros(puntos_tomados, 2, 'single');
    
    if isempty(simOut(i).ErrorMessage) && ~isempty(simOut(i).logsout)
        try

            voltaje = simOut(i).logsout.getElement('Voltaje').Values;
            corriente = simOut(i).logsout.getElement('Corriente').Values;

            % Resampleo a saltos de 20 microsegundos
            V_resampleado = interp1(voltaje.Time, voltaje.Data, pasos, 'pchip');
            I_resampleado = interp1(corriente.Time, corriente.Data, pasos, 'pchip');
                
            %guarda en nuestro bloque temporal del lote
            bloque_lote(:, 1) = single(V_resampleado(:)); 
            bloque_lote(:, 2) = single(I_resampleado(:)); 

            % Añadimos los datos que faltan al DataSet 
            h5write('simulaciones.h5', '/salidas', bloque_lote, ...
            [1, 1, simErr(i)], ...           
            [puntos_tomados, 2, 1]); 

        catch ME
                fprintf('Error de extracción en sim %d: %s\n', simErr(i), ME.message);
        end
    else
            fprintf('Error de simulación en sim %d\n', simErr(i));
    end    
end

disp('Se logro cawn')
tTot = toc(tTotal);

