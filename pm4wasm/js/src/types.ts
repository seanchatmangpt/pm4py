// ─── Shared domain types ──────────────────────────────────────────────────────

/** A single event inside a trace. */
export interface LogEvent {
  name: string;
  timestamp?: string;
  lifecycle?: string;
  attributes: Record<string, string>;
}

/** An ordered sequence of events for one case. */
export interface Trace {
  case_id: string;
  events: LogEvent[];
}

/** A parsed XES or CSV event log. */
export interface EventLog {
  traces: Trace[];
}

// ─── Petri net ────────────────────────────────────────────────────────────────

export interface PetriPlace {
  name: string;
}

export interface PetriTransition {
  name: string;
  label?: string | null;
  properties: Record<string, unknown>;
}

export interface PetriArc {
  source: string;
  target: string;
  weight: number;
}

export interface PetriNet {
  name: string;
  places: PetriPlace[];
  transitions: PetriTransition[];
  arcs: PetriArc[];
}

export type Marking = Record<string, number>;

export interface PetriNetResult {
  net: PetriNet;
  initial_marking: Marking;
  final_marking: Marking;
}

// ─── Process tree ─────────────────────────────────────────────────────────────

export type PtOperator = "Sequence" | "Xor" | "Parallel" | "Loop";

export interface ProcessTree {
  label?: string | null;
  operator?: PtOperator | null;
  children: ProcessTree[];
}

// ─── Footprints ───────────────────────────────────────────────────────────────

export interface Footprints {
  start_activities: string[];
  end_activities: string[];
  activities: string[];
  activities_always_happening: string[];
  skippable_activities: string[];
  /** [a, b] pairs where a directly precedes b. */
  sequence: [string, string][];
  /** [a, b] pairs where a and b are concurrent. */
  parallel: [string, string][];
  min_trace_length: number;
}

// ─── Conformance ──────────────────────────────────────────────────────────────

export interface TraceReplayResult {
  case_id: string;
  fitness: number;
  produced_tokens: number;
  consumed_tokens: number;
  missing_tokens: number;
  remaining_tokens: number;
}

export interface FitnessResult {
  /** Global token-weighted fitness in [0, 1]. */
  percentage: number;
  /** Average per-trace fitness. */
  avg_trace_fitness: number;
  perfectly_fitting_traces: number;
  total_traces: number;
  trace_results: TraceReplayResult[];
}

// ─── Node info ────────────────────────────────────────────────────────────────

export type NodeType =
  | "Transition"
  | "FrequentTransition"
  | "StrictPartialOrder"
  | "OperatorPowl"
  | "Invalid";

export type NodeInfo =
  | { type: "Transition"; label: string; id: number }
  | {
      type: "FrequentTransition";
      label: string;
      activity: string;
      skippable: boolean;
      selfloop: boolean;
    }
  | { type: "StrictPartialOrder"; children: number[]; edges: [number, number][] }
  | { type: "OperatorPowl"; operator: string; children: number[] }
  | { type: "Invalid" };
