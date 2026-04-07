/**
 * @pm4py/powl-wasm
 *
 * High-level TypeScript API for the POWL v2 Rust/WASM library.
 *
 * Usage:
 * ```ts
 * import { Powl } from "@pm4py/powl-wasm";
 *
 * const powl = await Powl.init();
 * const model = powl.parse("X(A, B)");
 * console.log(model.toString());       // "X ( A, B )"
 * const pn = model.toPetriNet();
 * const fitness = powl.conformance(pn, log);
 * ```
 */

import type {
  EventLog,
  FitnessResult,
  Footprints,
  NodeInfo,
  PetriNetResult,
} from "./types.js";

export type * from "./types.js";

// ─── Lazy WASM loader ─────────────────────────────────────────────────────────

type WasmModule = typeof import("../pkg/powl_wasm.js");
let _wasm: WasmModule | null = null;

async function getWasm(): Promise<WasmModule> {
  if (!_wasm) {
    const mod = await import("../pkg/powl_wasm.js");
    await mod.default(); // run wasm-bindgen init + start()
    _wasm = mod;
  }
  return _wasm;
}

// ─── PowlModel handle ─────────────────────────────────────────────────────────

/**
 * An opaque handle to a parsed POWL model in WASM memory.
 *
 * Obtain via `Powl.parse()` — do not construct directly.
 */
export class PowlModel {
  /** @internal */
  constructor(
    /** @internal */ private readonly _wm: WasmModule,
    /** @internal */ private readonly _handle: InstanceType<WasmModule["PowlModel"]>,
  ) {}

  /** Arena index of the root node. */
  get root(): number {
    return this._handle.root();
  }

  /** Total number of nodes in the arena. */
  get size(): number {
    return this._handle.len();
  }

  /** Canonical string representation (matches Python `__repr__`). */
  toString(): string {
    return this._wm.powl_to_string(this._handle);
  }

  /** Return typed info about a node by arena index. */
  nodeInfo(arenaIdx: number): NodeInfo {
    return JSON.parse(this._wm.node_info_json(this._handle, arenaIdx)) as NodeInfo;
  }

  /** Child arena indices of an operator or SPO node; empty for leaves. */
  children(arenaIdx: number): number[] {
    return Array.from(this._wm.get_children(this._handle, arenaIdx));
  }

  /** String representation of one node. */
  nodeToString(arenaIdx: number): string {
    return this._wm.node_to_string(this._handle, arenaIdx);
  }

  /**
   * Validate all StrictPartialOrder nodes.
   * @throws {Error} if any violation is found.
   */
  validate(): void {
    this._wm.validate_partial_orders(this._handle);
  }

  /** Return a new simplified model (structure-normalized). */
  simplify(): PowlModel {
    return new PowlModel(this._wm, this._wm.simplify_powl(this._handle));
  }

  /** Convert XOR(A,tau) / LOOP(A,tau) patterns to FrequentTransitions. */
  simplifyFrequent(): PowlModel {
    return new PowlModel(this._wm, this._wm.simplify_frequent_transitions(this._handle));
  }

  /** Convert to Petri net. */
  toPetriNet(): PetriNetResult {
    return JSON.parse(
      this._wm.powl_to_petri_net(this.toString()),
    ) as PetriNetResult;
  }

  /**
   * Compute footprints (behavioural signature).
   *
   * @returns JSON-parsed footprints object.
   */
  footprints(): Footprints {
    // footprints are computed node-by-node internally; expose as JSON
    // by re-parsing and calling the internal API
    throw new Error(
      "footprints() not yet wired as a direct WASM export — use Powl.footprints(model)",
    );
  }

  /**
   * Walk every node in the tree, depth-first (pre-order).
   * Calls `visitor(arenaIdx, info)` for each node.
   */
  walk(visitor: (idx: number, info: NodeInfo) => void): void {
    const visit = (idx: number): void => {
      const info = this.nodeInfo(idx);
      visitor(idx, info);
      for (const child of this.children(idx)) {
        visit(child);
      }
    };
    visit(this.root);
  }

  /**
   * Collect all activity labels in the model (leaf Transitions with non-null label).
   */
  activities(): Set<string> {
    const acts = new Set<string>();
    this.walk((_idx, info) => {
      if (info.type === "Transition" && info.label !== "tau") {
        acts.add(info.label);
      }
    });
    return acts;
  }

  /** Raw ordering relation of an SPO node as flat edge list `[src, tgt, …]`. */
  orderEdges(spoIdx: number): number[] {
    const rel = this._wm.get_order_of(this._handle, spoIdx);
    return Array.from(rel.edges_flat());
  }

  /** Transitive closure edges of an SPO node. */
  closureEdges(spoIdx: number): number[] {
    const rel = this._wm.transitive_closure(this._handle, spoIdx);
    return Array.from(rel.edges_flat());
  }

  /** Transitive reduction edges of an SPO node. */
  reductionEdges(spoIdx: number): number[] {
    const rel = this._wm.transitive_reduction(this._handle, spoIdx);
    return Array.from(rel.edges_flat());
  }
}

// ─── Main client class ────────────────────────────────────────────────────────

