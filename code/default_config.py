import itertools
from experiments import running_exp

"""
Default configurations for the research questions
Each function corresponds to a specific research question and its subtasks.
The functions set the parameters and call the `running_exp` function to execute the experiments.   
"""

# The object programs are used for each RQ
abb_programs = ['IC', 'LAF', 'LPR', 'QFT', 'WA', 'DO']
# abb_programs = ['IC', 'LAF', 'LPR', 'WA', 'DO']

def default_config_RQ1(task_id):
    ##################################### PARAMETERS #####################################
    # program_versions = ['v1', 'v2', 'v3', 'v4', 'v5']
    program_versions = ['v2', 'v3', 'v4', 'v5']
    total_qubits = 10
    total_repeats = 20
    backend = 'Ideal'    
    woo_toler_err = 0
    shots_dict = {
        "DO":   range(5, 201, 5),
        "IC":   range(2, 51, 2),    # This program is expected to output a deterministic result
        "LAF":  range(5, 201, 5),
        "LPR":  range(5, 201, 5),
        "QFT":  range(5, 201, 5),
        "WA":   range(2, 51, 2),    # This program is expected to output a deterministic result
    }
    ######################################################################################

    print(
        f"\n" 
        f"RQ1 subtask{task_id} with the default configuration" 
        f"\n"
    )
    
    if task_id == 1:
        # In this task, we try SDMs with a fixed threshold, and the varied shots
        # baselines = ["MWTest", "ChiTest", "KSTest", "CrsEnt", "JSDiv", "ExpVal", "DOSS"]
        baselines = ["MWTest", "ChiTest", "KSTest", "CrsEnt", "JSDiv", "ExpVal"]
        opo_toler_err = 0.05
        # Generate all the combinations
        combined_variables = list(itertools.product(
            abb_programs, 
            program_versions, 
            baselines
            )
        )
        for abb_name, program_version, test_oracle in combined_variables:
            shots_list = shots_dict[abb_name]
            for shots in shots_list:
                running_exp(
                    abb_name,
                    program_version,
                    test_oracle,
                    shots,
                    total_qubits,
                    1,
                    task_id,
                    backend,
                    total_repeats,
                    opo_toler_err,
                    woo_toler_err
                )
    elif task_id == 2:
        # In this task, we zoom into SDMs with varied thresholds
        involved_programs = ["LPR", "LAF"]
        baselines = ["CrsEnt", "JSDiv"]
        opo_toler_errs = [0.01, 0.02, 0.1, 0.2, 0.5]
        # Generate all the combinations
        combined_variables = list(itertools.product(
            involved_programs, 
            program_versions, 
            baselines,
            opo_toler_errs
            )
        )
        for abb_name, program_version, test_oracle, opo_toler_err in combined_variables:
            shots_list = shots_dict[abb_name]
            for shots in shots_list:
                running_exp(
                    abb_name,
                    program_version,
                    test_oracle,
                    shots,
                    total_qubits,
                    1,
                    task_id,
                    backend,
                    total_repeats,
                    opo_toler_err,
                    woo_toler_err
                )
        
