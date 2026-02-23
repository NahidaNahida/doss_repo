import numpy as np
import util.global_variables as gv
opo_baselines_dict = gv.opo_baselines

def expected_output_generation(statistical_method, exp_state, total_qubits, shots):
    """
        Generate expected output based on the statistical method and experimental state.

        Args:
            statistical_method (str): The statistical method to be used (e.g., "MWTest", "ChiTest", etc.).
            exp_state (list): The expected state of the quantum system, represented as a list of complex amplitudes.
            total_qubits (int): The total number of qubits in the quantum system.
            shots (int): The number of samples to generate.
        
        Returns:
            list: A list of expected outputs based on the specified statistical method.
    """
      
    exp_probs = list(abs(np.array(exp_state)) ** 2) 
    # probs: use the probability distribution
    # samps: generate samples comforting the expected probabilities
    if statistical_method in opo_baselines_dict["samps"]:
        opo_type = "samps"  
        exp_outputs = list(np.random.choice(range(2 ** total_qubits), size=shots, p=exp_probs))
    elif statistical_method in opo_baselines_dict['probs']:
        opo_type = "probs"
        exp_outputs = exp_probs
    return exp_outputs, opo_type

 