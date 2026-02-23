from qiskit import transpile
from qiskit_aer import Aer, AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit.providers.fake_provider import FakeManilaV2, FakeVigoV2, FakeAthensV2

def circuit_execution_ideal(qc, shots): 
    """
        Execute the quantum circuit with given shots, and then return the measurement results.
    """     
    backend = Aer.get_backend('qasm_simulator')
    executed_qc = transpile(qc, backend)
    count= backend.run(executed_qc, shots=shots).result().get_counts()
    dict_counts = count.int_outcomes()
    return dict_counts.copy()

    
def circuit_execution_vector(qc):
    """
        Execute the quantum circuit, and then return the statevectors.
    """
    backend = Aer.get_backend('statevector_simulator')
    executed_qc = transpile(qc, backend)
    result = backend.run(executed_qc).result()
    statevector = result.get_statevector()
    return statevector


def circuit_execution_noise(qc, shots, model):
    """
        Execute the quantum circuit via noisy simulators.
    """
    # Get a fake backend from the fake provider
    fake_noise_models = {
        "Manila": FakeManilaV2(),
        "Vigo": FakeVigoV2(),
        "Athens": FakeAthensV2()
    }
    noise_model = NoiseModel.from_backend(fake_noise_models[model])

    backend = AerSimulator(noise_model=noise_model)
    executed_qc = transpile(qc, backend)
    count= backend.run(executed_qc, shots=shots).result().get_counts()
    dict_counts = count.int_outcomes()
    return dict_counts.copy()


def measurement_based_backend(qc, shots, backend):
    if backend == 'Ideal':
        dict_counts = circuit_execution_ideal(qc, shots)
    elif backend in ['Manila', 'Vigo', 'Athens']:
        dict_counts = circuit_execution_noise(qc, shots, backend)
    return dict_counts