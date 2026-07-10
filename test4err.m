N = 125000
pos =  1;
simErr = [];

for i = 1:N
    p_err = h5read('simulaciones.h5','/salidas', [2,1,i],[1,1,1]);
    if p_err == 0
        simErr(pos) = i;    
        pos = pos + 1;
    end
    
end

data_size = length(simErr)