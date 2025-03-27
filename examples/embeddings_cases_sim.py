import pm4py
from pm4py.algo.transformation.to_embeddings.variants import cases_transformers


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")

    log_paid = cases_transformers.keep_top_k_per_similarity(log, "paid cases", 2)
    print(log)

    log_rejected = cases_transformers.keep_top_k_per_similarity(log, "rejected cases", 2)
    print(log)


if __name__ == "__main__":
    execute_script()
