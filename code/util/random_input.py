import random

def random_input_single(length, elem_list, max_size=1000):
    # Generate random inputs of a given length from a list of elements.
    # The inputs are unique combinations of elements from the list.
    num_input = 0
    input_list = []
    while num_input <= min(max_size, len(elem_list) ** length):
        templist = []
        for _ in range(length):
            rand_elem = random.choice(elem_list)
            templist.append(rand_elem)
        input_list.append(templist)
        unique_list = list(set(tuple(x) for x in input_list))
        input_list = [list(x) for x in unique_list]
        num_input = len(input_list)
    return input_list

def random_input_ent(input_qubits, single_list, entangled_list, max_size=1000):
    """
    Generate a list of random quantum state sequences for testing.
    
    Args:
        input_qubits: Total number of qubits each test input must account for
        max_size: Maximum number of test inputs to generate
        
    Returns:
        List of test inputs, where each test input is a list of quantum states 
        (single-qubit or Bell states) that collectively account for exactly `input_qubits`
    """
    # List to store all generated test inputs
    test_inputs = []
    
    # Generate up to max_size test inputs
    for _ in range(max_size):
        # Current state sequence for this test input
        current_sequence = []
        # Current qubit count covered by the sequence
        covered_qubits = 0
        
        # Build sequence until all input qubits are accounted for
        while covered_qubits < input_qubits:
            remaining_qubits = input_qubits - covered_qubits
            
            # When only one qubit remains, must choose a single-qubit state
            if remaining_qubits == 1:
                state = random.choice(single_list)
                current_sequence.append(state)
                covered_qubits += 1
                
            # For two or more qubits remaining, randomly choose state type
            else:
                # Randomly decide to add single-qubit or Bell state
                if random.choice([0, 1]):
                    state = random.choice(single_list)
                    current_sequence.append(state)
                    covered_qubits += 1
                else:
                    state = random.choice(entangled_list)
                    current_sequence.append(state)
                    covered_qubits += 2
        
        # Add the completed sequence to our test inputs
        test_inputs.append(current_sequence)
    
    return test_inputs