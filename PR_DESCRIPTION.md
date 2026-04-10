# PR Description: POWL 2.0 Choice Graph (PM×) Inductive Miner

---

## Summary

This PR adds support for **Choice Graphs** (non-block-structured decisions) to PM4Py's POWL discovery, implementing the PM× (Inductive Miner with Choice Graphs) algorithm from:

> **H Kourani, G Park, WMP van der Aalst.** "Unlocking Non-Block-Structured Decisions: Inductive Mining with Choice Graphs" arXiv:2505.07052.

---

## Motivation

Current POWL discovery uses block-structured XOR operators for choices, which cannot model:
- ❌ Overlapping choice regions (activities in multiple branches)
- ❌ Cancellation within branches
- ❌ Non-block-structured workflow patterns (43 patterns reference)

**Choice Graphs** extend POWL to handle these cases while maintaining:
- ✅ Soundness guarantees
- ✅ Fitness preservation (Lemma 1)
- ✅ Efficient discovery (MineDG algorithm)

---

## What's Included

### 🎯 New Discovery Variants (4)

| Variant | Description |
|---------|-------------|
| `DECISION_GRAPH_MAX` | Maximal partial order detection |
| `DECISION_GRAPH_CLUSTERING` | Frequency-based clustering |
| `DECISION_GRAPH_CYCLIC` | Cycle-aware discovery |
| `DECISION_GRAPH_CYCLIC_STRICT` | Strict acyclicity validation |

### 🔧 New Features

- **Algorithm 1 (MineDG)** - Choice graph discovery from event logs
- **Definition 3 (Language)** - `L(G)` computation for model language
- **Definition 5 (Valid Cuts)** - Cut detection and validation
- **Soundness Validation** - Connectivity, acyclicity, structural soundness
- **Visualization** - Blue dashed arcs for choice graph edges (paper's Figure 2)

---

## Files Added (13 files)

### Core Implementation
```
pm4py/objects/powl/
├── choice_graph_discovery.py     # MineDG, valid cuts, language semantics
├── frequency.py                   # FrequencyTagged mixin
├── types.py                      # ModelType enum
├── graph_base.py                 # GraphTraversable, StartEndNodes
├── serializable.py               # to_dict/from_dict
├── enhanced.py                   # EnhancedTransition, EnhancedChoiceGraph
├── compat.py                     # API compatibility layer
├── api.py                        # Top-level functions
└── extensions.py                 # GuardCondition, CancellationScope
```

### Inductive Miner
```
pm4py/algo/discovery/powl/inductive/variants/
└── im_choice_graph.py            # PM× with all 4 variants
```

### Tests & Examples
```
tests/tests_objects/
├── test_powl2_complete.py        # Integration tests (19 tests)
└── test_powl_extensions.py       # Unit tests

examples/
└── powl_choice_graph_example.py  # Usage examples
```

---

## Files Modified (6 files)

- `pm4py/objects/powl/obj.py` - Added DecisionGraph methods (get_edges, language, validate_soundness)
- `pm4py/objects/powl/BinaryRelation.py` - Added get_preset/get_postset methods
- `pm4py/algo/discovery/powl/algorithm.py` - Added variant mappings
- `pm4py/algo/discovery/powl/inductive/variants/powl_discovery_varaints.py` - Added enum values
- `pm4py/visualization/powl/variants/basic.py` - Added blue dashed arcs
- `pm4py/objects/powl/__init__.py` - Updated exports

---

## Example Usage

```python
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.powl import algorithm as powl_algorithm
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant

# Create event log
log = EventLog([
    Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
    Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'c'})]),
])

# Discover using Choice Graph variant
model = powl_algorithm.apply(
    log,
    variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX
)

# Soundness validation
if isinstance(model, DecisionGraph):
    report = model.get_soundness_report()
    print(f"Sound: {report['is_sound']}")
    print(f"Nodes: {report['metrics']['num_nodes']}")
    print(f"Edges: {report['metrics']['num_edges']}")
```

See `examples/powl_choice_graph_example.py` for more examples.

---

## Tests

✅ **All 19 tests passing**

- Unit tests for MineDG, valid cuts, projection, language semantics
- Integration tests for all 4 DecisionGraph variants
- Soundness validation tests
- Fitness preservation tests (Lemma 1)

```bash
pytest tests/tests_objects/test_powl2_complete.py -v
```

---

## Backwards Compatibility

✅ **Fully backwards compatible**
- All existing POWL functionality unchanged
- New variants are opt-in via `variant` parameter
- No breaking changes to existing APIs

---

## How to Review

1. **Start with the example**: `examples/powl_choice_graph_example.py`
2. **Read the paper**: arXiv:2505.07052 (sections 1-4 provide context)
3. **Check the tests**: `tests/tests_objects/test_powl2_complete.py`
4. **Key files to review**:
   - `choice_graph_discovery.py` - Core algorithms
   - `im_choice_graph.py` - Inductive miner implementation
   - `obj.py` (DecisionGraph section) - Soundness validation

---

## Implementation Notes

- **License**: All code is AGPL-3.0 (compatible with PM4Py)
- **Type Hints**: Complete type annotations throughout
- **Documentation**: Docstrings on all public APIs
- **Code Style**: Follows PM4Py conventions (IMBasePOWL framework, UVCL, Parameters)

---

## References

- Paper: https://arxiv.org/abs/2505.07052
- Branch: `feature/powl-choice-graph` on seanchatmangpt/pm4py
- Commit: `6bae527a1`

---

## Checklist

- [x] Code follows PM4Py style guidelines
- [x] All files have AGPL-3.0 license headers
- [x] Type hints included
- [x] Docstrings included
- [x] Tests added (19 tests, all passing)
- [x] Backwards compatible
- [x] Example code provided
- [x] Fixed encoding issues (en-dash → hyphen)
- [x] Removed duplicate module docstrings

---

## Related Issues

Closes (if applicable): 

---

## Screenshots (Optional)

If helpful, I can add screenshots showing:
- Choice graph visualization with blue dashed arcs
- Soundness validation report example
- Comparison with block-structured XOR discovery

---

**Ready for review!** 🚀
