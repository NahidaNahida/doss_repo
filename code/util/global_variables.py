abb2full_name_mapping = {
    "DO":   "Diagonal",
    "IC":   "IntegerComparator",
    "LAF":  "LinearAmplitudeFunction",
    "LPR":  "LinearPauliRotations",
    "QFT":  "QuantumFourierTransform",
    "WA":   "WeightedAdder"
}

total_baselines = {
    "opos": ["JSDiv", "CrsEnt", "ExpVal", "DMSQ-JSDiv", "DMSQ-CrsEnt", "DMSQ-ExpVal",
             "ChiTest", "KSTest", "MWTest", "DMSQ-ChiTest", "DMSQ-KSTest", "DMSQ-KWTest"],
    "woos": ["STFQ", "STSQ", "DOSS"]
}

opo_baselines = {
    "samps": ["MWTest", "ChiTest", "KSTest", "DMSQ-MWTest", "DMSQ-ChiTest", "DMSQ-KWTest"], 
    "probs": ["JSDiv", "CrsEnt", "ExpVal", "DMSQ-JSDiv", "DMSQ-CrsEnt", "DMSQ-ExpVal"]
}

all_versions = ['v1', 'v2', 'v3', 'v4', 'v5']

all_abbs = list(abb2full_name_mapping.keys())

default_rq_settings = {
    "common": {
        "total_repeats": 20
    },
    "RQ1": {
        "task1": {     
            "program_versions": all_versions,
            "abb_programs": all_abbs,
            "shots_dict": {
                "DO":   range(5, 201, 5),
                "IC":   range(2, 51, 2),    # This program is expected to output a deterministic result
                "LAF":  range(5, 201, 5),
                "LPR":  range(5, 201, 5),
                "QFT":  range(5, 201, 5),
                "WA":   range(2, 51, 2),    # This program is expected to output a deterministic result
            },
            "test_oracles": ["MWTest", "ChiTest", "KSTest", "CrsEnt", "JSDiv", "ExpVal", "DOSS"],
            "backend": "Ideal",
            "total_qubits": 10,
            "errs": {
                "woos": [0],
                "opos": [0.05]
            }
        },
        "task2": {
            "program_versions": all_versions,
            "abb_programs": ['LAF', 'LPR'],
            "shots_dict": {
                "DO":   range(5, 201, 5),
                "IC":   range(2, 51, 2),    # This program is expected to output a deterministic result
                "LAF":  range(5, 201, 5),
                "LPR":  range(5, 201, 5),
                "QFT":  range(5, 201, 5),
                "WA":   range(2, 51, 2),    # This program is expected to output a deterministic result
            },
            "test_oracles": ["CrsEnt", "JSDiv"],
            "backend": "Ideal",
            "total_qubits": 10,
            "errs": {
                "woos": [0],
                "opos": [0.01, 0.02, 0.1, 0.2, 0.5]
            } 
        }
    },
    "RQ2": {
        "task1":{
            "program_versions": all_versions,
            "abb_programs": all_abbs,
            "shots": [5, 10, 15],
            "test_oracles": ['STFQ', 'STSQ', 'DOSS'],
            "backend": "Ideal",
            "total_qubits": 10,
            "errs":{
                "opo": 0.05,
                "woo": 0
            }
        },
        "task2":{
            "program_versions": all_versions,
            "abb_programs": all_abbs,
            "shots": [5, 10, 15],
            "test_oracles": ['ChiTest', 'DMSQ-ChiTest', 'CrsEnt', 'DMSQ-CrsEnt'],
            "backend": "Ideal",
            "total_qubits": 10,
            "errs":{
                "opo": 0.05,
                "woo": 0
            }
        }
    },
    "RQ3": {
        "task1":{
            "program_version": "v1",
            "abb_programs": all_abbs,
            "shots": 10,
            "test_oracles": ['MWTest', 'ChiTest', 'KSTest', 'CrsEnt', 'JSDiv', 'ExpVal', 'STSQ', 'STFQ', 'DOSS'],
            "backend": "Ideal",
            "total_qubits": {
                "DO": list(range(6, 13)),
                "IC": list(range(6, 13, 2)),
                "LPR": list(range(6, 13)),
                "LAF": list(range(6, 13)),
                "WA": list(range(6, 13)),
                "QFT": list(range(6, 13))
            },
            "errs":{
                "opo": 0.05,
                "woo": 0
            }
        }
    },
    "RQ4": {
        "task1":{
            "program_version": "v1",
            "abb_programs": all_abbs,
            "shots": 10,
            "test_oracle": 'DOSS',
            "backends": ['Manila', 'Vigo', 'Athens'],
            "total_qubits": 10,
            "woos": [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
        }
    }
}