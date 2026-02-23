import pandas as pd
import sys, os
import ast

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
current_file_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_file_path)   

import numpy as np

from diagonal_defect1 import Diagonal_defect1
from diagonal_defect2 import Diagonal_defect2
from diagonal_defect3 import Diagonal_defect3
from diagonal_defect4 import Diagonal_defect4
from diagonal_defect5 import Diagonal_defect5

version_dict = {
    "v1": Diagonal_defect1,
    "v2": Diagonal_defect2,
    "v3": Diagonal_defect3,
    "v4": Diagonal_defect4,
    "v5": Diagonal_defect5
}

program_name = 'Diagonal'
    
def fully_decompose(qc):
    '''
        thoroughly decompose a qc until only basis gates
    '''
    while True:
        decomposed_qc = qc.decompose()
        if decomposed_qc == qc:
            break
        qc = decomposed_qc
    return qc

def info_collection(num_qubits, program_version):
    '''
        count the gate numbers and depths corresponding to the tested program and print the data
        
        input variables:
        + num_qubits        [int]   the number of qubits involved in the quantum circuit
        + program_version   [str]   the version of the tested program, e.g., 'v1', 'v2'
    '''
    gates_list = []
    depth_list = []

    filename = (
        f"/DO_{program_version}_testSuites_(qubit={num_qubits},"
        f"fr=0.5,#t=50).csv"
    )
    df = pd.read_csv(parent_dir + filename, skiprows=0)

    for test_order in range(len(df)): 
        test_input = df.iloc[test_order] 
        # need to vary with different programs
        num_qubits = test_input.iloc[1]
        initial_state, realDiagPair, imagDiagPair = test_input.iloc[2], test_input.iloc[3], test_input.iloc[4]
        initial_state = ast.literal_eval(initial_state)
        realDiagPair = ast.literal_eval(realDiagPair)
        imagDiagPair= ast.literal_eval(imagDiagPair)
        
        diag_pair_list = realDiagPair.copy()
        for index in range(len(diag_pair_list)):
            diag_pair_list[index] = [complex(realDiagPair[index][0], imagDiagPair[index][0]),
                                    complex(realDiagPair[index][1], imagDiagPair[index][1])]
        
        # calculate kron product
        diag_matrix_array = [np.array(elem) for elem in diag_pair_list]
        temp_matrix = diag_matrix_array[0]
        for diag in diag_matrix_array[1:]:
            temp_matrix = np.kron(temp_matrix, diag)
        diag_matrix = list(temp_matrix)

        # running the quantum programs
        qc = version_dict[program_version](diag_matrix)

        # counts information of quantum circuits
        decomposed_qc = fully_decompose(qc)
        depths = decomposed_qc.depth()
        gates_dict = decomposed_qc.count_ops()
        gates = sum(gates_dict.values())
        gates_list.append(gates)
        depth_list.append(depths)
    
    print(
        f"# gates = [{min(gates_list)}, {max(gates_list)}], "
        f"depth = [{min(depth_list)}, {max(depth_list)}]"
    )
 

if __name__ == "__main__":
    RQ_checks = 'RQ3'      # options: 'RQ1','RQ2','RQ3'

    if RQ_checks in ['RQ1', 'RQ2']:
        num_qubits = 10
        program_versions = ['v1', 'v2', 'v3', 'v4', 'v5']
        for program_version in program_versions:
            print('version = {}, # qubits = {}'.format(program_version, num_qubits))
            info_collection(num_qubits, program_version)
    elif RQ_checks == 'RQ3':
        num_qubits_list = [6, 7, 8, 9, 10, 11, 12]
        program_version = 'v1'
        for num_qubits in num_qubits_list:
            print('version = {}, # qubits = {}'.format(program_version, num_qubits))
            info_collection(num_qubits, program_version)