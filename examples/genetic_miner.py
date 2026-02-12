import pm4py
import os
import importlib.util
from examples import examples_conf
from pm4py.algo.discovery.genetic.algorithm import Parameters


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = pm4py.discover_petri_net_genetic(log, population_size = 20, generations = 30)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