/**
 * Entry-point for the POWL WASM library.
 *
 * ```ts
 * const powl = await Powl.init();
 * ```
 */
export class Powl {
  /** @internal */
  private constructor(private readonly wm: WasmModule) {}

  /**
   * Initialise the WASM module and return a ready-to-use `Powl` instance.
   * Safe to call multiple times — the WASM module is loaded only once.
   */
  static async init(): Promise<Powl> {
    const wm = await getWasm();
    return new Powl(wm);
  }

  // ── Parsing ────────────────────────────────────────────────────────────────

  /**
   * Parse a POWL model string (Python `__repr__` format).
   *
   * @throws {Error} on syntax error.
   *
   * @example
   * ```ts
   * const m = powl.parse("X(A, B)");
   * const spo = powl.parse("PO=(nodes={A, B, C}, order={A-->B, A-->C})");
   * ```
   */
  parse(s: string): PowlModel {
    const handle = this.wm.parse_powl(s);
    return new PowlModel(this.wm, handle);
  }

  // ── Event log parsing ──────────────────────────────────────────────────────

  /**
   * Parse a XES-formatted XML string.
   *
   * @throws {Error} on XML parse failure.
   */
  parseXes(xml: string): EventLog {
    return JSON.parse(this.wm.parse_xes_log(xml)) as EventLog;
  }

  /**
   * Parse a CSV string with headers.
   *
   * Required columns: `case_id` / `case:concept:name`, `activity` / `concept:name`.
   * Optional: `timestamp` / `time:timestamp`.
   *
   * @throws {Error} on parse failure.
   *
   * @example
   * ```ts
   * const log = powl.parseCsv(
   *   "case_id,activity,timestamp\n" +
   *   "1,A,2020-01-01\n" +
   *   "1,B,2020-01-02\n"
   * );
   * ```
   */
  parseCsv(csv: string): EventLog {
    return JSON.parse(this.wm.parse_csv_log(csv)) as EventLog;
  }

  /**
   * Fetch and parse an XES file from a URL.
   *
   * @example
   * ```ts
   * const log = await powl.fetchXes("/logs/running-example.xes");
   * ```
   */
  async fetchXes(url: string): Promise<EventLog> {
    const text = await fetch(url).then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status} fetching ${url}`);
      return r.text();
    });
    return this.parseXes(text);
  }

  /**
   * Parse an XES `File` object from a drag-and-drop or `<input type="file">`.
   *
   * @example
   * ```ts
   * input.addEventListener("change", async (e) => {
   *   const log = await powl.readXesFile(e.target.files[0]);
   * });
   * ```
   */
  async readXesFile(file: File): Promise<EventLog> {
    const text = await file.text();
    return this.parseXes(text);
  }

  /** Parse a CSV `File` object. */
  async readCsvFile(file: File): Promise<EventLog> {
    const text = await file.text();
    return this.parseCsv(text);
  }

  // ── Conformance checking ───────────────────────────────────────────────────

  /**
   * Compute token-replay fitness of an event log against a POWL model.
   *
   * Internally converts the model to a Petri net then runs token replay.
   *
   * @example
   * ```ts
   * const model = powl.parse("PO=(nodes={A, B, C}, order={A-->B, B-->C})");
   * const log   = powl.parseCsv("case_id,activity\n1,A\n1,B\n1,C\n");
   * const fit   = powl.conformance(model, log);
   * console.log(fit.percentage);  // 1.0
   * ```
   */
  conformance(model: PowlModel, log: EventLog): FitnessResult {
    const pnJson = this.wm.powl_to_petri_net(model.toString());
    return JSON.parse(
      this.wm.token_replay_fitness(pnJson, JSON.stringify(log)),
    ) as FitnessResult;
  }

  /**
   * Compute token-replay fitness given a pre-built `PetriNetResult`.
   * Use when you already have a Petri net and want to avoid recomputing it.
   */
  conformancePetriNet(pn: PetriNetResult, log: EventLog): FitnessResult {
    return JSON.parse(
      this.wm.token_replay_fitness(JSON.stringify(pn), JSON.stringify(log)),
    ) as FitnessResult;
  }

  // ── Batch utilities ────────────────────────────────────────────────────────

  /**
   * Filter an event log to only traces whose fitness meets a threshold.
   *
   * @param threshold Minimum fitness score (0..1), default 0.8.
   */
  filterByFitness(
    model: PowlModel,
    log: EventLog,
    threshold = 0.8,
  ): EventLog {
    const result = this.conformance(model, log);
    const passingIds = new Set(
      result.trace_results
        .filter((r) => r.fitness >= threshold)
        .map((r) => r.case_id),
    );
    return {
      traces: log.traces.filter((t) => passingIds.has(t.case_id)),
    };
  }

  /**
   * Return variant statistics for an event log.
   *
   * @returns Map from activity sequence (joined by "→") to count.
   */
  variants(log: EventLog): Map<string, number> {
    const map = new Map<string, number>();
    for (const trace of log.traces) {
      const key = trace.events.map((e) => e.name).join("→");
      map.set(key, (map.get(key) ?? 0) + 1);
    }
    return map;
  }
}
