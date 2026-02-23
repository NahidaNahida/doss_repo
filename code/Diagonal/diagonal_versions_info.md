# DO - v1
    bug:
        line 110: add a \texttt{ch} gate
        + circuit.ch(0, -1)       # defect: add

    complexity:
        # qubits = 6:   # gates = [11, 105], depth = [10, 91]
        # qubits = 7:   # gates = [26, 164], depth = [22, 142]
        # qubits = 8:   # gates = [27, 359], depth = [23, 328]
        # qubits = 9:   # gates = [50, 574], depth = [43, 536]
        # qubits = 10:  # gates = [53, 359], depth = [45, 329] 
        # qubits = 11:  # gates = [93, 1328], depth = [78, 1273] 
        # qubits = 12:  # gates = [160, 4179], depth = [138, 4117] 
 

# DO - v2 
    bug:
        line 102: modify the condition of \texttt{while}
        - while n >= 2:      
        + while n >= 8:        # >= 2 -> >= 8

    complexity:
        # qubits = 10:  # gates = [30, 573], depth = [28, 566]

# DO - v3
    bug:
        line 105: switch two inputs of a subroutine
        - diag_phases[i // 2], rz_angle = _extract_rz(diag_phases[i], diag_phases[i + 1])
        + diag_phases[i // 2], rz_angle = _extract_rz(diag_phases[i + 1], diag_phases[i]) # def: switch diag_phases[i], diag_phases[i + 1]

    complexity:
        # qubits = 10:  # gates = [35, 527], depth = [33, 521]

# DO - v4 
    bug:
        line 102: add a \texttt{cx} gate
        + circuit.cx(0, 1)        # add gate

    complexity: 
        # qubits = 10:  # gates = [32, 1088], depth = [30, 1081]

# DO - v5
    bug:
        line 110: modify the target qubit of a \texttt{ucrz} gate
        - circuit.ucrz(angles_rz, ctrl_qubits, target_qubit)
        + circuit.ucrz(angles_rz, ctrl_qubits, 0) 

    complexity:
        # qubits = 10:  # gates = [31, 527], depth = [31, 527]