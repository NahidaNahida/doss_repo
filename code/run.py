import argparse
import os
import sys
from default_config import (
    default_config_RQ1, 
    default_config_RQ2, 
    default_config_RQ3, 
    default_config_RQ4
)
from experiments import running_exp
import util.global_variables as gv

# The mapping of the object programs
name_mapping = gv.abb2full_name_mapping

# Add the root directory to the system path
root = os.path.dirname(__file__)
sys.path.append(root)
for program in name_mapping.values():
    sys.path.append(os.path.join(root, program))
sys.path.append(os.path.join(root, 'util'))

################## ARGUMENT CONFIGURATION ################## 
# The baselines for the object programs
baselines = gv.total_baselines
args_choices = {
    "mode": ['replicated', 'custom'],
    "program_names": list(name_mapping.keys()),
    "program_versions": [1, 2, 3, 4, 5],
    "test_oracles": baselines["opos"] + baselines["woos"],
    "backends": ['Ideal', 'Manila', 'Vigo', 'Athens']
}

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run a specific RQ script from a program directory.')
    
    # Add the argument of the object program
    parser.add_argument('mode',
                        type=str,
                        help='The mode for replication or custom running',
                        choices=args_choices["mode"])
    
    # Add the followings for the custom mode only
    parser.add_argument('--program', 
                        type=str,
                        help='The abbreviation of an object program (required for "custom" mode)',
                        choices=args_choices["program_names"])
    parser.add_argument('--ver',
                        type=int,
                        help='The buggy version for testing (required for "custom" mode)',
                        choices=args_choices["program_versions"])
    parser.add_argument('--oracle',
                        type=str,
                        help='The test oracle (required for "custom" mode)',
                        choices=args_choices["test_oracles"])
    parser.add_argument('--shots',
                        type=int,
                        help='The shots for each run of the quantum circuit (required for "custom" mode)')
    parser.add_argument('--backend',
                        type=str,
                        help='The backend for implementing quantum circuits (required for "custom" mode)',
                        default='Ideal',
                        choices=args_choices["backends"])
    parser.add_argument('--repeats',
                        type=int,
                        help='The number of repeating the same experiment (required for "custom" mode)',
                        default=20)
    parser.add_argument('--err',
                        type=float,
                        help='The error limit for the test oracle (required for "custom" mode)')
    
    # Add the followings for the replication mode only
    parser.add_argument('--rq',
                        type=int,
                        help="The index for replicating the research question (required for 'replicated' mode)",
                        choices=[1, 2, 3, 4])
    parser.add_argument('--task',
                        type=int,
                        help="The index of the task for specific research question (required for 'replicated' mode)" +
                             "RQ1: [1, 2]; RQ2: [1, 2]; RQ3: [1]; RQ4: [1, 2]",
                        choices=[1, 2])
    parser.add_argument

    args = parser.parse_args()
   
    if args.mode == 'replicated':
        # Replicate the experiments with the default configurations
        default_rqs = {1: default_config_RQ1,
                       2: default_config_RQ2,
                       3: default_config_RQ3,
                       4: default_config_RQ4} 
        rq_id, task_id = args.rq, args.task
        if None in [rq_id, task_id]:
            print('incomplete arguments for "rep" mode')
        else:
            default_rqs[rq_id](task_id)
    elif args.mode == 'custom':
        total_qubits = 10   # We limit the total qubit numbers as 10 corresponding to the generated test suites
        abb_name = args.program
        program_version = f"v{args.ver}"
        test_oracle = args.oracle
        shots = args.shots
        backend = args.backend
        total_repeats = args.repeats
        toler_error = args.err
        if None in [
            abb_name, 
            program_version, 
            test_oracle, 
            shots, backend, 
            total_repeats, 
            toler_error
        ]:
            print('incomplete arguments for "custom" mode')
        else:
            if test_oracle in baselines["opos"]:
                # Give the default setting if the value is not assigned before
                opo_toler_err = toler_error if toler_error != None else 0.05
                woo_toler_err = 0 if backend == "Ideal" else 0.25
            elif test_oracle in baselines['woos']:
                # Give the default setting if the value is not assigned before
                woo_toler_err = toler_error if toler_error != None else 0
                opo_toler_err = 0.05
            running_exp(
                abb_name, 
                program_version, 
                test_oracle, 
                shots, 
                total_qubits, 
                None,           # This refers to the custom mode 
                None,           # This refers to the custom mode
                backend, 
                total_repeats, 
                opo_toler_err, 
                woo_toler_err
            )

if __name__ == '__main__':
    main()