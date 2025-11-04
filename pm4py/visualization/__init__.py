from pm4py.util import constants as pm4_constants

if pm4_constants.ENABLE_INTERNAL_IMPORTS:
    import importlib.util

    if importlib.util.find_spec("graphviz"):
        # imports the visualizations only if graphviz is installed
        from pm4py.visualization import (
            common,
            dfg,
            petri_net,
            process_tree,
            transition_system,
            bpmn,
            trie,
            ocel,
            network_analysis,
            heuristics_net
        )

        if importlib.util.find_spec("matplotlib"):
            from pm4py.visualization import performance_spectrum

            if importlib.util.find_spec("pyvis"):
                # SNA requires both packages matplotlib and pyvis.
                from pm4py.visualization import sna

    if importlib.util.find_spec("matplotlib"):
        # graphs require matplotlib. This is included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import graphs
