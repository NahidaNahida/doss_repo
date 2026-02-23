import math, cmath
import numpy as np

# Define the candidate statevectors for Diagonal
candidate_statevectors = {
    "|0>": [1, 0],
    "|1>": [0, 1],
    "|+>": [1 / math.sqrt(2), 1 / math.sqrt(2)],
    "|->": [1 / math.sqrt(2), -1 / math.sqrt(2)],
    "|Phi+>": [1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)],
    "|Phi->": [1 / math.sqrt(2), 0, 0, -1 / math.sqrt(2)], 
    "|Psi+>": [0, 1 / math.sqrt(2), 1 / math.sqrt(2), 0],
    "|Psi->": [0, 1 / math.sqrt(2), -1 / math.sqrt(2), 0]                         
}

def program_specification_angles(init_state, diag_operation):
    '''
        This function is for the single-qubit output only
        return theta for Ry gate, beta for Rz gate
    '''
    init_statevector = candidate_statevectors[init_state]
    exp_statevector = [
        init_statevector[0] * diag_operation[0],
        init_statevector[1] * diag_operation[1]
    ]
    beta = cmath.phase(exp_statevector[1]) - cmath.phase(exp_statevector[0])
    theta = 2 * math.acos(abs(exp_statevector[0]))
    return beta, theta

def program_specification_state(initial_state, complex_diags):
    num_separable_parts = len(initial_state)
    for sep_id in range(num_separable_parts):
        init_stat_str = initial_state[-1 - sep_id]
        diag_operation = complex_diags[-1 - sep_id] 
        init_statevector = candidate_statevectors[init_stat_str]
        num_dim = len(init_statevector)
        temp_statevector = [
            init_statevector[dim_id] * diag_operation[dim_id]
            for dim_id in range(num_dim)
        ]
        if sep_id == 0:
            final_statevector = np.array(temp_statevector)
        else:
            final_statevector = np.kron(temp_statevector, final_statevector)
    return final_statevector
