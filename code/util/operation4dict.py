def extract_keys(nested_dict, level=0, result=None):
    """
    Recursively extracts keys from a nested dictionary at all levels.
    
    Parameters:
    nested_dict (dict): The input dictionary from which keys will be extracted.
    level (int): The current depth level in the nested dictionary (default is 0).
    result (dict): A dictionary to store the keys of each level. It is initialized to an empty dictionary if not provided.

    Returns:
    dict: A dictionary where keys are the depth levels and values are lists of keys at that level.
    """
    
    # Initialize the result dictionary if it's not provided
    if result is None:
        result = {}

    # Extract the keys at the current level and store them in the result dictionary
    result[level] = list(nested_dict.keys())

    # Iterate through the dictionary and recursively extract keys from nested dictionaries
    for _, value in nested_dict.items():
        # If the value is a dictionary, recurse deeper to extract its keys
        if isinstance(value, dict):
            extract_keys(value, level + 1, result)

    # Return the result dictionary with keys from all levels
    return result

# Recursive function to merge dictionaries
def merge_dicts(d1, d2):
    result = d1.copy()  # Avoid modifying the original dictionary
    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)  # Recursively merge nested dictionaries
        else:
            result[key] = value
    return result