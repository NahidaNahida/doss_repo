import os
import sys

"""
This file implemnents the main function for running the object programs
and the test suites for the research questions.

The object programs are imported from their respective directories.
The test suites are implemented in the scripts directory.
"""

name_mapping = {
    "DO":   "Diagonal",
    "IC":   "IntegerComparator",
    "LAF":  "LinearAmplitudeFunction",
    "LPR":  "LinearPauliRotations",
    "QFT":  "QuantumFourierTransform",
    "WA":   "WeightedAdder"
}

# Add the root directory to the system path
root = os.path.dirname(__file__)
sys.path.append(root)
for program in name_mapping.values():
    sys.path.append(os.path.join(root, program))
sys.path.append(os.path.join(root, 'scripts'))

################## ARGUMENT CONFIGURATION ################## 
# The baselines for the object programs
baselines = {
    "opos": ["JSDiv", "CrsEnt", "ExpVal", "DMSQ-JSDiv", "DMSQ-JSDiv", "DMSQ-ExpVal",
             "ChiTest", "KSTest", "MWTest", "DMSQ-ChiTest", "DMSQ-KSTest", "DMSQ-KWTest", "DMSQ-CrsEnt"],
    "woos": ["STFQ", "STSQ", "DOSS"]
}

import Diagonal 
import IntegerComparator  
import LinearAmplitudeFunction  
import LinearPauliRotations  
import QuantumFourierTransform  
import WeightedAdder  

running_dict = {
    "Diagonal": Diagonal,
    "IntegerComparator": IntegerComparator,
    "LinearAmplitudeFunction": LinearAmplitudeFunction,
    "LinearPauliRotations": LinearPauliRotations,
    "QuantumFourierTransform": QuantumFourierTransform,
    "WeightedAdder": WeightedAdder
}

from util.csv_processing import saving_files

def running_exp(
    abb_name, 
    program_version, 
    test_oracle, 
    shots, 
    total_qubits, 
    rq_id, 
    task_id, 
    backend, 
    total_repeats, 
    opo_toler_err, 
    woo_toler_err
):
    program_name = name_mapping[abb_name]
    obj_name = running_dict[program_name]
    for repeat_id in range(total_repeats):
        if test_oracle in baselines["opos"]:
            separation = "DMSQ-" in test_oracle
            
            res_dict, run_time = obj_name.testing_with_statistic(
                program_version, 
                total_qubits, 
                shots, 
                test_oracle,
                separation, 
                rq_id, 
                backend, 
                opo_toler_err
            )
            toler_err = opo_toler_err
        elif test_oracle in baselines["woos"]:
            woo_testing_process = {
                "STFQ": obj_name.testing_with_swap_full,
                "STSQ": obj_name.testing_with_swap_separable,
                "DOSS": obj_name.testing_with_doss
            }
            res_dict, run_time = woo_testing_process[test_oracle](
                program_version,
                total_qubits,
                shots,
                rq_id,
                backend,
                woo_toler_err
            )
            toler_err = woo_toler_err
        else:
            print(test_oracle)
        saving_files(
            rq_id, 
            task_id, 
            program_name, 
            program_version, 
            total_qubits, 
            test_oracle, 
            shots, 
            toler_err, 
            backend, 
            res_dict, 
            run_time
        )
        
        if rq_id != None and task_id != None:       # Replicated
            starter = f'Replication of RQ{rq_id}-{task_id}'
        elif rq_id == None:                         # Custom
            starter = f'Custom mode'
        print(
            f"{starter}: Repeat {repeat_id + 1}/{total_repeats}; Test oracle: {test_oracle}; " 
            f"Program: {program_name}-{program_version}; Qubits: {total_qubits}; Shots: {shots};"
            f"Tolerant error: {toler_err}; Backend: {backend}"
        )