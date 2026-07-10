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

%% Tabla de resultados HDF5

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

%% Simulaciones Creación, paralelización, y extracción
lotes_totales = ceil(N/tamLote);

%Cambio de 1 por el lote 121251 el que se cree que se quedo :P
for k = 121251:tamLote:N
    % Asigna el Rango del lote
    idLote = k:min(k + tamLote - 1, N);
    nSims = numel(idLote);
    numLote = ceil(k/tamLote);
    
    fprintf('\nLote actual %d de %d  |  sims %d a %d\n', numLote, lotes_totales, idLote(1), idLote(end));

    % Genera las simulaciones y asigna los valores de u2av
    simIn(1:nSims) = Simulink.SimulationInput(modelo);
    for j = 1:nSims
        simIn(j) = simIn(j).setVariable('u2av', valores(idLote(j)));
        simIn(j) = simIn(j).setModelParameter('SimulationMode', 'rapid-accelerator');
    end

    % Ejecución de las simulaciones en paralelo
    ticLote = tic;
    simOut = parsim(simIn, 'ShowProgress', 'on');
    tL = toc(ticLote);
    fprintf('Tiempo lote: %.2f s   (%.2f s/sim)\n', tL, tL/nSims);

    % Creaun bloque temporal para el lote
    bloque_lote = zeros(puntos_tomados, 2, nSims, 'single');
    
    for i = 1:nSims
        if isempty(simOut(i).ErrorMessage) && ~isempty(simOut(i).logsout)
            try
                voltaje = simOut(i).logsout.getElement('Voltaje').Values;
                corriente = simOut(i).logsout.getElement('Corriente').Values;

                % Resampleo a saltos de 20 microsegundos
                V_resampleado = interp1(voltaje.Time, voltaje.Data, pasos, 'pchip');
                I_resampleado = interp1(corriente.Time, corriente.Data, pasos, 'pchip');
                
                %guardaen nuestro bloque temporal del lote
                bloque_lote(:, 1, i) = single(V_resampleado(:)); 
                bloque_lote(:, 2, i) = single(I_resampleado(:)); 

            catch ME
                fprintf('Error de extracción en sim %d: %s\n', idLote(i), ME.message);
            end
        else
            fprintf('Error de simulación en sim %d\n', idLote(i));
        end    
    end

    % Empuja el bloque completo al archivo HDF5 
    h5write('simulaciones.h5', '/salidas', bloque_lote, ...
            [1, 1, idLote(1)], ...           
            [puntos_tomados, 2, nSims]);     
            
    fprintf('>> Lote inyectado al archivo HDF5 exitosamente.\n');
end

tTot = toc(tTotal);

fprintf('Dataset HDF5 generado en %.2f segundos (%.2f horas).\n', tTot, tTot/3600);
fprintf('Archivo guardado como: simulaciones.h5\n');