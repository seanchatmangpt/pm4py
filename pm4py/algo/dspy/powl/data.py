"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""



import os
import random


def create_log_abstraction(
    log_obj,
    max_dfg_len: int = 2000,
    max_variants_len: int = 1500,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> str:
    """Create a textual abstraction of an event log for LLM consumption."""
    import pm4py

    dfg_text = pm4py.llm.abstract_dfg(
        log_obj,
        max_len=max_dfg_len,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )

    variants_text = pm4py.llm.abstract_variants(
        log_obj,
        max_len=max_variants_len,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )

    return f"Directly-Follows Graph:\n{dfg_text}\n\nProcess Variants:\n{variants_text}"


def extract_activity_names(log_obj, activity_key: str = "concept:name") -> list:
    """Extract unique activity names from an event log."""
    import pm4py
    return sorted(
        pm4py.get_event_attribute_values(log_obj, activity_key).keys()
    )


def create_training_example(
    log_path: str,
    discovery_variant=None,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
):
    """Create a DSPy training example from an event log file.

    Returns a dspy.Example with:
    - log_abstraction (input): textual DFG + variants
    - powl_model (output): ground truth POWL string
    - event_log (not input): for conformance checking in metric
    - expected_activities (not input): for coverage checking
    """
    import dspy
    import pm4py

    if log_path.endswith(".xes") or log_path.endswith(".xes.gz"):
        log = pm4py.read_xes(log_path)
    elif log_path.endswith(".csv"):
        import pandas as pd
        df = pd.read_csv(log_path)
        log = pm4py.format_dataframe(df)
    else:
        import pandas as pd
        df = pd.read_csv(log_path)
        log = pm4py.format_dataframe(df)

    ground_truth_powl = pm4py.discover_powl(
        log,
        variant=discovery_variant,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )

    abstraction = create_log_abstraction(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )

    activities = extract_activity_names(log, activity_key=activity_key)

    return dspy.Example(
        log_abstraction=abstraction,
        powl_model=str(ground_truth_powl),
        event_log=log,
        expected_activities=activities,
    ).with_inputs("log_abstraction")


def load_training_data(
    log_paths: list,
    discovery_variant: str = "maximal",
    shuffle_seed: int = 0,
    train_ratio: float = 0.3,
    dev_ratio: float = 0.3,
):
    """Load event logs and split into train/dev/test sets.

    Parameters
    ----------
    log_paths : list of str
        Paths to event log files (XES or CSV).
    discovery_variant : str
        POWL discovery variant for ground truth.
    shuffle_seed : int
        Random seed for shuffling.
    train_ratio : float
        Fraction of data for training (rest split equally dev/test).

    Returns
    -------
    tuple of (trainset, devset, testset)
    """
    import warnings

    examples = []
    for path in log_paths:
        if not os.path.exists(path):
            warnings.warn(f"Log file not found: {path}")
            continue
        try:
            example = create_training_example(path, discovery_variant=discovery_variant)
            examples.append(example)
        except Exception as e:
            warnings.warn(f"Failed to create example from {path}: {e}")

    random.Random(shuffle_seed).shuffle(examples)

    n = len(examples)
    n_train = int(n * train_ratio)
    n_dev = int(n * dev_ratio)

    trainset = examples[:n_train]
    devset = examples[n_train:n_train + n_dev]
    testset = examples[n_train + n_dev:]

    return trainset, devset, testset
