# Import packages included in the environment
from qiskit import QuantumCircuit
import numpy as np
import time
import ast

# Import the specification and buggy versions related to the program
from diagonal_specification import *
from diagonal_defect1 import Diagonal_defect1
from diagonal_defect2 import Diagonal_defect2
from diagonal_defect3 import Diagonal_defect3
from diagonal_defect4 import Diagonal_defect4
from diagonal_defect5 import Diagonal_defect5

program_name = 'Diagonal'
version_dict = {
    'v1': Diagonal_defect1, 
    'v2': Diagonal_defect2,
    'v3': Diagonal_defect3,
    'v4': Diagonal_defect4,
    'v5': Diagonal_defect5
}

# Import the scripts for testing
import sys, os
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root, '..', 'code'))

from util.circuit_execution import *
from util.csv_processing import *
from util.expectation_generation import *
from util.result_processing import *
from util.opo_separation import *
from util.data_conversion import *
from util.oracle_execution import *

# Define the candidate states for single and entangled qubits
# Single-qubit states are |0>, |1>, |+>, |->, and entangled states are Bell states
# |Phi+> = (|00> + |11>)/sqrt(2)
# |Phi-> = (|00> - |11>)/sqrt(2)
# |Psi+> = (|01> + |10>)/sqrt(2)
# |Psi-> = (|01> - |10>)/sqrt(2)
candidate_states = {
    "single": ['|0>', '|1>', '|+>', '|->'],              
    "entangle": ['|Psi+>', '|Psi->', '|Phi+>', '|Phi->']                
}

def DO_state_initialization(qc, initial_state):
    """
        Initialize the quantum circuit based on the initial state.
        
        Args:
            qc (QuantumCircuit): The quantum circuit to be initialized.
            initial_state (list): A list of strings representing the initial state of each qubit or two entangled ones.
                                  Each string can be one of the candidate states.
    """
    temp_index = 0
    for state_str in initial_state[::-1]:
        if state_str in candidate_states['single']:
            # Apply single-qubit gates based on the initial state
            if state_str == '|1>':
                qc.x(temp_index)
            elif state_str == '|+>':
                qc.h(temp_index)
            elif state_str == '|->':
                qc.x(temp_index)
                qc.h(temp_index)
            temp_index += 1
        elif state_str in candidate_states['entangle']:
            # Initialize the Bell states 
            if state_str == '|Phi+>':
                qc.h(temp_index)
                qc.cx(temp_index, temp_index + 1)
            elif state_str == '|Phi->':
                qc.h(temp_index)
                qc.cx(temp_index, temp_index + 1)
                qc.z(temp_index + 1)
            elif state_str == '|Psi+>':
                qc.h(temp_index)
                qc.cx(temp_index, temp_index + 1)
                qc.x(temp_index + 1)
            elif state_str == '|Psi->':
                qc.h(temp_index)
                qc.cx(temp_index, temp_index + 1)
                qc.x(temp_index + 1)
                qc.z(temp_index + 1)
            temp_index += 2

