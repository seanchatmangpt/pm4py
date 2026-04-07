'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

import pm4py
import sys
import os
import itertools
from pathlib import Path
import traceback
import pandas as pd
from pm4py.util import constants, pandas_utils
import platform
import importlib.util
import subprocess


methods = {
    "Doctor": {
        "inputs": [],
        "output_extension": None,
        "method": lambda x: doctor_command(),
    },
    "ConvertToXES": {
        "inputs": [".csv"],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.convert_to_event_log(
                pm4py.format_dataframe(pandas_utils.read_csv(x[0]))
            ),
            x[1],
        ),
    },
    "ConvertToCSV": {
        "inputs": [".xes"],
        "output_extension": ".csv",
        "method": lambda x: pm4py.convert_to_dataframe(
            pm4py.read_xes(x[0])
        ).to_csv(x[1], index=False),
    },
    "ConvertPNMLtoBPMN": {
        "inputs": [".pnml"],
        "output_extension": ".bpmn",
        "method": lambda x: pm4py.write_bpmn(
            pm4py.convert_to_bpmn(*pm4py.read_pnml(x[0])), x[1]
        ),
    },
    "ConvertPNMLtoPTML": {
        "inputs": [".pnml"],
        "output_extension": ".ptml",
        "method": lambda x: pm4py.write_ptml(
            pm4py.convert_to_process_tree(*pm4py.read_pnml(x[0])), x[1]
        ),
    },
    "ConvertPTMLtoPNML": {
        "inputs": [".ptml"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.convert_to_petri_net(pm4py.read_ptml(x[0])), x[1]
        ),
    },
    "ConvertPTMLtoBPMN": {
        "inputs": [".ptml"],
        "output_extension": ".bpmn",
        "method": lambda x: pm4py.write_bpmn(
            pm4py.convert_to_bpmn(pm4py.read_ptml(x[0])), x[1]
        ),
    },
    "ConvertBPMNtoPNML": {
        "inputs": [".bpmn"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.convert_to_petri_net(pm4py.read_bpmn(x[0])), x[1]
        ),
    },
    "ConvertDFGtoPNML": {
        "inputs": [".dfg"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.convert_to_petri_net(*pm4py.read_dfg(x[0])), x[1]
        ),
    },
    "DiscoverPetriNetAlpha": {
        "inputs": [".xes"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.discover_petri_net_alpha(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverPetriNetInductive": {
        "inputs": [".xes"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.discover_petri_net_inductive(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverPetriNetHeuristics": {
        "inputs": [".xes"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.discover_petri_net_heuristics(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverPetriNetGenetic": {
        "inputs": [".xes"],
        "output_extension": ".pnml",
        "method": lambda x: pm4py.write_pnml(
            *pm4py.discover_petri_net_genetic(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverBPMNInductive": {
        "inputs": [".xes"],
        "output_extension": ".bpmn",
        "method": lambda x: pm4py.write_bpmn(
            pm4py.discover_bpmn_inductive(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverProcessTreeInductive": {
        "inputs": [".xes"],
        "output_extension": ".ptml",
        "method": lambda x: pm4py.write_ptml(
            pm4py.discover_process_tree_inductive(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverDFG": {
        "inputs": [".xes"],
        "output_extension": ".dfg",
        "method": lambda x: pm4py.write_dfg(
            *pm4py.discover_dfg(__read_log(x[0])), x[1]
        ),
    },
    "ConformanceDiagnosticsTBR": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.conformance_diagnostics_token_based_replay(
                    __read_log(x[0]),
                    *pm4py.read_pnml(x[1]),
                    return_diagnostics_dataframe=False
                )
            )
        ),
    },
    "ConformanceDiagnosticsAlignments": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.conformance_diagnostics_alignments(
                    __read_log(x[0]),
                    *pm4py.read_pnml(x[1]),
                    return_diagnostics_dataframe=False
                )
            )
        ),
    },
    "FitnessTBR": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.fitness_token_based_replay(
                    __read_log(x[0]), *pm4py.read_pnml(x[1])
                )
            )
        ),
    },
    "FitnessAlignments": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.fitness_alignments(
                    __read_log(x[0]), *pm4py.read_pnml(x[1])
                )
            )
        ),
    },
    "PrecisionTBR": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.precision_token_based_replay(
                    __read_log(x[0]), *pm4py.read_pnml(x[1])
                )
            )
        ),
    },
    "PrecisionAlignments": {
        "inputs": [".xes", ".pnml"],
        "output_extension": ".txt",
        "method": lambda x: open(x[2], "w").write(
            str(
                pm4py.precision_alignments(
                    __read_log(x[0]), *pm4py.read_pnml(x[1])
                )
            )
        ),
    },
    "SaveVisDFG": {
        "inputs": [".dfg"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_dfg(*pm4py.read_dfg(x[0]), x[1]),
    },
    "SaveVisPNML": {
        "inputs": [".pnml"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_petri_net(
            *pm4py.read_pnml(x[0]), x[1]
        ),
    },
    "SaveVisBPMN": {
        "inputs": [".bpmn"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_bpmn(pm4py.read_bpmn(x[0]), x[1]),
    },
    "SaveVisPTML": {
        "inputs": [".ptml"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_process_tree(
            pm4py.read_ptml(x[0]), x[1]
        ),
    },
    "SaveVisDottedChart": {
        "inputs": [".xes", None, None, None],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_dotted_chart(
            __read_log(x[0]), x[4], attributes=[x[1], x[2], x[3]]
        ),
    },
    "SaveVisTransitionSystem": {
        "inputs": [".xes"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_transition_system(
            pm4py.discover_transition_system(__read_log(x[0])), x[1]
        ),
    },
    "SaveVisTrie": {
        "inputs": [".xes"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_prefix_tree(
            pm4py.discover_prefix_tree(__read_log(x[0])), x[1]
        ),
    },
    "SaveVisEventsDistribution": {
        "inputs": [".xes", None],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_events_distribution_graph(
            __read_log(x[0]), x[2], distr_type=x[1]
        ),
    },
    "SaveVisEventsPerTime": {
        "inputs": [".xes"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_events_per_time_graph(
            __read_log(x[0]), x[1]
        ),
    },
    "GenerateProcessTree": {
        "inputs": [None],
        "output_extension": ".ptml",
        "method": lambda x: pm4py.write_ptml(
            pm4py.generate_process_tree(
                parameters={
                    "min": int(x[0]),
                    "max": int(x[0]),
                    "mode": int(x[0]),
                }
            ),
            x[1],
        ),
    },
    "PNMLplayout": {
        "inputs": [".pnml"],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.play_out(*pm4py.read_pnml(x[0])), x[1]
        ),
    },
    "PTMLplayout": {
        "inputs": [".ptml"],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.play_out(pm4py.read_ptml(x[0])), x[1]
        ),
    },
    "DFGplayout": {
        "inputs": [".dfg"],
        "output_extension": ".dfg",
        "method": lambda x: pm4py.write_xes(
            pm4py.play_out(*pm4py.read_dfg(x[0])), x[1]
        ),
    },
    "SaveVisSNA": {
        "inputs": [".xes", None],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_sna(
            __apply_sna(__read_log(x[0]), x[1]), x[2]
        ),
    },
    "SaveVisCaseDuration": {
        "inputs": [".xes"],
        "output_extension": ".png",
        "method": lambda x: pm4py.save_vis_case_duration_graph(
            __read_log(x[0]), x[1]
        ),
    },
    "FilterVariantsTopK": {
        "inputs": [".xes", None],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.filter_variants_top_k(__read_log(x[0]), int(x[1])), x[2]
        ),
    },
    "FilterVariantsCoverage": {
        "inputs": [".xes", None],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.filter_variants_by_coverage_percentage(
                __read_log(x[0]), float(x[1])
            ),
            x[2],
        ),
    },
    "FilterCasePerformance": {
        "inputs": [".xes", None, None],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.filter_case_performance(
                __read_log(x[0]),
                min_performance=float(x[1]),
                max_performance=float(x[2]),
            ),
            x[3],
        ),
    },
    "FilterTimeRange": {
        "inputs": [".xes", None, None],
        "output_extension": ".xes",
        "method": lambda x: pm4py.write_xes(
            pm4py.filter_time_range(
                __read_log(x[0]), x[1] + " 00:00:00", x[2] + " 23:59:59"
            ),
            x[3],
        ),
    },
    "DiscoverPOWL": {
        "inputs": [".xes"],
        "output_extension": ".powl",
        "method": lambda x: __write_powl(
            pm4py.discover_powl(__read_log(x[0])), x[1]
        ),
    },
    "DiscoverPOWLFromText": {
        "inputs": [None],
        "output_extension": ".powl",
        "method": lambda x: __write_powl_from_text(x[0], x[1]),
    },
    "DiscoverPOWLToBPMN": {
        "inputs": [None],
        "output_extension": ".bpmn",
        "method": lambda x: __write_powl_to_bpmn(x[0], x[1]),
    },
}


def __read_log(log_path):
    if "xes" in log_path.lower():
        return pm4py.read_xes(log_path)
    elif "csv" in log_path.lower():
        dataframe = pandas_utils.read_csv(log_path)
        dataframe = pm4py.format_dataframe(dataframe)
        return dataframe


def __apply_sna(log, method, **kwargs):
    if method == "handover":
        return pm4py.discover_handover_of_work_network(log, **kwargs)
    elif method == "working_together":
        return pm4py.discover_working_together_network(log, **kwargs)
    elif method == "similar_activities":
        return pm4py.discover_activity_based_resource_similarity(log, **kwargs)
    elif method == "subcontracting":
        return pm4py.discover_subcontracting_network(log, **kwargs)


def __get_output_name(inp_list, idx, method_name, extension):
    ret = []
    for inp in inp_list:
        ret.append(str(Path(inp).stem))
    return "_".join(ret) + "_" + method_name + extension


def __write_powl(powl_model, output_path):
    with open(output_path, "w") as f:
        f.write(str(powl_model))
    print("POWL model written to", output_path)


def __write_powl_from_text(description_or_path, output_path):
    import os as _os
    # If it's a file path, read the description from file
    if _os.path.exists(description_or_path):
        with open(description_or_path, "r") as f:
            description = f.read()
    else:
        description = description_or_path

    from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text
    result = generate_powl_from_text(description, max_refinements=1)

    with open(output_path, "w") as f:
        f.write(result["powl"])

    verdict_str = "VERIFIED" if result["verdict"] else "NOT VERIFIED"
    print(f"POWL model ({verdict_str}, {result['refinements']} refinements) written to {output_path}")
    if result["reasoning"]:
        print(f"Judge: {result['reasoning'][:200]}...")


def doctor_command():
    """
    Run comprehensive health checks on pm4py installation.

    Checks:
    - Python version compatibility
    - Core dependencies (numpy, pandas, etc.)
    - Optional dependencies (scikit-learn, graphviz, etc.)
    - pm4py installation integrity
    - File permissions and directory access
    - Test suite health
    - Visualization backends
    """
    print("=" * 70)
    print("PM4Py Doctor - Health Check")
    print("=" * 70)
    print()

    # Track overall health
    issues = []
    warnings = []
    passes = []

    # 1. Python Version Check
    print("🐍 Python Version")
    print("-" * 40)
    python_version = sys.version_info
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    print(f"Python: {version_str}")
    print(f"Platform: {platform.system()} {platform.release()}")

    # Check if Python version is supported (3.9+)
    if python_version >= (3, 9):
        passes.append("✅ Python version supported")
    else:
        issues.append("❌ Python version not supported (requires 3.9+)")
    print()

    # 2. Core Dependencies
    print("📦 Core Dependencies")
    print("-" * 40)
    core_deps = [
        ("numpy", "Numerical computing"),
        ("pandas", "Data manipulation"),
        ("networkx", "Graph algorithms"),
        ("lxml", "XML parsing"),
        ("scipy", "Scientific computing"),
        ("matplotlib", "Visualization"),
        ("graphviz", "Graph visualization"),
    ]

    for module, description in core_deps:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", "unknown")
            passes.append(f"✅ {module} ({version}) - {description}")
        except ImportError:
            issues.append(f"❌ {module} - {description} (MISSING)")
        except Exception as e:
            warnings.append(f"⚠️  {module} - {description} (ERROR: {str(e)[:50]})")

    print()

    # 3. Optional Dependencies
    print("📦 Optional Dependencies")
    print("-" * 40)
    optional_deps = [
        ("sklearn", "scikit-learn", "Machine learning"),
        ("cvxopt", "CVXOPT", "Linear programming (ILP miner)"),
        ("polars", "Polars", "Fast dataframe operations"),
        ("pyarrow", "PyArrow", "Columnar data format"),
        ("pyvis", "PyVis", "Interactive visualization"),
        ("workalendar", "Workalendar", "Business calendars"),
        ("pyemd", "PyEMD", "Earth mover's distance"),
        ("deprecation", "Deprecation utilities", "Optional"),
    ]

    for dep_info in optional_deps:
        if len(dep_info) == 3:
            module, display_name, description = dep_info
        else:
            module, description = dep_info
            display_name = module

        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", "unknown")
            passes.append(f"✅ {display_name} ({version}) - {description}")
        except ImportError:
            warnings.append(f"⚠️  {display_name} - {description} (optional, not installed)")
        except Exception as e:
            warnings.append(f"⚠️  {display_name} - {description} (ERROR: {str(e)[:50]})")

    print()

    # 4. pm4py Installation Integrity
    print("🔧 pm4py Installation")
    print("-" * 40)
    try:
        import pm4py
        pm4py_version = pm4py.__version__
        passes.append(f"✅ pm4py {pm4py_version} installed")

        # Check key submodules
        key_modules = [
            "pm4py.discovery",
            "pm4py.conformance",
            "pm4py.filtering",
            "pm4py.stats",
            "pm4py.vis",
            "pm4py.convert",
            "pm4py.analysis",
            "pm4py.dx",  # Our new DX module
        ]

        for module in key_modules:
            try:
                importlib.import_module(module)
                passes.append(f"✅ {module} accessible")
            except ImportError:
                issues.append(f"❌ {module} not accessible")

    except ImportError as e:
        issues.append(f"❌ pm4py not installed: {e}")

    print()

    # 5. File Permissions and Directory Access
    print("📁 File System")
    print("-" * 40)
    import tempfile

    # Test temp directory access
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_pm4py.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        passes.append("✅ Temp directory accessible")
    except Exception as e:
        issues.append(f"❌ Temp directory error: {e}")

    # Test current directory write access
    try:
        test_file = "pm4py_doctor_test.tmp"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        passes.append("✅ Current directory writable")
    except Exception as e:
        issues.append(f"❌ Current directory error: {e}")

    print()

    # 6. Visualization Backends
    print("🎨 Visualization Backends")
    print("-" * 40)

    # Check Graphviz
    try:
        import graphviz
        # Try to create a simple digraph
        dot = graphviz.Digraph()
        dot.node("A")
        passes.append("✅ Graphviz (Python bindings)")
    except ImportError:
        warnings.append("⚠️  Graphviz Python bindings not installed")
    except Exception as e:
        warnings.append(f"⚠️  Graphviz error: {e}")

    # Check Graphviz binary
    try:
        result = subprocess.run(
            ["dot", "-V"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0] if result.stderr else ""
            passes.append(f"✅ Graphviz binary ({version_line.split()[1]})")
        else:
            warnings.append("⚠️  Graphviz binary not found in PATH")
    except FileNotFoundError:
        warnings.append("⚠️  Graphviz binary not found in PATH")
    except Exception as e:
        warnings.append(f"⚠️  Graphviz binary error: {e}")

    print()

    # 7. Basic Functionality Tests
    print("🧪 Basic Functionality")
    print("-" * 40)

    # Test creating a simple event log
    try:
        from pm4py.objects.log.obj import Event, EventLog, Trace
        trace = Trace([Event({"concept:name": "A"})])
        log = EventLog([trace])
        passes.append("✅ Event log creation works")
    except Exception as e:
        issues.append(f"❌ Event log creation failed: {e}")

    # Test POWL parsing
    try:
        from pm4py.objects.powl.parser import parse_powl_model_string
        model = parse_powl_model_string("X(A, B)")
        passes.append("✅ POWL parsing works")
    except Exception as e:
        issues.append(f"❌ POWL parsing failed: {e}")

    # Test DX utilities
    try:
        from pm4py.dx import log_summary, model_summary
        passes.append("✅ DX utilities accessible")
    except Exception as e:
        issues.append(f"❌ DX utilities failed: {e}")

    # Test discovery
    try:
        from pm4py.objects.log.obj import Event, EventLog, Trace
        trace = Trace([
            Event({"concept:name": "A"}),
            Event({"concept:name": "B"}),
        ])
        log = EventLog([trace])
        model = pm4py.discover_powl(log)
        passes.append("✅ POWL discovery works")
    except Exception as e:
        issues.append(f"❌ POWL discovery failed: {e}")

    print()

    # 8. Environment Information
    print("💻 Environment")
    print("-" * 40)
    print(f"Executable: {sys.executable}")
    print(f"Prefix: {sys.prefix}")
    print(f"Base Prefix: {getattr(sys, 'base_prefix', 'N/A')}")

    # Check for virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        passes.append("✅ Running in virtual environment")
    else:
        warnings.append("⚠️  Not running in virtual environment")

    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {len(passes)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Issues: {len(issues)}")
    print()

    if issues:
        print("CRITICAL ISSUES (must fix):")
        for issue in issues:
            print(f"  {issue}")
        print()

    if warnings:
        print("WARNINGS (recommended fixes):")
        for warning in warnings[:10]:  # Show first 10 warnings
            print(f"  {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings")
        print()

    if not issues and not warnings:
        print("🎉 All checks passed! pm4py is healthy.")
    elif not issues:
        print("✅ No critical issues. pm4py is functional (some optional features may be limited).")
    else:
        print("❌ Critical issues detected. Please fix the problems above for full functionality.")

    print()
    print("For help, visit: https://processintelligence.solutions")
    print("=" * 70)


def __write_powl_to_bpmn(description_or_path, output_path):
    import os as _os
    if _os.path.exists(description_or_path):
        with open(description_or_path, "r") as f:
            description = f.read()
    else:
        description = description_or_path

    from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text
    result = generate_powl_from_text(description, max_refinements=1)
    powl_string = result["powl"]

    if not powl_string:
        raise Exception("Failed to generate POWL model")

    from pm4py.objects.powl.parser import parse_powl_model_string
    parsed = parse_powl_model_string(powl_string)
    if parsed is None:
        raise Exception("Generated POWL could not be parsed")

    # Try direct POWL→BPMN, fall back to POWL→PetriNet→BPMN
    try:
        bpmn_model = pm4py.convert_to_bpmn(parsed)
    except Exception:
        net, im, fm = pm4py.convert_to_petri_net(parsed)
        bpmn_model = pm4py.convert_to_bpmn(net, im, fm)

    pm4py.write_bpmn(bpmn_model, output_path)

    verdict_str = "VERIFIED" if result["verdict"] else "NOT VERIFIED"
    print(f"BPMN model ({verdict_str}) written to {output_path}")


def cli_interface():
    method_name = sys.argv[1]
    if method_name in methods:
        method = methods[method_name]

        # Special handling for Doctor command (no inputs/outputs)
        if method_name == "Doctor":
            try:
                method["method"]([])
                return
            except BaseException:
                traceback.print_exc()
                return

        inputs = []
        for i in range(len(method["inputs"])):
            ci = sys.argv[2 + i] if len(sys.argv) > 2 + i else None
            if ci is None:
                break  # Missing required argument

            if os.path.isdir(ci):
                if not os.path.exists(ci):
                    raise Exception(
                        "the provided path (" + ci + ") does not exist."
                    )
                files = os.listdir(ci)
                inputs.append(
                    [
                        os.path.join(ci, f)
                        for f in files
                        if os.path.isfile(os.path.join(ci, f))
                        and f.endswith(method["inputs"][i])
                    ]
                )
            else:
                inputs.append([ci])

        if not inputs and method["inputs"]:
            # Command requires inputs but none provided
            raise Exception(f"Missing required inputs for {method_name}")

        j = 2 + len(method["inputs"])
        inputs = list(itertools.product(*inputs))
        if len(inputs) == 1:
            outputs = [[sys.argv[j]]] if len(sys.argv) > j else [None]
        else:
            if not os.path.exists(sys.argv[j]):
                os.mkdir(sys.argv[j])
            outputs = [
                [
                    os.path.join(
                        sys.argv[j],
                        __get_output_name(
                            inputs[z],
                            z,
                            method_name,
                            method["output_extension"],
                        ),
                    )
                ]
                for z in range(len(inputs))
            ]
        method_tuples = [(*inputs[i], *outputs[i]) for i in range(len(inputs))]
        for i in range(len(method_tuples)):
            try:
                if method_tuples[i][-1] is not None and not os.path.exists(method_tuples[i][-1]):
                    print(method_name, method_tuples[i])
                    method["method"](method_tuples[i])
            except BaseException:
                traceback.print_exc()
    else:
        raise Exception(
            "the provided method ("
            + method_name
            + ") does not exist in the CLI."
        )


if __name__ == "__main__":
    cli_interface()
