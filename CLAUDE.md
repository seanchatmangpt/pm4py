# CLAUDE.md

PM4Py is a Python process mining library (v2.7.22.1, AGPL-3.0) with `pm4wasm/` — a Rust/WASM crate for browser-native POWL v2 process mining.

## Setup

```bash
# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                    # Core
pip install openai dspy-ai litellm groq  # LLM features

# Prerequisites
brew install graphviz                # macOS (visualization)
```

## Commands

### Python

```bash
pip install -e .                    # Editable install
python tests/execute_tests.py       # Full test suite (unittest-based)
python -m pytest tests/              # Alternative runner
python -m pytest tests/alpha_test.py -k "test_name"  # Single test
python -m pm4py.cli DiscoverPOWLToBPMN "description..." output.bpmn  # NL → BPMN
```

### Rust / WASM (pm4wasm)

```bash
cd pm4wasm
cargo check                         # Type-check (fast)
cargo test                          # 247 tests (245 pass; 2 pre-existing LLM failures)
wasm-pack build --target web --release  # WASM package → pkg/
```

No `Makefile` — use `cargo`/`wasm-pack` directly (global `cargo make` rule doesn't apply here).

WASM binary size budget: <500KB gzipped (currently ~374KB).

### Docker

```bash
docker build -t pm4py .
```

## pm4wasm Patterns

### WASM Export Pattern

All browser-callable functions use `#[wasm_bindgen]` in `src/lib.rs`:

```rust
#[wasm_bindgen]
pub fn my_function(input_json: &str) -> Result<String, JsValue> {
    let input: MyType = serde_json::from_str(input_json)
        .map_err(|e| JsValue::from_str(&format!("JSON error: {}", e)))?;
    let result = my_module::do_thing(&input);
    serde_json::to_string(&result)
        .map_err(|e| JsValue::from_str(&format!("JSON error: {}", e)))
}
```

Prefer `lib.rs` wrappers over `#[wasm_bindgen]` in individual module files.

### Known Test Failures

Two LLM tests always fail (pre-existing, not caused by new work):
- `llm::demos::tests::test_get_demos`
- `llm::judge::tests::test_validate_sound_loop_with_exit`

## Architecture

- **`pm4py/`** — Python package. Public API via flat modules (`pm4py.read`, `pm4py.discovery`, etc.) delegating to `pm4py/algo/` variants. Core types in `pm4py/objects/` (petri_net, powl, bpmn, dfg, ocel).
- **`pm4wasm/`** — Rust/WASM crate. Arena-based `PowlModel` in `src/lib.rs`. Modules: `conformance/` (alignments, token replay, precision, footprints), `discovery/` (inductive, alpha, genetic, correlation, batches, heuristics, log skeleton, declare, temporal profile, performance spectrum), `conversion/` (BPMN, PNML, PTML, DFG, Petri nets, YAWL), `algorithms/` (marking equation, reduction, simplification, transitive), `quality/` (generalization), `streaming/`, `diff/`, `complexity/`, `statistics/`, `filtering/`, `llm/`.
- **`pm4wasm/js/`** — TypeScript/Vite browser client wrapping WASM output.

Full module docs: [pm4wasm/docs/architecture.md](pm4wasm/docs/architecture.md)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `quick_xml` misses self-closing elements | Handle both `Empty` (self-closing `<tag/>`) and `Start`/`End` (non-self-closing `<tag>...</tag>`) events |
| `#[allow(dead_code)]` on struct doesn't suppress field warnings | Place `#[allow(dead_code)]` on each unused field directly |
| Graphviz `ExecutableNotFound` | `brew install graphviz` |
| `ModuleNotFoundError: polars` | `pip install polars pyarrow scikit-learn` |
| WASM build fails on macOS ARM64 | `rustup update` |
| pandas attribute errors | `pip install --upgrade pandas` (>= 3.0.0) |

## Test Data

`tests/input_data/` — event logs and models. Compressed variants in `tests/compressed_input_data/`.