def testing_with_statistic(
    program_version, 
    total_qubits, 
    shots, 
    stat_method, 
    separation, 
    rq_id, 
    backend='Ideal', 
    opo_toler_err=0.05
):
    '''
        Test quantum programs using statistical methods as the test oracle.
        
        Args:
            program_version: [str] the buggy version to be tested, including "v1", "v2", "v3", "v4" and "v5"
            total_qubits:    [int] the total number of qubits in the quantum circuit
            shots:           [int] the number of shots for the quantum circuit execution
            rq_id:           [int] the request ID for reading files
            backend:         [str] the backend to execute the quantum circuit, default is 'Ideal'
            opo_toler_err:   [float] the tolerance error for WOO execution, default is 0.05
            
        Returns:
            res_dict:       [dict] a dictionary containing the results of the test, including true positives, true negatives, false positives, false negatives, and the number of faults
            dur_time:       [float] the duration time of the test process
    '''
    
    # Initialize the result dictionary                     
    res_dict = {"true_pos": 0, 
                "true_neg": 0, 
                "false_pos": 0, 
                "false_neg": 0, 
                "#faults": 0}         
    
    # Read the input parameters from the CSV file
    df = reading_files(program_name, program_version, total_qubits, rq_id)

    # Record the running time
    start_time = time.time()                    
    
    # Iterate through each test case in the DataFrame
    # Each row in the DataFrame contains the input parameters for the quantum circuit       
    for test_order in range(len(df)): 
        test_input = df.iloc[test_order]                   
        _, total_qubits = test_input.iloc[0], test_input.iloc[1]
        initial_state, real_diags, imag_diags = (
            ast.literal_eval(test_input.iloc[2]), 
            ast.literal_eval(test_input.iloc[3]),
            ast.literal_eval(test_input.iloc[4])
        )
        true_result = bool(test_input.iloc[-1])
        
        # Combine the real and imaginary parts
        complex_diags = []
        num_separable_parts = len(real_diags)
        for sep_id in range(num_separable_parts):
            real_diag_part, imag_diag_part = real_diags[sep_id], imag_diags[sep_id]
            num_dim = len(real_diag_part)
            complex_diags.append([
                    complex(real_diag_part[dim_id], imag_diag_part[dim_id]) 
                    for dim_id in range(num_dim)
                ]
            )
        
        # Calculate the kronecker product
        diag_matrix_array = [np.array(elem) for elem in complex_diags]
        for index, diag in enumerate(diag_matrix_array[::-1]):
            if index == 0:
                temp_matrix = np.array(diag)
            else:
                temp_matrix = np.kron(diag, temp_matrix)
        diag_matrix = list(temp_matrix)
        
        qc_initial = QuantumCircuit(total_qubits, total_qubits)
        
        # State initialization
        DO_state_initialization(qc_initial, initial_state)

        # Running the quantum programs
        qc = qc_initial.copy()
        qc_test = version_dict[program_version](diag_matrix)
        qc.append(qc_test, qc.qubits)
        qc.measure(qc.qubits,qc.clbits)

        # Use the backend to execute the quantum circuit    
        dict_counts = measurement_based_backend(qc, shots, backend)

        # Generate expected sample according to the expected probabilities
        exp_state = program_specification_state(
            initial_state, 
            complex_diags
        )

        # Generate the expected output according to the statistical method
        exp_results, opo_type = expected_output_generation(
            stat_method, 
            exp_state, 
            total_qubits, 
            shots
        )
        
        # Convert the dictionary to a list of samples
        test_samps = outputdict2list(dict_counts)

        # Perform the assertion according to the mode
        if separation == False:
            # If separation is False, use the full set of samples
            test_result = opo_execution(
                total_qubits, 
                exp_results, 
                test_samps, 
                stat_method, 
                opo_toler_err
            )
        elif separation == True:
            # If separation is True, use the bitwise separation method
            # Randomly select a qubit to test
            qubit_order = np.random.choice(
                range(total_qubits), 
                size=total_qubits, 
                replace=False
            )

            exp_bitwise_res = output_separation(exp_results, total_qubits, opo_type)
            test_bitwise_samps = output_separation(test_samps, total_qubits, "samps")
            
            # For each qubit, perform the test
            for sel_qubit in qubit_order:
                temp_exp_bitwise_res = exp_bitwise_res[sel_qubit]
                temp_test_bitwise_samps = test_bitwise_samps[sel_qubit]

                test_result = opo_execution(
                    1,
                    temp_exp_bitwise_res,
                    temp_test_bitwise_samps,
                    stat_method,
                    opo_toler_err
                )
                if test_result == False:
                    break
        
        # Update the result dictionary based on the test result
        test_result_updating(test_result, true_result, res_dict)
        
    # Calculate the duration time of the test process
    dur_time = time.time() - start_time            
    return res_dict, dur_time

