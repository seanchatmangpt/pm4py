# Coverage report

Measured on 2026-07-17 with coverage.py 7.15.2. Coverage was collected for the entire `pm4py` package with `--source=pm4py`; no files or package paths were omitted. The figures below are statement coverage, including files that were never imported.

## Results

| Measurement | Covered statements | Total statements | Missing statements | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Baseline test suite | 38,770 | 71,387 | 32,617 | 54.31% |
| Baseline tests and examples | 46,242 | 71,387 | 25,145 | 64.78% |
| Expanded test suite | 60,715 | 71,387 | 10,672 | 85.05% |
| Expanded tests and examples | 64,403 | 71,387 | 6,984 | **90.22%** |

The final combined result exceeds the 90% target by 0.22 percentage points. Ten source lines carry coverage.py exclusion pragmas; they are reported as excluded lines rather than omitted files.

## Verification

- Custom test runner: 929 tests discovered, 926 passed, 3 skipped, 0 failed, and 0 import failures (100% pass ratio among executed tests).
- Example runner: 139 examples passed, 4 skipped, and 0 failed (100% pass ratio among executed examples).
- The skipped entries require optional services, platform-specific facilities, or interactive environments that were unavailable during this headless run.
- Headless image-viewer warnings and conformance-diagnostic log messages were expected output; neither runner reported a failure.

The coverage increase comes from 28 focused coverage test modules registered with the existing custom runner. They exercise algorithms, object-centric logs, XES/BPMN I/O, Petri nets and process trees, POWL, Polars analytics, connectors, privacy, serialization, facades, visualizations, and edge/error paths. A small set of existing tests was also updated for current paths, timezone-aware APIs, and the custom runner interface.

## Reproduce

From the repository root, with `coverage` installed:

```bash
export PYTHONPATH="$PWD"
export COVERAGE_FILE="$PWD/.coverage"
export MPLCONFIGDIR=/tmp/pm4py-matplotlib
python -m coverage erase
(cd tests && python -m coverage run --source=pm4py execute_tests.py --pipeline)
(cd examples && python -m coverage run --append --source=pm4py execute_everything.py --pipeline)
python -m coverage report
```

The expanded-test-only snapshot was taken after the first `coverage run`; the final result was taken after appending the example run.
