import pm4py
from pm4py.algo.transformation.trace_encodings import algorithm as trace_encodings
import os
import pandas


def execute_script():
    log: pandas.DataFrame = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    feature_names: list[str]
    data, feature_names = trace_encodings.apply(log, variant=trace_encodings.Variants.TRACE_BASED)
    print(data)
    print(feature_names)
    data, feature_names = trace_encodings.apply(log, variant=trace_encodings.Variants.EVENT_BASED)
    print(data)
    print(feature_names)


if __name__ == "__main__":
    execute_script()
