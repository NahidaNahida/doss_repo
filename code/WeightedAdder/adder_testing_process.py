# Import packages included in the environment
from qiskit import QuantumCircuit
import numpy as np
import time

from adder_specification import *
from adder_defect1 import WeightedAdder_defect1
from adder_defect2 import WeightedAdder_defect2
from adder_defect3 import WeightedAdder_defect3
from adder_defect4 import WeightedAdder_defect4
from adder_defect5 import WeightedAdder_defect5

program_name = 'WeightedAdder'
version_dict = {
    'v1': WeightedAdder_defect1, 
    'v2': WeightedAdder_defect2,
    'v3': WeightedAdder_defect3,
    'v4': WeightedAdder_defect4,
    'v5': WeightedAdder_defect5
}

# Import the scripts for testing
import sys, os
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root, '..', 'code'))

import ast

from util.circuit_execution import *
from util.csv_processing import *
from util.expectation_generation import *
from util.result_processing import *
from util.opo_separation import *
from util.data_conversion import *
from util.oracle_execution import *

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
        input_qubits, total_qubits = test_input.iloc[0], test_input.iloc[1]
        number, weight = test_input.iloc[2], ast.literal_eval(test_input.iloc[3])
        true_result = bool(test_input.iloc[-1]) 
        str_number = bin(number)[2:]
        str_number = str_number.zfill(input_qubits)   
        initial_state = [int(bit) for bit in str_number]
        
        qc_initial = QuantumCircuit(total_qubits, total_qubits)
        
        # State initialization
        # The initial state is a binary string, where 1 indicates the qubit is in the |1> state
        # and 0 indicates the qubit is in the |0> state.
        for index, val in enumerate(initial_state[::-1]):
            if val == 1:
                qc_initial.x(index)

        # Running the quantum programs
        qc = qc_initial.copy()
        qc_test = version_dict[program_version](input_qubits, weight)
        qc.append(qc_test, qc.qubits)
        qc.measure(qc.qubits,qc.clbits)

        # Use the backend to execute the quantum circuit    
        dict_counts = measurement_based_backend(qc, shots, backend)

        # Generate expected sample according to the expected probabilities
        exp_state = program_specification_state(
            input_qubits,
            total_qubits, 
            number, 
            weight
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
        input_qubits, total_qubits = test_input.iloc[0], test_input.iloc[1]
        number, weight = test_input.iloc[2], ast.literal_eval(test_input.iloc[3])
        true_result = bool(test_input.iloc[-1]) 
        str_number = bin(number)[2:]
        str_number = str_number.zfill(input_qubits)   
        initial_state = [int(bit) for bit in str_number]

        qc_initial = QuantumCircuit(2 * total_qubits + 1, 1)

        # State initialization
        # The initial state is a binary string, where 1 indicates the qubit is in the |1> state
        # and 0 indicates the qubit is in the |0> state.
        for index, val in enumerate(initial_state[::-1]):
            if val == 1:
                qc_initial.x(index)
                                            
        # Running the quantum programs
        qc = qc_initial.copy()
        qc_test = version_dict[program_version](input_qubits, weight)

        # Prepare the expected state
        qc_exp = QuantumCircuit(total_qubits)
        exp_state = program_specification_state(
            input_qubits,
            total_qubits, 
            number, 
            weight
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
        input_qubits, total_qubits = test_input.iloc[0], test_input.iloc[1]
        number, weight = test_input.iloc[2], ast.literal_eval(test_input.iloc[3]) 
        true_result = bool(test_input.iloc[-1]) 
        str_number = bin(number)[2:]
        str_number = str_number.zfill(input_qubits)   
        initial_state = [int(bit) for bit in str_number]

        qc_initial = QuantumCircuit(total_qubits + 2, 1)
        
        # State initialization
        # The initial state is a binary string, where 1 indicates the qubit is in the |1> state
        # and 0 indicates the qubit is in the |0> state.
        for index, val in enumerate(initial_state[::-1]):
            if val == 1:
                qc_initial.x(index)
        
        # Select a qubit to test 
        qubit_order = np.random.choice(
            range(total_qubits), 
            size=total_qubits, 
            replace=False
        )
        for sel_qubit in qubit_order:                          
            # Running the quantum programs
            qc = qc_initial.copy()
            qc_test = version_dict[program_version](input_qubits, weight)
            qc.append(qc_test, qc.qubits[:total_qubits])
            beta, theta = program_specification_angles(
                sel_qubit, 
                input_qubits,
                total_qubits, 
                number, 
                weight
            )
            
            # Specification state initialization
            qc.ry(theta, total_qubits)
            qc.rz(beta, total_qubits)

            # Perform the swap test
            qc.h(-1)
            qc.cswap(-1, sel_qubit, total_qubits)
            qc.h(-1)
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
        input_qubits, total_qubits = test_input.iloc[0], test_input.iloc[1]
        number, weight = test_input.iloc[2], ast.literal_eval(test_input.iloc[3])
        true_result = bool(test_input.iloc[-1]) 
        str_number = bin(number)[2:]
        str_number = str_number.zfill(input_qubits)   
        initial_state = [int(bit) for bit in str_number]
        
        # Form only on partition
        qc_initial = QuantumCircuit(total_qubits, total_qubits)
        for index, val in enumerate(initial_state[::-1]):
            if val == 1:
                qc_initial.x(index)
            
        # Running the quantum programs
        qc = qc_initial.copy()
        # Need to vary with different programs
        qc_test = version_dict[program_version](input_qubits, weight)
        qc.append(qc_test, qc.qubits)
        qc.measure(qc.qubits, qc.clbits)
        
        # Use the backend to execute the quantum circuit
        dict_counts = measurement_based_backend(qc, shots, backend)
        
        # Generate the expected value
        expected_val = program_specification_value(input_qubits, total_qubits, number, weight)
        
        # Execute the WOO method to determine the test result
        test_result = woo_execution(dict_counts, expected_val, woo_toler_err)
        
        # Update the result dictionary based on the test result
        test_result_updating(test_result, true_result, res_dict)
        
        # print(expected_val, dict_counts, test_result, true_result)
    # Calculate the duration time of the test process
    dur_time = time.time() - start_time            
    return res_dict, dur_time