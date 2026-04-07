//! # powl-wasm
//!
//! WebAssembly port of POWL v2 (Partially Ordered Workflow Language) from pm4py.
//!
//! ## Quick start (JavaScript / browser)
//!
//! ```js
//! import init, {
//!   parse_powl,
//!   validate_partial_orders,
//!   powl_to_string,
//!   simplify_powl,
//!   simplify_frequent_transitions,
//!   transitive_reduction,
//!   transitive_closure,
//!   is_strict_partial_order,
//! } from './pkg/powl_wasm.js';
//!
//! await init();
//!
//! // Parse a POWL model string (same format as Python __repr__)
//! const model = parse_powl("PO=(nodes={A, B, C}, order={A-->B, A-->C})");
//!
//! // Validate
//! validate_partial_orders(model);   // throws on violation
//!
//! // Serialise back
//! console.log(powl_to_string(model));
//!
//! // Graph ops on a binary relation
//! const rel = transitive_closure(model, 0);  // root SPO's order, closed
//! const red = transitive_reduction(rel);
//! ```
//!
//! ## Architecture
//!
//! All nodes are stored in a flat [`PowlModel`] arena (a thin wasm-bindgen
//! wrapper around [`PowlArena`]).  Nodes are referenced by their `u32` index.
//! The root of the parsed tree is always the *last* node added (index
//! `model.len() - 1`).

use wasm_bindgen::prelude::*;

mod binary_relation;
mod powl;
mod parser;
pub mod algorithms;

use binary_relation::BinaryRelation;
use powl::{PowlArena, PowlNode};
use parser::parse_powl_model_string;
use algorithms::simplify as simplify_algo;
use algorithms::transitive as transitive_algo;

// ─── JS-visible wrapper types ────────────────────────────────────────────────

/// Flat arena holding the entire POWL model tree.
///
/// Construct with [`parse_powl`].  The root node is at index `model.root()`.
#[wasm_bindgen]
pub struct PowlModel {
    arena: PowlArena,
    root: u32,
}

#[wasm_bindgen]
impl PowlModel {
    /// Index of the root node.
    pub fn root(&self) -> u32 {
        self.root
    }

    /// Total number of nodes in the arena.
    pub fn len(&self) -> usize {
        self.arena.len()
    }

    pub fn is_empty(&self) -> bool {
        self.arena.is_empty()
    }
}

/// A serialisable binary relation (adjacency matrix) exposed to JavaScript.
///
/// Construct via [`transitive_closure`], [`transitive_reduction`], or
/// [`get_order_of`].
#[wasm_bindgen]
pub struct BinaryRelationJs {
    inner: BinaryRelation,
}

#[wasm_bindgen]
impl BinaryRelationJs {
    /// Number of nodes.
    pub fn n(&self) -> usize {
        self.inner.n
    }

    /// Test whether edge i→j exists.
    pub fn is_edge(&self, i: usize, j: usize) -> bool {
        self.inner.is_edge(i, j)
    }

    /// Return all edges as a flat `[src0, tgt0, src1, tgt1, …]` array.
    pub fn edges_flat(&self) -> Vec<u32> {
        self.inner
            .edge_list()
            .into_iter()
            .flat_map(|(s, t)| [s as u32, t as u32])
            .collect()
    }

    pub fn is_irreflexive(&self) -> bool {
        self.inner.is_irreflexive()
    }

    pub fn is_transitive(&self) -> bool {
        self.inner.is_transitive()
    }

    pub fn is_strict_partial_order(&self) -> bool {
        self.inner.is_strict_partial_order()
    }

    /// Nodes with no incoming edges.
    pub fn start_nodes(&self) -> Vec<u32> {
        self.inner
            .get_start_nodes()
            .into_iter()
            .map(|x| x as u32)
            .collect()
    }

    /// Nodes with no outgoing edges.
    pub fn end_nodes(&self) -> Vec<u32> {
        self.inner
            .get_end_nodes()
            .into_iter()
            .map(|x| x as u32)
            .collect()
    }
}

// ─── Public WASM API ─────────────────────────────────────────────────────────

/// Parse a POWL model string (the same format as the Python `__repr__`) and
/// return an opaque [`PowlModel`] handle.
///
/// # Errors
/// Throws a JavaScript `Error` if parsing fails.
#[wasm_bindgen]
pub fn parse_powl(s: &str) -> Result<PowlModel, JsValue> {
    let mut arena = PowlArena::new();
    let root = parse_powl_model_string(s, &mut arena)
        .map_err(|e| JsValue::from_str(&format!("POWL parse error: {}", e)))?;
    Ok(PowlModel { arena, root })
}

/// Validate that all `StrictPartialOrder` nodes in `model` have irreflexive
/// and transitive ordering relations.
///
/// # Errors
/// Throws a JavaScript `Error` describing the first violation found.
#[wasm_bindgen]
pub fn validate_partial_orders(model: &PowlModel) -> Result<(), JsValue> {
    model
        .arena
        .validate_partial_orders(model.root)
        .map_err(|e| JsValue::from_str(&e))
}

/// Return the string representation of the model root (mirrors Python `__repr__`).
#[wasm_bindgen]
pub fn powl_to_string(model: &PowlModel) -> String {
    model.arena.to_repr(model.root)
}

/// Recursively simplify the model (merge XOR+LOOP patterns, flatten nested
/// XORs, inline sub-SPOs where possible).  Returns a new [`PowlModel`].
#[wasm_bindgen]
pub fn simplify_powl(model: &PowlModel) -> PowlModel {
    let mut arena = model.arena.clone();
    let new_root = simplify_algo::simplify(&mut arena, model.root);
    PowlModel { arena, root: new_root }
}

