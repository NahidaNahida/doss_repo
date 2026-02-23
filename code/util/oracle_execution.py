from scipy.spatial.distance import jensenshannon
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu
from scipy.stats import ks_2samp
from scipy.stats import entropy

import numpy as np 
from util.closing_warnings import suppress_warnings
from util.data_conversion import *

suppress_warnings()                 # Close warnings globally

def opo_execution(total_qubits, exp_results, test_samps, test_oracle, toler_err=0.05):
    '''
        implement the required statistical methods and yield the test result

        Input variables:
            + n             [int]   the number of output qubits
            + exp_results   [list]  the expected samples for NHTs and expected probabilities for SDMs
            + test_samps    [list]  the list of measurement results from the tested program
            + test_oracle   [str]   the OPO type using statistical methods
            + toler_err     [float] the threshold for NHTs and SDMs
        
        Output variable:
            + test result   [boolean]   whether the test passes, using TRUE of FALSE
    '''
    
    # transform the dictionary into a list of samples 
    test_probs = samp2prob(total_qubits, test_samps)

    if test_oracle in ['ChiTest', 'DMSQ-ChiTest']:
        test_result = opo_chi_squared(exp_results, test_samps, total_qubits, toler_err)
    elif test_oracle in ['KSTest', 'DMSQ-KSTest']:
        test_result = opo_ks_test(exp_results, test_samps, toler_err)
    elif test_oracle in ['MWTest', 'DMSQ-MWTest']:
        test_result = opo_mwu_test(exp_results, test_samps, toler_err)
    elif test_oracle in ['JSDiv', 'DMSQ-JSDiv']:
        test_result = opo_js_div(exp_results, test_probs, toler_err)
    elif test_oracle in ['CrsEnt', 'DMSQ-CrsEnt']:
        test_result = opo_cross_entropy(exp_results, test_probs, toler_err)
    elif test_oracle in ['ExpVal', 'DMSQ-ExpVal']:
        test_result = opo_expect_value(exp_results, test_probs, toler_err)
    return test_result

def woo_execution(dict_counts, valid_val, toler_err=0):
    val_list = list(dict_counts.keys())
    shots = sum(dict_counts.values())
    num_toler_wrong_results = toler_err * shots
    # num_bits = len(val_list[0])
    # valid_str_val =  bin(valid_val)[2:].zfill(num_bits)

    # toler_err = 0 corresponds to the ideal case
    # toler_err indicates the number of val!=valid_val where we still consider as the test passing.
    if valid_val in val_list and len(val_list) == 1:
        return True
    elif valid_val in val_list and len(val_list) >= 2:
        num_invalid_samps = shots - dict_counts[valid_val]
        return True if num_invalid_samps <= num_toler_wrong_results else False
    else:
        return False

def opo_chi_squared(exp_samples, test_samples, n, toler_err=0.05):
    exp_frequencies = count2frequencies(exp_samples, 2**n)
    test_frequencies = count2frequencies(test_samples, 2**n)
    
    popList = []
    
    # To avoid 0 / 0, remove the exp_frequencies[i] and test_frequencies[i] if
    # exp_frequencies[i] / test_frequencies[i] approximates 0 / 0.
    for i in range(len(exp_frequencies)):
        if exp_frequencies[i] <= 1e-6 and test_frequencies[i] <= 1e-6:
            popList.append(i)
    if len(popList) > 0:
        for pop_index in sorted(popList, reverse=True):
            exp_frequencies.pop(pop_index)
            test_frequencies.pop(pop_index)
    
    if len(exp_frequencies) == 1 and len(test_frequencies) == 1:
        return True
    else:        
        _, p_value = chisquare(exp_frequencies, test_frequencies) # Pearson chi-squares
        if p_value > toler_err:
            return True
        else:
            return False

def opo_js_div(exp_probs, res_probs, toler_err=0.05):
    exp_probs = np.array(exp_probs)
    res_probs = np.array(res_probs)
    dist = jensenshannon(exp_probs, res_probs)
    if dist <= toler_err:
        return True
    else:
        return False

def opo_cross_entropy(exp_probs, res_probs, toler_err=0.05):
    exp_probs = np.array(exp_probs)
    res_probs = np.array(res_probs)
    dist = entropy(exp_probs, res_probs)
    if dist <= toler_err:
        return True
    else:
        return False

def opo_expect_value(exp_probs, res_probs, toler_err=0.05):
    """
        Calculate the expected value for both expected and result probabilities
        exp_probs and res_probs should be lists of probabilities
        
        Based on Asmar's work [https://dl.acm.org/doi/abs/10.1145/3691620.3695275], they set 0.01 for the simulator 
        and std_err for the real quantum computer. However, the std_err depends on the specific quantum computer, and
        is calculated upon enough statistical samples. Therefore, we set the default toler_err = 0.05 for convenience.
    """
    exp_probs = np.array(exp_probs)
    res_probs = np.array(res_probs)
    exp_val = np.sum(np.arange(len(exp_probs)) * exp_probs)
    res_val = np.sum(np.arange(len(res_probs)) * res_probs)
    dist = abs(exp_val - res_val)
    if dist <= toler_err:
        return True
    else:
        return False

def opo_mwu_test(exp_samps, test_samps, toler_err=0.05):
    # Mann-Whitney U test
    # exp_samps and test_samps should be lists of samples
    exp_samps = list(exp_samps)
    test_samps = list(test_samps)
    _, p_value = mannwhitneyu(exp_samps, test_samps)
    if p_value > toler_err:
        return True
    else:
        return False
    
def opo_ks_test(exp_samps, test_samps, toler_err=0.05):
    # Kolmogorov-Smirnov test
    # exp_samps and test_samps should be lists of samples
    exp_samps = list(exp_samps)
    test_samps = list(test_samps)
    _, p_value = ks_2samp(exp_samps, test_samps, method='asymp')
    if p_value > toler_err:
        return True
    else:
        return False
    