def default_config_RQ2(task_id):
    ##################################### PARAMETERS #####################################
    # program_versions = ['v1', 'v2', 'v3', 'v4', 'v5']
    program_versions = ['v2', 'v3', 'v5']
    total_qubits = 10
    total_repeats = 20
    backend = 'Ideal'    
    opo_toler_err = 0.05
    woo_toler_err = 0
    ######################################################################################

    print(
        f"\n" 
        f"RQ2 subtask{task_id} with the default configuration" 
        f"\n"
    )
    
    if task_id == 1:
        # In this task, we compare DOSS with two WOOs
        shots_list = [5, 10, 15]
        baselines = ['STSQ', 'STFQ', 'DOSS']
        # baselines = ['STSQ', 'STFQ']
        # Generate all the combinations
        combined_variables = list(itertools.product(
            abb_programs, 
            program_versions, 
            shots_list, 
            baselines
            )
        )
        for abb_name, program_version, shots, test_oracle in combined_variables:
            running_exp(
                abb_name,
                program_version,
                test_oracle,
                shots,
                total_qubits,
                2,              # This indicates RQ2
                task_id,
                backend,
                total_repeats,
                opo_toler_err,
                woo_toler_err
            )
    elif task_id == 2:
        # In this task, we include OPOs along with their mutants with separation
        shot_list = [5, 15]
        baselines = ['ChiTest', 'DMSQ-ChiTest', 'CrsEnt', 'DMSQ-CrsEnt']
        # Generate all the combinations
        combined_variables = list(itertools.product(
            abb_programs, 
            program_versions, 
            baselines,
            shot_list
            )
        )
        for abb_name, program_version, test_oracle, shots in combined_variables:
            running_exp(
                abb_name,
                program_version,
                test_oracle,
                shots,
                total_qubits,
                2,              # This indicates RQ2
                task_id,
                backend,
                total_repeats,
                opo_toler_err,
                woo_toler_err
            )

def default_config_RQ3(task_id):
    ##################################### PARAMETERS #####################################
    program_version = 'v1'
    shots = 10
    backend = 'Ideal'    
    # baselines = ['MWTest', 'ChiTest', 'KSTest', 'CrsEnt', 'JSDiv', 'ExpVal', 'STSQ', 'STFQ', 'DOSS']
    baselines = ['STFQ']
    opo_toler_err = 0.05
    woo_toler_err = 0
    ######################################################################################

    print(
        f"\n" 
        f"RQ3 subtask{task_id} with the default configuration" 
        f"\n"
    )
    
    if task_id == 1:
        # Generate all the combinations
        combined_variables = list(itertools.product(abb_programs, baselines))
        for abb_name, test_oracle in combined_variables:
            # Only qubits with an odd number appear in IntegerComparator
            qubit_list = list(range(6, 13)) if abb_name != "IC" else list(range(6, 13, 2))                      # TODO
            for total_qubits in qubit_list:
                # Repeating 12-qubit Diagonal is extremely costly with STFQ, 
                # so we set 5 repeats for this program, while 20 for the others.
                total_repeats = 3 if abb_name == 'DO' and test_oracle == "STFQ" and total_qubits == 12 else 5 # 5, 20 TODO
                running_exp(
                    abb_name, 
                    program_version, 
                    test_oracle, 
                    shots, 
                    total_qubits, 
                    3,          # This indicates RQ3 
                    task_id, 
                    backend, 
                    total_repeats, 
                    opo_toler_err, 
                    woo_toler_err
                )

def default_config_RQ4(task_id):
    ##################################### PARAMETERS #####################################
    program_version = 'v1'
    shots = 10
    total_qubits = 10
    backends = ['Ideal', 'Manila', 'Vigo', 'Athens']    
    baselines = ['DOSS', 'STSQ', 'ChiTest']
    total_repeats = 20
    opo_toler_err = 0.05
    ######################################################################################
        
    print(
        f"\n" 
        f"RQ4 subtask{task_id} with the default configuration" 
        f"\n"
    )
    
    # Implement subtasks for RQ4
    if  task_id == 1:
        # RQ4 subtask2: investigate DOSS with a varied error limits
        woo_toler_errs = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
        test_oracle = 'DOSS'
        # Generate all the combinations
        combined_variables = list(itertools.product(backends[1:], abb_programs, woo_toler_errs))
        for backend, abb_name, woo_toler_err in combined_variables:        
            running_exp(
                abb_name, 
                program_version, 
                test_oracle, 
                shots, 
                total_qubits, 
                4,              # This indicates RQ4 
                task_id, 
                backend, 
                total_repeats, 
                opo_toler_err, 
                woo_toler_err
            )
    else:
        print("invalid subtask") 