def testing_with_swap_full(
    program_version, 
    total_qubits, 
    shots, 
    rq_id, 
    backend='Ideal', 
    woo_toler_err=0
):
    """
        Test quantum programs using the swap test without decomposition.
        
        Arg: 
            program_version: [str] the buggy version to be tested, including "v1", "v2", "v3", "v4" and "v5"
            total_qubits:    [int] the total number of qubits in the quantum circuit
            shots:           [int] the number of shots for the quantum circuit execution
            rq_id:           [int] the request ID for reading files
            backend:         [str] the backend to execute the quantum circuit, default is 'Ideal'
            woo_toler_err:   [float] the tolerance error for WOO execution, default is 0
        
        Returns:
            res_dict:       [dict] a dictionary containing the results of the test, including true positives, true negatives, false positives, false negatives, and the number of faults
            dur_time:       [float] the duration time of the test process
    """
    # Initialize the result dictionary
    res_dict = {"true_pos": 0, 
                "true_neg": 0, 
                "false_pos": 0, 
                "false_neg": 0, 
                "#faults": 0}         
    
    # Read the input parameters from the CSV file
    df = reading_files(program_name, program_version, total_qubits, rq_id)

    # Record the running time
    start_time = time.time() 
    
    # Iterate through each test case in the DataFrame
    # Each row in the DataFrame contains the input parameters for the quantum circuit                        
    for test_order in range(len(df)): 
        test_input = df.iloc[test_order]                   
        _, total_qubits = test_input.iloc[0], test_input.iloc[1]
        initial_state, real_diags, imag_diags = (
            ast.literal_eval(test_input.iloc[2]), 
            ast.literal_eval(test_input.iloc[3]),
            ast.literal_eval(test_input.iloc[4])
        )
        true_result = bool(test_input.iloc[-1]) 

        # Combine the real and imaginary parts
        complex_diags = []
        num_separable_parts = len(real_diags)
        for sep_id in range(num_separable_parts):
            real_diag_part, imag_diag_part = real_diags[sep_id], imag_diags[sep_id]
            num_dim = len(real_diag_part)
            complex_diags.append([
                    complex(real_diag_part[dim_id], imag_diag_part[dim_id]) 
                    for dim_id in range(num_dim)
                ]
            )
        
        # Calculate the kronecker product
        diag_matrix_array = [np.array(elem) for elem in complex_diags]
        for index, diag in enumerate(diag_matrix_array[::-1]):
            if index == 0:
                temp_matrix = np.array(diag)
            else:
                temp_matrix = np.kron(diag, temp_matrix)
        diag_matrix = list(temp_matrix)

        qc_initial = QuantumCircuit(2 * total_qubits + 1, 1)

        # State initialization
        DO_state_initialization(qc_initial, initial_state)
        
        # Running the quantum programs
        qc = qc_initial.copy()
        qc_test = version_dict[program_version](diag_matrix)

        # Prepare the expected state
        qc_exp = QuantumCircuit(total_qubits)
        exp_state = program_specification_state(
            initial_state, 
            complex_diags
        )
        qc_exp.initialize(exp_state, qc_exp.qubits)
        qc.append(qc_test, qc.qubits[:total_qubits])
        qc.append(qc_exp, qc.qubits[total_qubits:2*total_qubits])

        # Perform the swap test
        qc.h(-1)
        for i in range(total_qubits):
            qc.cswap(-1, i, i + total_qubits)
        qc.h(-1)
        qc.measure(qc.qubits[-1], qc.clbits)
        
        # Use the backend to execute the quantum circuit              
        dict_counts = measurement_based_backend(qc, shots, backend)
        
        # Execute the WOO method to determine the test result        
        test_result = woo_execution(dict_counts, 0, woo_toler_err)
        
        # Update the result dictionary based on the test result
        test_result_updating(test_result, true_result, res_dict)

    # Calculate the duration time of the test process
    dur_time = time.time() - start_time            
    return res_dict, dur_time

