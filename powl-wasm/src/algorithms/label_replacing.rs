/// Label replacement utility for POWL models.
///
/// Ports `pm4py/objects/powl/utils/label_replacing.py:apply`.
use crate::powl::{PowlArena, PowlNode};
use std::collections::HashMap;

/// Replace activity labels in a POWL subtree according to a dictionary.
///
/// Creates a deep copy of the subtree with all transition labels mapped via the dictionary.
pub fn apply(
    arena: &PowlArena,
    node_idx: u32,
    label_map: &HashMap<String, String>,
    dest_arena: &mut PowlArena,
) -> u32 {
    match arena.get(node_idx) {
        None => node_idx, // shouldn't happen

        Some(PowlNode::Transition(t)) => {
            let new_label = t.label.as_ref().and_then(|l| {
                label_map.get(l).cloned().or_else(|| Some(l.clone()))
            });
            dest_arena.add_transition(new_label)
        }

        Some(PowlNode::FrequentTransition(t)) => {
            let new_activity = label_map
                .get(&t.activity)
                .cloned()
                .unwrap_or_else(|| t.activity.clone());
            let min_freq = if t.skippable { 0 } else { 1 };
            let max_freq = if t.selfloop { None } else { Some(1) };
            dest_arena.add_frequent_transition(new_activity, min_freq, max_freq)
        }

        Some(PowlNode::OperatorPowl(op)) => {
            let new_children: Vec<u32> = op
                .children
                .iter()
                .map(|&c| apply(arena, c, label_map, dest_arena))
                .collect();
            dest_arena.add_operator(op.operator, new_children)
        }

        Some(PowlNode::StrictPartialOrder(spo)) => {
            let old_children = spo.children.clone();
            let old_order = spo.order.clone();
            let mut new_children: Vec<u32> = Vec::new();
            let n = old_children.len();

            for &c in &old_children {
                new_children.push(apply(arena, c, label_map, dest_arena));
            }

            let spo_idx = dest_arena.add_strict_partial_order(new_children);

            // Restore edges (indices map 1-to-1)
            for i in 0..n {
                for j in 0..n {
                    if old_order.is_edge(i, j) {
                        dest_arena.add_order_edge(spo_idx, i, j);
                    }
                }
            }

            spo_idx
        }
    }
}

// ─── tests ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::parse_powl_model_string;

    #[test]
    fn replace_single_label() {
        let mut arena = PowlArena::new();
        let root = parse_powl_model_string("A", &mut arena).unwrap();

        let mut map = HashMap::new();
        map.insert("A".to_string(), "B".to_string());

        let mut dest = PowlArena::new();
        let new_root = apply(&arena, root, &map, &mut dest);

        let repr = dest.to_repr(new_root);
        assert_eq!(repr, "B");
    }

    #[test]
    fn replace_in_xor() {
        let mut arena = PowlArena::new();
        let root = parse_powl_model_string("X ( A, B )", &mut arena).unwrap();

        let mut map = HashMap::new();
        map.insert("A".to_string(), "X".to_string());
        map.insert("B".to_string(), "Y".to_string());

        let mut dest = PowlArena::new();
        let new_root = apply(&arena, root, &map, &mut dest);

        let repr = dest.to_repr(new_root);
        assert!(repr.contains("X") && repr.contains("Y"), "got: {}", repr);
    }

    #[test]
    fn replace_in_po() {
        let mut arena = PowlArena::new();
        let root =
            parse_powl_model_string("PO=(nodes={A, B}, order={A-->B})", &mut arena).unwrap();

        let mut map = HashMap::new();
        map.insert("A".to_string(), "Start".to_string());
        map.insert("B".to_string(), "End".to_string());

        let mut dest = PowlArena::new();
        let new_root = apply(&arena, root, &map, &mut dest);

        let repr = dest.to_repr(new_root);
        assert!(repr.contains("Start") && repr.contains("End"), "got: {}", repr);
    }
}
