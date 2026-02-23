import warnings
'''
    Close the warning from Qiskit.
'''

def suppress_warnings():
    """
        Suppress DeprecationWarning and FutureWarning globally.
    """
    # Close DeprecationWarning for Qiskit packages
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Close FutureWarning for Qiskit packages
    warnings.filterwarnings("ignore", category=FutureWarning)

    # Close RuntimeWarning for baseline test oracles
    warnings.filterwarnings("ignore", category=RuntimeWarning)