def testing_with_swap_separable(
    program_version, 
    total_qubits, 
    shots, 
    rq_id, 
    backend='Ideal', 
    toler_err=0.05
):    
    '''
        Testing quantum programs using the swap test with separable states.
        
        Args:
            program_version: [str] the buggy version to be tested, including "v1", "v2", "v3", "v4" and "v5"
            total_qubits:    [int] the total number of qubits in the quantum circuit
            shots:           [int] the number of shots for the quantum circuit execution
            rq_id:           [int] the request ID for reading files
            backend:         [str] the backend to execute the quantum circuit, default is 'Ideal'
            woo_toler_err:   [float] the tolerance error for WOO execution, default is 0

        Returns:
            res_dict:       [dict] a dictionary containing the results of the test, including true positives, true negatives, false positives, false negatives, and the number of faults
            dur_time:       [float] the duration time of the test process
    '''

    # Initialize the result dictionary
    res_dict = {"true_pos": 0,
                "true_neg": 0,
                "false_pos": 0,
                "false_neg": 0,
                "#faults": 0}

    # Read the input parameters from the CSV file
    # The CSV file contains the input parameters for the quantum circuit
    df = reading_files(program_name, program_version, total_qubits, rq_id)
    
    # Record the running time
    start_time = time.time()
    
    # Iterate through each test case in the DataFrame
    # Each row in the DataFrame contains the input parameters for the quantum circuit
    for test_order in range(len(df)): 
        test_input = df.iloc[test_order]                   
        _, total_qubits = test_input.iloc[0], test_input.iloc[1]
        initial_state, real_diags, imag_diags = (
            ast.literal_eval(test_input.iloc[2]), 
            ast.literal_eval(test_input.iloc[3]),
            ast.literal_eval(test_input.iloc[4])
        )
        true_result = bool(test_input.iloc[-1])
        
        # Combine the real and imaginary parts
        complex_diags = []
        num_separable_parts = len(real_diags)
        for sep_id in range(num_separable_parts):
            real_diag_part, imag_diag_part = real_diags[sep_id], imag_diags[sep_id]
            num_dim = len(real_diag_part)
            complex_diags.append([
                    complex(real_diag_part[dim_id], imag_diag_part[dim_id]) 
                    for dim_id in range(num_dim)
                ]
            )
        
        # Calculate the kronecker product
        diag_matrix_array = [np.array(elem) for elem in complex_diags]
        for index, diag in enumerate(diag_matrix_array[::-1]):
            if index == 0:
                temp_matrix = np.array(diag)
            else:
                temp_matrix = np.kron(diag, temp_matrix)
        diag_matrix = list(temp_matrix) 

        # Mark the initial state for each qubit
        partition_dict = {}
        qubit_id = 0
        for state_idx, state_str in enumerate(initial_state[::-1]):
            if state_str in candidate_states['single']:
                partition_dict[state_idx] = {
                    "attribute": "single-qubit",
                    "init_state": [state_str],
                    "qubit_ids": [qubit_id],
                    "diag_elem": [complex_diags[-1-state_idx]]
                }
                qubit_id += 1
            elif state_str in candidate_states['entangle']:
                partition_dict[state_idx] = {
                    "attribute": "multi-qubit",
                    "init_state": [state_str],
                    "qubit_ids": [qubit_id, qubit_id + 1],
                    "diag_elem": [complex_diags[-1-state_idx]]   
                }
                qubit_id += 2 
        
        # Select a separable partition to test 
        partition_order = np.random.choice(
            range(num_separable_parts), 
            size=num_separable_parts, 
            replace=False
        )
        
        for sel_part_id in partition_order:          
            # Construct the quantum circuit, where the qubit number depends on the entanglement or non-entanglement
            # of the selected separable partition
            sel_partition = partition_dict[sel_part_id]
            part_att = sel_partition["attribute"]
            sel_qubits = sel_partition["qubit_ids"]
            part_state = sel_partition["init_state"][0]
            sel_diag = sel_partition["diag_elem"][0]
            num_sel_qubits = len(sel_qubits)
            qc_initial = QuantumCircuit(total_qubits + 1 + num_sel_qubits, 1)
        
            # State initialization
            DO_state_initialization(qc_initial, initial_state)

            # Running the quantum programs
            qc = qc_initial.copy()
            qc_test = version_dict[program_version](diag_matrix)
            qc.append(qc_test, qc.qubits[:total_qubits])
            
            # If the selected partition includes one qubits, we then utilize the two angles for reference state preparation
            if part_att == "single-qubit":
                sel_qubit = sel_qubits[0]
                beta, theta = program_specification_angles(
                    part_state,
                    sel_diag
                )
                
                # Specification state initialization
                qc.ry(theta, total_qubits)
                qc.rz(beta, total_qubits)

                # Perform the swap test
                qc.h(-1)
                qc.cswap(-1, sel_qubit, total_qubits)
                qc.h(-1)
         
            # If the selected partition encompasses more than one, we then attempt the statevector for its simplicity.
            elif part_att == "multi-qubit":
                exp_state = program_specification_state(
                    [part_state],
                    [sel_diag]
                )
                
                # Specification state initialization
                qc.initialize(
                    exp_state, 
                    qc.qubits[total_qubits: total_qubits + num_sel_qubits]
                )
                
                # Perform the swap test
                qc.h(-1)
                for ref_qubit_id, sel_qubit_id in enumerate(sel_qubits):
                    qc.cswap(-1, sel_qubit_id, total_qubits + ref_qubit_id)
                qc.h(-1)

            # Measure the output qubits
            qc.measure(qc.qubits[-1], qc.clbits)

            # Use the backend to execute the quantum circuit
            dict_counts = measurement_based_backend(qc, shots, backend)
            
            # Execute the WOO method to determine the test result
            test_result = woo_execution(dict_counts, 0, toler_err)
            
            # If the test result fails, break the loop
            if test_result == False:
                break
        
        # Update the result dictionary based on the test result
        test_result_updating(test_result, true_result, res_dict)
    
    # Calculate the duration time of the test process
    dur_time = time.time() - start_time            
    return res_dict, dur_time

