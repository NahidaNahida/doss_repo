def find_stable_point(shots, ave_faults, std_faults, eps_conv=0.5, window=5, exp_faults=25):
    '''
        This function calculates the involved three metrics
        
        Inputs:
            + shots :      the number of shots
            + ave_faults:  the list of mean values of detected faults 
            + std_faults:  the list of standard derivations of detected faults
            + eps_conv:    the tolerable error limit for the convergency
            + windows:     the length of windows
        
        Outputs:
            + s_star
            + delta_star
            + sigma_star
    '''
    stable_count = 0
    for i in range(1, len(ave_faults)):
        if abs(ave_faults[i] - ave_faults[i-1]) < eps_conv:
            stable_count += 1
        else:
            stable_count = 0                    # if the convergency fails, reset the count
        if stable_count >= window - 1:          # continue to make the criterion true for the window's length
            return shots[i], exp_faults - ave_faults[i], std_faults[i]   # the curve identified as convergency
    return "O/S", exp_faults - ave_faults[i], std_faults[i]              # the curve identified as no convergency