/// Convert `XOR(A, tau)` / `LOOP(A, tau)` patterns to `FrequentTransition`
/// nodes.  Returns a new [`PowlModel`].
#[wasm_bindgen]
pub fn simplify_frequent_transitions(model: &PowlModel) -> PowlModel {
    let mut arena = model.arena.clone();
    let new_root =
        simplify_algo::simplify_using_frequent_transitions(&mut arena, model.root);
    PowlModel { arena, root: new_root }
}

/// Return the transitive closure of the ordering relation of a
/// `StrictPartialOrder` node.
///
/// `spo_arena_idx` is the arena index of the SPO node (use `model.root()` for
/// the root, or another index for a nested SPO).
///
/// # Errors
/// Throws if `spo_arena_idx` does not point to a `StrictPartialOrder`.
#[wasm_bindgen]
pub fn transitive_closure(
    model: &PowlModel,
    spo_arena_idx: u32,
) -> Result<BinaryRelationJs, JsValue> {
    match model.arena.get(spo_arena_idx) {
        Some(PowlNode::StrictPartialOrder(spo)) => {
            let closed = transitive_algo::transitive_closure(&spo.order);
            Ok(BinaryRelationJs { inner: closed })
        }
        _ => Err(JsValue::from_str(&format!(
            "node {} is not a StrictPartialOrder",
            spo_arena_idx
        ))),
    }
}

/// Return the transitive reduction of the ordering relation of a
/// `StrictPartialOrder` node.
///
/// # Errors
/// Throws if the node is not an SPO or the relation is not irreflexive.
#[wasm_bindgen]
pub fn transitive_reduction(
    model: &PowlModel,
    spo_arena_idx: u32,
) -> Result<BinaryRelationJs, JsValue> {
    match model.arena.get(spo_arena_idx) {
        Some(PowlNode::StrictPartialOrder(spo)) => {
            let red = spo.order.get_transitive_reduction();
            Ok(BinaryRelationJs { inner: red })
        }
        _ => Err(JsValue::from_str(&format!(
            "node {} is not a StrictPartialOrder",
            spo_arena_idx
        ))),
    }
}

/// Return the raw ordering relation of a `StrictPartialOrder` node as a
/// [`BinaryRelationJs`].
///
/// # Errors
/// Throws if `spo_arena_idx` does not point to a `StrictPartialOrder`.
#[wasm_bindgen]
pub fn get_order_of(
    model: &PowlModel,
    spo_arena_idx: u32,
) -> Result<BinaryRelationJs, JsValue> {
    match model.arena.get(spo_arena_idx) {
        Some(PowlNode::StrictPartialOrder(spo)) => {
            Ok(BinaryRelationJs { inner: spo.order.clone() })
        }
        _ => Err(JsValue::from_str(&format!(
            "node {} is not a StrictPartialOrder",
            spo_arena_idx
        ))),
    }
}

/// Return the string representation of an individual node by arena index.
#[wasm_bindgen]
pub fn node_to_string(model: &PowlModel, arena_idx: u32) -> String {
    model.arena.to_repr(arena_idx)
}

/// Return the child arena indices of an SPO or OperatorPOWL node as a flat
/// `u32` array.  Returns an empty array for leaf nodes.
#[wasm_bindgen]
pub fn get_children(model: &PowlModel, arena_idx: u32) -> Vec<u32> {
    match model.arena.get(arena_idx) {
        Some(PowlNode::StrictPartialOrder(spo)) => spo.children.clone(),
        Some(PowlNode::OperatorPowl(op)) => op.children.clone(),
        _ => Vec::new(),
    }
}

/// Return a JSON string describing the node at `arena_idx`.
///
/// Format: `{"type":"Transition","label":"A"}` or
///         `{"type":"StrictPartialOrder","children":[0,1],"edges":[[0,1]]}`
#[wasm_bindgen]
pub fn node_info_json(model: &PowlModel, arena_idx: u32) -> String {
    match model.arena.get(arena_idx) {
        None => r#"{"type":"Invalid"}"#.to_string(),
        Some(PowlNode::Transition(t)) => {
            let label = t.label.as_deref().unwrap_or("tau");
            format!(r#"{{"type":"Transition","label":"{}","id":{}}}"#, label, t.id)
        }
        Some(PowlNode::FrequentTransition(t)) => {
            format!(
                r#"{{"type":"FrequentTransition","label":"{}","activity":"{}","skippable":{},"selfloop":{}}}"#,
                t.label, t.activity, t.skippable, t.selfloop
            )
        }
        Some(PowlNode::StrictPartialOrder(spo)) => {
            let children_json: Vec<String> =
                spo.children.iter().map(|c| c.to_string()).collect();
            let edges: Vec<String> = spo
                .order
                .edge_list()
                .iter()
                .map(|(s, t)| format!("[{},{}]", s, t))
                .collect();
            format!(
                r#"{{"type":"StrictPartialOrder","children":[{}],"edges":[{}]}}"#,
                children_json.join(","),
                edges.join(",")
            )
        }
        Some(PowlNode::OperatorPowl(op)) => {
            let op_str = op.operator.as_str();
            let children_json: Vec<String> =
                op.children.iter().map(|c| c.to_string()).collect();
            format!(
                r#"{{"type":"OperatorPowl","operator":"{}","children":[{}]}}"#,
                op_str,
                children_json.join(",")
            )
        }
    }
}

// ─── Utility ─────────────────────────────────────────────────────────────────

/// Set up the `console_error_panic_hook` in debug/dev builds so Rust panics
/// surface as useful browser console messages.  Call once after `init()`.
#[wasm_bindgen(start)]
pub fn start() {
    #[cfg(feature = "console_error_panic_hook")]
    console_error_panic_hook::set_once();
}
