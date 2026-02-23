import math
import numpy as np

def program_specification_angles(sel_qubit, input_qubits, number, L, sign):
    '''
        return theta for Ry gate
    '''
    strNumber = bin(number)[2:]
    strNumber = strNumber.zfill(input_qubits)
    initial_state = [int(bit) for bit in strNumber]
    revInitialState = initial_state[::-1]
    
    if sel_qubit < input_qubits:      # |x>
        qubitVal = revInitialState[sel_qubit]
        theta = 0 if qubitVal == 0 else math.pi
    else:                         # |q>n>
        if sign == True:
            zeroVal = int(number >= L)
        else:
            zeroVal = int(number < L)
        if sel_qubit == input_qubits:
            theta = 0 if zeroVal == 0 else math.pi
        else:
            theta = 0
    beta = 0
    return beta, theta

def program_specification_value(input_qubits, number, L, sign):
    '''
        return the expected value
    '''
    if sign == True:
        high = int(number >= L)
    else:
        high = int(number < L)
    value = number + high * (2 ** input_qubits)
    return value

def program_specification_state(input_qubits, total_qubits, number, L, sign):
    '''
        return the expected state
    '''
    value = program_specification_value(input_qubits, number, L, sign)
    exp_state = [0] * (2 ** (total_qubits))
    exp_state[value] = 1
    return exp_state