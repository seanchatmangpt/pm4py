# @pm4py/powl-wasm

Browser-native POWL v2 (Partially Ordered Workflow Language) powered by Rust/WebAssembly.

## Install

```bash
npm install @pm4py/powl-wasm
```

## Quick start

```ts
import { Powl } from "@pm4py/powl-wasm";

const powl = await Powl.init();

// Parse
const model = powl.parse("PO=(nodes={A, B, C}, order={A-->B, A-->C})");
model.validate();                       // throws if invalid
console.log(model.toString());          // canonical string
console.log([...model.activities()]);   // ["A", "B", "C"]

// Convert
const petriNet = model.toPetriNet();
console.log(petriNet.net.transitions.length);

// Parse event log from CSV
const log = powl.parseCsv(
  "case_id,activity\n1,A\n1,B\n1,C\n2,A\n2,C\n"
);

// Check conformance
const fitness = powl.conformance(model, log);
console.log(fitness.percentage);         // 0.0 – 1.0
console.log(fitness.perfectly_fitting_traces);

// Filter by fitness threshold
const goodTraces = powl.filterByFitness(model, log, 0.8);
```

## Build from source

Requires Rust + [wasm-pack](https://rustwasm.github.io/wasm-pack/).

```bash
# Install wasm-pack (once)
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Build WASM then TypeScript
cd js/
npm install
npm run build
```

## Dev / demo server

```bash
npm run demo
# Opens http://localhost:5173 — live POWL editor + conformance checker
```

## Run browser tests

```bash
npm test                   # Firefox headless
# or:
wasm-pack test .. --headless --chrome
```

## API overview

### `Powl.init() → Promise<Powl>`

Loads the WASM module once; safe to call multiple times.

### Parsing

| Method | Description |
|--------|-------------|
| `powl.parse(str)` | Parse a POWL model string |
| `powl.parseXes(xml)` | Parse a XES event log |
| `powl.parseCsv(csv)` | Parse a CSV event log |
| `powl.fetchXes(url)` | Fetch + parse XES from URL |
| `powl.readXesFile(file)` | Parse `File` drag-drop XES |
| `powl.readCsvFile(file)` | Parse `File` drag-drop CSV |

### `PowlModel`

| Method | Description |
|--------|-------------|
| `.toString()` | Canonical model string |
| `.validate()` | Throws on SPO violations |
| `.simplify()` | Structure-normalized model |
| `.simplifyFrequent()` | Convert XOR/LOOP+tau → FrequentTransition |
| `.toPetriNet()` | Returns `PetriNetResult` |
| `.nodeInfo(idx)` | Typed node description |
| `.children(idx)` | Child arena indices |
| `.activities()` | All activity labels |
| `.walk(visitor)` | Pre-order tree traversal |
| `.orderEdges(idx)` | SPO ordering relation edge list |
| `.closureEdges(idx)` | Transitive closure edge list |
| `.reductionEdges(idx)` | Transitive reduction edge list |

### Conformance

| Method | Description |
|--------|-------------|
| `powl.conformance(model, log)` | Token-replay fitness |
| `powl.conformancePetriNet(pn, log)` | Fitness against pre-built Petri net |
| `powl.filterByFitness(model, log, threshold)` | Filter traces by fitness |
| `powl.variants(log)` | Variant frequency map |
