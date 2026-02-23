import math, cmath
import numpy as np

def program_specification_angles(sel_qubit, input_qubits, total_qubits, number, weight):
    '''
        return theta for Ry gate
    '''
    str_number = bin(number)[2:]
    str_number = str_number.zfill(input_qubits)
    initial_state = [int(bit) for bit in str_number]
    rev_initial_state = initial_state[::-1]
    
    if sel_qubit < input_qubits:      # |x>
        qubit_val = rev_initial_state[sel_qubit]
        if qubit_val == 0:
            theta = 0
        elif qubit_val == 1:
            theta = math.pi
    else:                           # [cos(aq+b)/2, sin(aq+b)/2]
        exp_res = 0
        s = total_qubits - input_qubits
        for i in range(input_qubits):
            exp_res += rev_initial_state[i] * weight[i]
        str_exp_res = bin(int(exp_res))[2:]
        str_exp_res = str_exp_res.zfill(s)
        outState = [int(bit) for bit in str_exp_res]
        revOutState = outState[::-1]
        
        outIndex = sel_qubit - input_qubits
        theta = 0 if revOutState[outIndex] == 0 else math.pi

    beta = 0    
    return beta, theta

def program_specification_state(input_qubits, total_qubits, number, weight):
    '''
        return the state vector
    '''
    inVec = [0] * (2 ** input_qubits)
    inVec[number] = 1
    
    str_number = bin(number)[2:]
    str_number = str_number.zfill(input_qubits)
    initial_state = [int(bit) for bit in str_number]
    rev_initial_state = initial_state[::-1]
    
    s = total_qubits - input_qubits
    outVec = [0] * (2 ** s)
    exp_res = 0
    for i in range(input_qubits):
        exp_res += rev_initial_state[i] * weight[i]      
    outVec[exp_res] = 1
    
    final_state = np.kron(np.array(outVec), np.array(inVec))
    return final_state


def program_specification_value(input_qubits, total_qubits, number, weight):
    '''
        return theta for Ry gate
    '''
    # initial state = [1, 0] means (01)b = 1
    s = total_qubits - input_qubits
    str_number = bin(number)[2:]
    str_number = str_number.zfill(input_qubits)
    initial_state = [int(bit) for bit in str_number]
    rev_initial_state = initial_state[::-1]
    exp_res = 0
    for i in range(input_qubits):
        exp_res += rev_initial_state[i] * weight[i]
    str_exp_res = bin(int(exp_res))[2:]
    str_exp_res = str_exp_res.zfill(s)
    str_exp_res = str_exp_res[::-1]
    value = number
    for ind, bit in enumerate(str_exp_res):
        value += int(bit) * (2 ** (input_qubits + ind))
    return value

