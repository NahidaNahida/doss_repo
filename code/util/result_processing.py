def test_result_updating(test_result, true_result, res_dict):
    """
        Update the result dictionary based on the test result and the true result.
    
        Args:
            test_result (bool): The result of the test (True or False).
            true_result (bool): The actual expected result (True or False).
            res_dict (dict): A dictionary to store the results.
        
            We require that the res_dict should be in a form as 
            res_dict = {"true_pos": 0, 
                        "true_neg": 0, 
                        "false_pos": 0, 
                        "false_neg": 0, 
                        "#faults": 0}
                        
        Returns:
            None: The function updates the res_dict in place.
    """
    if test_result == True and true_result == True:
        res_dict["true_neg"] += 1
    elif test_result == True and true_result == False:
        res_dict["false_neg"] += 1
    elif test_result == False and true_result == True:
        res_dict["false_pos"] += 1
        res_dict["#faults"] += 1
    elif test_result == False and true_result == False:
        res_dict["true_pos"] += 1
        res_dict["#faults"] += 1