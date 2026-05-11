import pm4py
from pm4py.algo.transformation.trace_encodings import algorithm as trace_encodings
from pm4py.util import constants
import pandas


def execute_script():
    log: pandas.DataFrame = pm4py.read_xes("../tests/input_data/running-example.xes")

    log_paid = trace_encodings.keep_top_k_per_similarity(log, "paid cases", 2, parameters={
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "concept:name"})
    print(log_paid)

    log_rejected = trace_encodings.keep_top_k_per_similarity(log, "rejected cases", 2, parameters={
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "concept:name"})
    print(log_rejected)


if __name__ == "__main__":
    execute_script()