def testing_with_doss(
    program_version, 
    total_qubits, 
    shots, 
    rq_id, 
    backend='Ideal', 
    woo_toler_err=0.05
):
    '''
        This function implements the test process using DOSS (Dynamic Oracle via Separable States) which is a WOO method.
        
        Args:
            program_version: [str] the buggy version to be tested, including "v1", "v2", "v3", "v4" and "v5"
            total_qubits:    [int] the total number of qubits in the quantum circuit
            shots:           [int] the number of shots for the quantum circuit execution
            rq_id:           [int] the request ID for reading files
            backend:         [str] the backend to execute the quantum circuit, default is 'Ideal'
            woo_toler_err:   [float] the tolerance error for WOO execution, default is 0
            
        Returns:
            res_dict:       [dict] a dictionary containing the results of the test, including true positives, true negatives, false positives, false negatives, and the number of faults
            dur_time:       [float] the duration time of the test process
    '''
    
    # Initialize the result dictionary
    res_dict = {"true_pos": 0, 
                "true_neg": 0, 
                "false_pos": 0, 
                "false_neg": 0, 
                "#faults": 0}         
    
    # Read the input parameters from the CSV file
    df = reading_files(program_name, program_version, total_qubits, rq_id)
 
    # Record the running time
    start_time = time.time()
    
    # Iterate through each test case in the DataFrame
    # Each row in the DataFrame contains the input parameters for the quantum circuit          
    for test_order in range(len(df)): 
        test_input = df.iloc[test_order]                   
        _, total_qubits = test_input.iloc[0], test_input.iloc[1]
        initial_state, real_diags, imag_diags = (
            ast.literal_eval(test_input.iloc[2]), 
            ast.literal_eval(test_input.iloc[3]),
            ast.literal_eval(test_input.iloc[4])
        )
        true_result = bool(test_input.iloc[-1]) 
        
        # Combine the real and imaginary parts
        complex_diags = []
        num_separable_parts = len(real_diags)
        for sep_id in range(num_separable_parts):
            real_diag_part, imag_diag_part = real_diags[sep_id], imag_diags[sep_id]
            num_dim = len(real_diag_part)
            complex_diags.append([
                    complex(real_diag_part[dim_id], imag_diag_part[dim_id]) 
                    for dim_id in range(num_dim)
                ]
            )
        
        # Calculate the kronecker product
        diag_matrix_array = [np.array(elem) for elem in complex_diags]
        for index, diag in enumerate(diag_matrix_array[::-1]):
            if index == 0:
                temp_matrix = np.array(diag)
            else:
                temp_matrix = np.kron(diag, temp_matrix)
        diag_matrix = list(temp_matrix)
        
        # Form the partitions, and note that we attribute classical states to one partitions
        partition_dict = {}
        qubit_id, num_partitions = 0, 0
        for state_idx, state_str in enumerate(initial_state[::-1]):
            if state_str in ["|0>", "|1>"]:           # Computational basis states
                if_exist_basis = False
                # Traverse for the possible existing partition for basis states
                for partition in partition_dict.values():
                    if partition["attribute"] == "basis":
                        if_exist_basis = True
                        partition["qubit_ids"].append(qubit_id)
                        partition["init_state"].append(state_str)
                        partition["diag_elem"].append(complex_diags[-1-state_idx])
                        break
                # Create a new partition for basis states
                if not if_exist_basis:
                    partition_dict[num_partitions] = {
                        "attribute": "basis",
                        "init_state": [state_str],
                        "qubit_ids": [qubit_id],
                        "diag_elem": [complex_diags[-1-state_idx]]
                    }
                    num_partitions += 1   # Because of adding a new partition
                qubit_id += 1           # Because of assigning a qubit
            elif state_str in ["|+>", "|->"]:         # Superposition states
                # Need another partition for this qubit
                partition_dict[num_partitions] = {
                    "attribute": "superposition",
                    "init_state": [state_str],
                    "qubit_ids": [qubit_id],
                    "diag_elem": [complex_diags[-1-state_idx]]
                }
                num_partitions += 1       # Because of adding a new partition
                qubit_id += 1           # Because of assigning a qubit
            elif state_str in candidate_states["entangle"]:   # Entangled states
                # Need another partition for the two qubits
                partition_dict[num_partitions] = {
                    "attribute": "entanglement",
                    "init_state": [state_str],
                    "qubit_ids": [qubit_id, qubit_id + 1],
                    "diag_elem": [complex_diags[-1-state_idx]]
                }
                num_partitions += 1       # Because of adding a new partition
                qubit_id += 2           # Because of assigning two qubits                
        
        # Select a separable partition to test 
        partition_order = np.random.choice(
            range(num_partitions),
            size=num_partitions,
            replace=False
        )    
        
        # Determine the quantum subroutine for testing
        qc_test = version_dict[program_version](diag_matrix)
        
        for sel_part_id in partition_order:
            sel_partition = partition_dict[sel_part_id]
            part_att = sel_partition["attribute"]
            num_sel_qubits = len(sel_partition["qubit_ids"])
            if part_att == "basis":     # Adopt direct measurement
                qc = QuantumCircuit(total_qubits, num_sel_qubits)
                
                # State initialization
                DO_state_initialization(qc, initial_state)
        
                # Running the tested program
                qc.append(qc_test, qc.qubits[:total_qubits])
                
                # Measure the output qubits
                exp_bina_list = []
                part_qubits = sel_partition["qubit_ids"]
                part_states = sel_partition["init_state"]
                for temp_id, qubit_id in enumerate(part_qubits):
                    qc.measure(qubit_id, qc.clbits[temp_id])    # From low to high
                    temp_bina = int(part_states[temp_id][1])    # Extract from "|0>" or "|1>"
                    exp_bina_list.insert(0, temp_bina)
                    
                # Convert to binary number
                exp_bina_str = ''.join(map(str, exp_bina_list))
                exp_number = int(exp_bina_str, 2)
                
            elif part_att == "superposition":     # Adopt
                sel_qubit = sel_partition["qubit_ids"][0]
                part_state = sel_partition["init_state"][0]
                sel_diag = sel_partition["diag_elem"][0]

                # ######## DEBUG ##########
                # import pdb; pdb.set_trace() 

                beta, theta = program_specification_angles(
                    part_state,         # The initial state for this superposition
                    sel_diag            # The diagonal elements with complex values
                )

                qc = QuantumCircuit(total_qubits + 1 + num_sel_qubits, 1)

                # State initialization
                DO_state_initialization(qc, initial_state)
        
                # Running the tested program
                qc.append(qc_test, qc.qubits[:total_qubits])

                # Specification state initialization
                qc.ry(theta, total_qubits)
                qc.rz(beta, total_qubits)

                # Perform the swap test
                qc.h(-1)
                qc.cswap(-1, sel_qubit, total_qubits)
                qc.h(-1)

                # Measure the output qubits
                qc.measure(qc.qubits[-1], qc.clbits)
                
                exp_number = 0
            elif part_att == "entanglement":
                exp_state = program_specification_state(
                    sel_partition["init_state"],
                    sel_partition["diag_elem"]
                )

                qc = QuantumCircuit(total_qubits + 1 + num_sel_qubits, 1)

                # State initialization
                DO_state_initialization(qc, initial_state)
        
                # Running the tested program
                qc.append(qc_test, qc.qubits[:total_qubits])

                # Specification state initialization
                qc.initialize(
                    exp_state, 
                    qc.qubits[total_qubits: total_qubits + num_sel_qubits]
                )                
                
                # Perform the swap test
                sel_qubits = sel_partition["qubit_ids"]
                qc.h(-1)
                for ref_qubit_id, sel_qubit_id in enumerate(sel_qubits):
                    qc.cswap(-1, sel_qubit_id, total_qubits + ref_qubit_id)
                qc.h(-1)

                # Measure the output qubits
                qc.measure(qc.qubits[-1], qc.clbits)

                exp_number = 0
                
            # Use the backend to execute the quantum circuit              
            dict_counts = measurement_based_backend(qc, shots, backend)
    
            # Execute the WOO method to determine the test result        
            test_result = woo_execution(dict_counts, exp_number, woo_toler_err)     
        
            # If the test result fails, break the loop
            if test_result == False:
                break
        
        # print(test_result, true_result, dict_counts, exp_number)

        # Update the result dictionary based on the test result
        test_result_updating(test_result, true_result, res_dict)
        
    # Calculate the duration time of the test process
    dur_time = time.time() - start_time            
    return res_dict, dur_time