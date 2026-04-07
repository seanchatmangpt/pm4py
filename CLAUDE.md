# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PM4Py is a Python process mining library (v2.7.22.1) providing state-of-the-art algorithms for process discovery, conformance checking, and analysis. Licensed AGPL-3.0.

This fork also includes `powl-wasm/` — a Rust crate compiling POWL v2 (Partially Ordered Workflow Language) to WebAssembly for browser-native process mining.

## Build & Development Commands

### Python (pm4py)

```bash
pip install -e .                  # Editable install
python tests/execute_tests.py     # Full test suite (primary runner, unittest-based)
python -m pm4py.cli               # CLI interface
python -m pytest tests/           # Also works (pytest runs unittest tests)
python -m pytest tests/alpha_test.py -k "test_name"  # Single test

# NL → POWL → BPMN (AI-assisted process discovery)
python -m pm4py.cli DiscoverPOWLFromText "A customer orders a product..." output.powl
python -m pm4py.cli DiscoverPOWLToBPMN "A customer orders a product..." output.bpmn
python -m pm4py.cli DiscoverPOWLToBPMN process_description.txt output.bpmn
python -m pm4py.cli DiscoverPOWL running-example.xes output.powl
```

Test config lives in `tests/config/test_config.py`. The primary test runner is `execute_tests.py` (unittest). It dynamically loads test classes from an `enabled_tests` list and conditionally includes Polars tests if `polars` is installed.

### Documentation

```bash
cd docs && bash build.sh          # Sphinx docs build (pydata_sphinx_theme)
```

### Rust / WASM (powl-wasm)

```bash
cd powl-wasm
cargo build                       # Build native
cargo test                        # Run Rust tests
wasm-pack test --headless --firefox  # WASM tests in browser

# JS/TS browser client
cd js
npm install
npm run build:wasm                # Build WASM via wasm-pack
npm run build:ts                  # Build TypeScript bundle
npm run dev                       # Dev server with HMR
npm run demo                      # Demo page
npm run test                      # WASM browser tests
```

### Docker

```bash
docker build -t pm4py .
```

## Architecture

### Python Package (`pm4py/`)

The public API is exposed through flat modules at the package root — `pm4py.read`, `pm4py.discovery`, `pm4py.conformance`, `pm4py.filtering`, `pm4py.vis`, etc. These delegate to implementations in:

- **`pm4py/algo/`** — Algorithm implementations organized by domain: `discovery/`, `conformance/`, `filtering/`, `analysis/`, `evaluation/`, `simulation/`, etc. Each contains multiple variant implementations with a factory selection mechanism.
- **`pm4py/objects/`** — Core data structures: `petri_net/`, `process_tree/`, `bpmn/`, `dfg/`, `powl/`, `ocel/` (object-centric event logs), `log/`, `transition_system/`.
- **`pm4py/util/`** — Shared utilities: `pandas_utils.py`, `variants_util.py`, `xes_constants.py`, `dt_parsing/`, `prefixspan.py`, `lp/` (linear programming), `compression/`.
- **`pm4py/statistics/`** — Event log and dataframe statistics.
- **`pm4py/streaming/`** — Streaming event log processing.
- **`pm4py/visualization/`** — Visualization backends.

### POWL Rust/WASM Crate (`powl-wasm/`)

**Documentation:**
- **[README.md](powl-wasm/README.md)** — Project overview, quick start, features
- **[docs/architecture.md](powl-wasm/docs/architecture.md)** — Module organization, data structures, algorithms
- **[docs/tutorial.md](powl-wasm/docs/tutorial.md)** — Getting started guide with examples
- **[docs/reference.md](powl-wasm/docs/reference.md)** — Complete API documentation
- **[docs/quick-reference.md](powl-wasm/docs/quick-reference.md)** — Common operations and patterns
- **[docs/troubleshooting.md](powl-wasm/docs/troubleshooting.md)** — Common issues and solutions
- **[docs/vision-2030.md](powl-wasm/docs/vision-2030.md)** — Roadmap and future directions

**Module Structure:**
- **`src/lib.rs`** — wasm-bindgen entry point, arena-based `PowlModel` storage. All nodes referenced by `u32` index; root is always the last node.
- **`src/powl.rs`** — POWL v2 node types (silent, visible, operator nodes: sequence, parallel, loop, choice, move_merge, silent_move_merge, transitive).
- **`src/parser.rs`** — Parses POWL model strings (same format as Python `__repr__`).
- **`src/binary_relation.rs`** — Bit-packed `BinaryRelation` with Warshall's algorithm for transitive closure/reduction.
- **`src/petri_net.rs`** — Petri net conversion with `Place`, `Transition`, `Arc` types.
- **`src/footprints.rs`** — Behavioral signature extraction.
- **`src/conformance/token_replay.rs`** — Token-based replay conformance checking.
- **`src/event_log.rs`** — XES/CSV event log parsing.
- **`src/streaming.rs`** — Streaming drift detection with EWMA smoothing.
- **`src/diff.rs`** — Behavioral diff between two POWL models.
- **`src/complexity.rs`** — Model complexity metrics.
- **`src/conversion/`** — Converters to BPMN, Petri nets, process trees.
- **`src/algorithms/`** — Label replacing, simplification, transitive operations.
- **`js/`** — TypeScript/Vite browser client wrapping the WASM output.

### DSPy POWL Generation (`pm4py/algo/dspy/powl/`)

AI-assisted process model generation and verification using DSPy framework:

- **`natural_language.py`** — NL → POWL generation with judge-refinement loop. `generate_powl_from_text(description)` returns verified POWL model.
- **`judge.py`** — "Dr. van der Aalst" POWL quality judge. Evaluates structural soundness (deadlock freedom, liveness, boundedness) without ground truth.
- **`nl_demos.py`** — 4 few-shot demos: loan approval, software release, e-commerce, A2A+MCP multi-agent orchestration.
- **`react_agent.py`** — Event log → POWL agent (programmatic discovery from DFG+variants abstraction).
- **`generation.py`** — Tool functions: `validate_powl()`, `check_activity_coverage()`, `check_fitness()`, `finish()`.
- **`optimize.py`** — SIMBA optimization, LM configuration, agent save/load.
- **`metrics.py`** — Quality metrics: parse-only, structural, conformance.
- **`data.py`** — Training data creation from event logs.
- **`demos.py`** — 5 few-shot demos for event log generation.

### Key Data Flows

```
# Event log discovery (programmatic)
Event log (XES/CSV/Pandas DataFrame)
  → pm4py.read_xes() / pm4py.read_csv()
  → pm4py.discover_petri_net_inductive() / discover_powl()
  → pm4py.check_fitness() / conformance checking
  → pm4py.view_petri_net() / visualization

# NL → POWL → BPMN (AI-assisted, central paradigm)
Natural language description
  → generate_powl_from_text(description)
  → POWLJudge verification + refinement loop
  → parse_powl_model_string()
  → pm4py.convert_to_bpmn() / write_bpmn()
  → BPMN 2.0 XML (open in Camunda, Signavio, etc.)
```

## Python Version & Dependencies

- Supports Python 3.9–3.14 (see `third_party/old_python_deps/` for 3.8)
- Core: numpy, pandas, networkx, graphviz, scipy, lxml, matplotlib
- Optional: openai, scikit-learn, polars, pyarrow, pyvis, workalendar, pyemd

## Test Data

Test event logs and models live in `tests/input_data/`. Compressed variants in `tests/compressed_input_data/`.
