import os
import pandas as pd
import re

import util.global_variables as gv

full2abb_name_mapping = {val: key for key, val in gv.abb2full_name_mapping.items()}

def reading_files(
    program_name, 
    program_version, 
    total_qubits, 
    rq_id
):
    """
        Read the test suite CSV file based on the program name, version, total qubits, and research question ID.

        Args:
            program_name (str): The name of the program (e.g., "Diagonal", "IntegerComparator", "LinearAmplitudeFunction", etc.).
            program_version (str): The version of the program (e.g., "v1"). 
            total_qubits (int): The total number of qubits used in the test suite.
            rq_id (int): The research question ID (1, 2, 3, or 4).
        
        Returns:
            pd.DataFrame: A pandas DataFrame containing the test suite data read from the CSV file.
    """
    abb_name = full2abb_name_mapping[program_name]

    # Only in RQ3, we run varied qubits
    data_type = 'fixed' if rq_id in [1, 2, 4] else 'varied'

    # Obtain the current path directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    file_name = (
        f"{abb_name}_{program_version}_testSuites"
        f"_(qubit={total_qubits},fr=0.5,#t=50).csv"
    )

    # Construct the absolute path to my_file.csv
    csv_path = os.path.abspath(os.path.join(
        script_dir, 
        '..',
        '..', 
        'data', 
        'test_suites', 
        program_name,
        data_type,
        r"{}".format(file_name)
        )
    )
    csv_path = os.path.normpath(csv_path)

    # Read CSV file with pandas
    df = pd.read_csv(csv_path) 
    return df

def saving_files(
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
):

    """
        Save the results of the test suite execution to a CSV file.
        The file is saved in a directory structure based on the research question ID, program name, and test oracle.
        
        Args:
            rq_id (int): The research question ID (1, 2, 3, or 4).
            program_name (str): The name of the program (e.g., "Diagonal", "IntegerComparator", "LinearAmplitudeFunction", etc.).
            program_version (str): The version of the program (e.g., "v1"). 
            total_qubits (int): The total number of qubits used in the test suite.
            test_oracle (str): The type of test oracle used (e.g., "DOSS", "ChiTest", "KSTest", etc.).
            shots (int): The number of shots used in the test execution.
            toler_err (float): The tolerable error for the test execution.
            backend (str): The backend used for the test execution.
            res_dict (dict): The results dictionary containing the test results.
            run_time (float): The run time of the test execution.

        Returns:
            None: The function saves the results to a CSV file and does not return any value.
    """
    
    # Obtain the current path directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abb_name = full2abb_name_mapping[program_name]
    saving_path = os.path.abspath(os.path.join(
        script_dir, 
        '..',
        '..', 
        'data', 
        'raw_data',
        f'RQ{rq_id}-{task_id}' if rq_id != None else 'custom',
        abb_name,
        test_oracle
        )
    )

    # Check if the saving path exists, if not create it
    if not os.path.exists(saving_path):
        os.makedirs(saving_path)  # Create the directory if it does not exist


    # Determine the file name
    if rq_id == None:
        # This refers to the custom mode
        info_without_id = f"{abb_name}_{program_version}_custom.csv"
    else:
        basic_info = f"{abb_name}_{program_version}_RQ{rq_id}_{test_oracle}"
        if rq_id == 1: 
            # RQ1 configures different shots with the ideal simulator.
            # Besides, different thresholds for SDMs are explored.
            rq_specified_info = f"shots={shots}_err={toler_err}.csv"
        elif rq_id == 2:
            # RQ2 also investigates several shots for separation and decomposition.
            rq_specified_info = f"shots={shots}.csv"
        elif rq_id == 3:
            # RQ3 sets different qubit numbers, so we need to specify the qubit number.
            rq_specified_info = f"qubits={total_qubits}.csv"
        elif rq_id == 4:
            # RQ4 includes the noise model, so we need to specify the backend.
            if test_oracle == 'DOSS':
                # We also discuss how the DOSS performs with different tolerable errors.
                rq_specified_info = f"backend={backend}_err={toler_err}.csv"
            else:
                # For other oracles, we only need to specify the backend.
                rq_specified_info = f"backend={backend}.csv"

        # Determine the appropriate id. We should consider the existing .csv files in the saving_path
        info_without_id = f"{basic_info}_{rq_specified_info}"
    
    # Check if there are existing .csv files in the saving_path
    all_files = os.listdir(saving_path)
    existing_csv_files = [file for file in all_files if file.endswith('.csv')]
    
    if not existing_csv_files:
        repeat_id = 1  # If there is no .csv file, return repeat_id = 1
    else:
        # Use regular expressions to extract the number before the first "_" in the file name
        id_list = [] 
        for file in existing_csv_files:
            # Match files with a pattern like "123_some_info.csv"
            match = re.match(r'^(\d+)_(' + re.escape(info_without_id) + r')', file)
            if match:
                id_list.append(int(match.group(1)))  # Append the number part before the first "_"

        # If there is no valid id, then repeat_id = 1
        if not id_list:
            repeat_id = 1
        else:
            repeat_id = max(id_list) + 1  # Increment the maximum id by 1
    
    file_name = f"{repeat_id}_{info_without_id}"
    # Determine the absolute path to the file
    csv_path = os.path.abspath(os.path.join(saving_path, file_name))
    csv_path = os.path.normpath(csv_path)

    # Create a DataFrame and save it to CSV
    extra_info = {
        'time': run_time,
        '#qubit': total_qubits,
        'shots': shots,
        'test_oracle': test_oracle,
        'backend': backend,
        'toler_err': toler_err,
    }
    full_record = {**res_dict, **extra_info}
    df = pd.DataFrame([full_record])
    
    # Save the DataFrame to a CSV file
    df.to_csv(csv_path, index=False)
    return