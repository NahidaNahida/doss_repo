import math, cmath
import numpy as np

def program_specification_angles(sel_qubit, input_qubits, number, slop, offset):
    '''
        return theta for Ry gate
    '''
    strNumber = bin(number)[2:]
    strNumber = strNumber.zfill(input_qubits)
    initial_state = [int(bit) for bit in strNumber]
    revInitialState = initial_state[::-1]
    
    if sel_qubit < input_qubits:      # |x>
        qubitVal = revInitialState[sel_qubit]
        if qubitVal == 0:
            theta = 0
        elif qubitVal == 1:
            theta = math.pi
    else:                           # [cos(aq+b)/2, sin(aq+b)/2]
        a, b = slop / 2, offset / 2
        theta = (a * number + b) * 2 
    
    beta = 0
    return beta, theta

def program_specification_state(input_qubits, number, slop, offset):
    '''
        return the state vector
    '''
    in_vec = [0] * (2 ** input_qubits)
    in_vec[number] = 1
    
    a, b = slop / 2, offset / 2
    theta = a * number + b
    res_vec = [math.cos(theta), math.sin(theta)] 
    final_state = np.kron(np.array(res_vec), np.array(in_vec))
    return final_state