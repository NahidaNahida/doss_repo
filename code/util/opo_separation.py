from collections import Counter

def output_separation(res, bit_length, arg_type):
    """
    Expand bitwise frequencies into sample lists or compute bitwise probabilities.

    Args:
        res (list or dict): 
            If 'samps': list of int (samples)
            If 'probs': 
                - list of float (index -> prob)
                - dict (int -> prob)
        bit_length (int): Number of bits
        arg_type (str): 'samps' or 'probs'

    Returns:
        If 'samps': list of list[int]
        If 'probs': list of list[float] -> [[p0_0, p0_1], [p1_0, p1_1], ...]
    """
    if arg_type == "samps":
        samps = res
        binary_samples = [bin(s)[2:].zfill(bit_length) for s in samps]
        freq_dict = Counter(binary_samples)

        bitwise_freqs_list = [[] for _ in range(bit_length)]
        for binary_str, freq in freq_dict.items():
            for i, bit in enumerate(binary_str):
                bitwise_freqs_list[i].extend([int(bit)] * freq)
        return bitwise_freqs_list

    elif arg_type == "probs":
        if isinstance(res, list):
            prob_dict = {i: p for i, p in enumerate(res)}
        elif isinstance(res, dict):
            prob_dict = res
        else:
            raise ValueError("For 'probs', input must be list or dict")

        bitwise_probs_list = [[0.0, 0.0] for _ in range(bit_length)]

        for sample_int, p in prob_dict.items():
            binary_str = bin(sample_int)[2:].zfill(bit_length)
            for i, bit in enumerate(binary_str):
                bitwise_probs_list[i][int(bit)] += p

        return bitwise_probs_list

    else:
        raise ValueError("arg_type must be 'samps' or 'probs'")