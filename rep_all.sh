#!/bin/bash

# Task list
rq_list=("1" "2" "3" "4")

# Run in background with nohub, display output in terminal (do not display | tee -a "$output_file" &)
for rq in "${rq_list[@]}"
do
    echo "Running the RQ $rq"
    
    # If rq is 1 or 2, execute tasks 1 and 2
    if [ "$rq" == "1" ] || [ "$rq" == "2" ]; then   
        tasks=("1" "2")
        for task in "${tasks[@]}"
        do
            output_file="nohup_rq${rq}_task${task}.out"  # Both task 1 and 2
            nohup python -u code/run.py replicated --rq $rq --task $task | tee -a "$output_file"
        done
    else
        # For other rq values, only execute task 1
        output_file="nohup_rq${rq}_task1.out"  # Only task 1
        nohup python -u code/run.py replicated --rq $rq --task 1 | tee -a "$output_file"
    fi
done
