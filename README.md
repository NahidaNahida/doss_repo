# DOSS

## Description

This repository incorporates the artifact involved in the manuscript '*A Dynamic Test Oracle for Quantum Programs with Separable Output States*'. 

More details will be updated if the manuscript is possibly accepted for publication. 

## Environment

First create a conda environment, such as named hoss.

```
conda create -n doss python=3.10.18
```

Then, activate the environment and install the packages in `requirements.txt`.

```
conda activate doss
pip install -r requirements.txt
```

Here are the requirements:

```
numpy==2.2.0
pandas==2.2.3
qiskit==0.46.2
qiskit_aer==0.13.3
qiskit_terra==0.46.2
scipy==1.14.1
tqdm==4.66.1
```

## Data

+ **Test suites**: [`test_suites`](./data/test_suites), the generated test suites by random sampling.
+ **Raw data**: zipped into [`raw_data.zip`](./data/raw_data.zip), the raw data derived from running the code.
+ **Processed data**: [`processed_data`](./data/processed_data), the JSON files summarizing the raw data and some of them ready for the displayed figures and tables.
+ **Displayed data**: [`displayed_data`](./data/displayed_data), the complete figures and raw data for the tables, where some of them are selected in the paper.

## Code

We provide `rep_all.sh` to replicate all the experiments in one try.

### On Linux

**Ensure the script has execution permissions**:
Open a terminal and navigate to the directory where `rep_all.sh` is located. Run the following command to make it executable:

```bash
chmod +x rep_all.sh
```

**Run the script**:
 Once the script is executable, you can run it using:

```bash
./rep_all.sh
```

This will execute the script on your Linux system.

### On Windows

Once you're in the correct directory, execute the script by running the follow demand in terminal.

```bash
./rep_all.sh
```