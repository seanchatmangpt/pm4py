/// Process tree data model.
///
/// Mirrors `pm4py/objects/process_tree/obj.py` for the subset used by
/// the POWL → ProcessTree conversion.
use serde::{Deserialize, Serialize};

/// Operators supported in a process tree.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum PtOperator {
    /// Sequential composition (`→`)
    Sequence,
    /// Exclusive choice (`×`)
    Xor,
    /// Parallel execution (`∧`)
    Parallel,
    /// Loop (`↺` — do/redo)
    Loop,
}

impl PtOperator {
    pub fn as_str(self) -> &'static str {
        match self {
            PtOperator::Sequence => "->",
            PtOperator::Xor => "X",
            PtOperator::Parallel => "+",
            PtOperator::Loop => "*",
        }
    }
}

/// A node in a process tree.
///
/// Leaf nodes have a label (`Some(str)` for activities, `None` for tau).
/// Internal nodes have an operator and children (label is `None`).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ProcessTree {
    /// Activity label for leaf nodes; `None` for internal nodes and tau leaves.
    pub label: Option<String>,
    /// Operator for internal nodes; `None` for leaf nodes.
    pub operator: Option<PtOperator>,
    /// Children (empty for leaf nodes).
    pub children: Vec<ProcessTree>,
}

impl ProcessTree {
    /// Create a leaf node.
    pub fn leaf(label: Option<String>) -> Self {
        ProcessTree {
            label,
            operator: None,
            children: Vec::new(),
        }
    }

    /// Create an internal node.
    pub fn internal(operator: PtOperator, children: Vec<ProcessTree>) -> Self {
        ProcessTree {
            label: None,
            operator: Some(operator),
            children,
        }
    }

    /// Canonical string representation (mirrors Python __repr__).
    pub fn to_repr(&self) -> String {
        match (&self.operator, &self.label) {
            (None, None) => "tau".to_string(),
            (None, Some(l)) => l.clone(),
            (Some(op), _) => {
                let children: Vec<String> =
                    self.children.iter().map(|c| c.to_repr()).collect();
                format!("{} ( {} )", op.as_str(), children.join(", "))
            }
        }
    }
}
