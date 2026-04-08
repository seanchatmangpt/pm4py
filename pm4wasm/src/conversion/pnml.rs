// PM4Py – A Process Mining Library for Python (POWL v2 WASM)
// Copyright (C) 2024 Process Intelligence Solutions
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/// PNML (Petri Net Markup Language) import/export.
///
/// Supports the PNML 2.0 standard for exchanging Petri nets between tools.
use crate::petri_net::{PetriNet, PetriNetResult, Place, Transition, Arc};
use wasm_bindgen::prelude::*;

/// Convert a PetriNetResult to PNML 2.0 XML format.
///
/// # Arguments
/// * `pn` - PetriNetResult containing the Petri net structure
///
/// # Returns
/// * PNML XML string
///
/// # Example
/// ```ignore
/// let pn = PetriNetResult {
///     net: PetriNet {
///         name: "My Net".to_string(),
///         places: vec![
///             Place { name: "p1".to_string() },
///             Place { name: "p2".to_string() },
///         ],
///         transitions: vec![
///             Transition {
///                 name: "t1".to_string(),
///                 label: Some("A".to_string()),
///                 properties: std::collections::HashMap::new(),
///             },
///         ],
///         arcs: vec![
///             Arc { source: "p1".to_string(), target: "t1".to_string(), weight: 1 },
///             Arc { source: "t1".to_string(), target: "p2".to_string(), weight: 1 },
///         ],
///     },
///     initial_marking: vec![("p1".to_string(), 1)].into_iter().collect(),
///     final_marking: vec![("p2".to_string(), 1)].into_iter().collect(),
/// };
///
/// let pnml = to_pnml(&pn);
/// ```
pub fn to_pnml(pn: &PetriNetResult) -> String {
    let mut xml = String::from("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.push_str("<pnml xmlns=\"http://www.pnml.org/version-2009/grammar\">\n");

    // Add net
    xml.push_str("  <net id=\"");
    xml.push_str(&pn.net.name);
    xml.push_str("\" type=\"P/T-net\">\n");

    // Add places
    for place in &pn.net.places {
        xml.push_str("    <place id=\"");
        xml.push_str(&place.name);
        xml.push_str("\">\n");
        xml.push_str("      <graphics/>\n");
        xml.push_str("    </place>\n");
    }

    // Add transitions
    for transition in &pn.net.transitions {
        xml.push_str("    <transition id=\"");
        xml.push_str(&transition.name);

        // Add label if present
        if let Some(label) = &transition.label {
            xml.push_str("\" name=\"");
            xml.push_str(label);
        }

        xml.push_str("\">\n");

        // Add tool-specific info if needed
        if !transition.properties.is_empty() {
            xml.push_str("      <toolspecific tool=\"ProM\">\n");
            // Could add tool-specific properties here
            xml.push_str("      </toolspecific>\n");
        }

        xml.push_str("      <graphics/>\n");
        xml.push_str("    </transition>\n");
    }

    // Add arcs
    for arc in &pn.net.arcs {
        xml.push_str("    <arc source=\"");
        xml.push_str(&arc.source);
        xml.push_str("\" target=\"");
        xml.push_str(&arc.target);
        xml.push_str("\">\n");

        // Add inscription (weight)
        xml.push_str("      <inscription>\n");
        xml.push_str("        <text>");
        xml.push_str(&arc.weight.to_string());
        xml.push_str("</text>\n");
        xml.push_str("      </inscription>\n");

        xml.push_str("      <graphics/>\n");
        xml.push_str("    </arc>\n");
    }

    // Add initial marking
    xml.push_str("    <initialmarking>\n");
    for (place, tokens) in &pn.initial_marking {
        if *tokens > 0 {
            xml.push_str("      <place idref=\"");
            xml.push_str(place);
            xml.push_str("\">\n");
            xml.push_str("        <text>");
            xml.push_str(&tokens.to_string());
            xml.push_str("</text>\n");
            xml.push_str("      </place>\n");
        }
    }
    xml.push_str("    </initialmarking>\n");

    // Add final marking
    xml.push_str("    <finalmarking>\n");
    for (place, tokens) in &pn.final_marking {
        if *tokens > 0 {
            xml.push_str("      <place idref=\"");
            xml.push_str(place);
            xml.push_str("\">\n");
            xml.push_str("        <text>");
            xml.push_str(&tokens.to_string());
            xml.push_str("</text>\n");
            xml.push_str("      </place>\n");
        }
    }
    xml.push_str("    </finalmarking>\n");

    xml.push_str("  </net>\n");
    xml.push_str("</pnml>\n");

    xml
}

/// Convert a PetriNetResult (JSON) to PNML 2.0 XML format.
///
/// # WASM Export
///
/// # Arguments
/// * `pn_json` - JSON string of PetriNetResult
///
/// # Returns
/// * PNML XML string
///
/// # Errors
/// * Returns JsValue error if JSON parsing fails
#[wasm_bindgen]
pub fn to_pnml_json(pn_json: &str) -> Result<String, JsValue> {
    let pn: PetriNetResult = serde_json::from_str(pn_json)
        .map_err(|e| JsValue::from_str(&format!("Failed to parse PetriNetResult JSON: {}", e)))?;
    Ok(to_pnml(&pn))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_to_pnml_simple() {
        let pn = PetriNetResult {
            net: PetriNet {
                name: "Test Net".to_string(),
                places: vec![
                    Place { name: "p1".to_string() },
                    Place { name: "p2".to_string() },
                ],
                transitions: vec![
                    Transition {
                        name: "t1".to_string(),
                        label: Some("A".to_string()),
                        properties: HashMap::new(),
                    },
                ],
                arcs: vec![
                    Arc { source: "p1".to_string(), target: "t1".to_string(), weight: 1 },
                    Arc { source: "t1".to_string(), target: "p2".to_string(), weight: 1 },
                ],
            },
            initial_marking: vec![("p1".to_string(), 1)].into_iter().collect(),
            final_marking: vec![("p2".to_string(), 1)].into_iter().collect(),
        };

        let pnml = to_pnml(&pn);
        assert!(pnml.contains("<?xml"));
        assert!(pnml.contains("<net id=\"Test Net\""));
        assert!(pnml.contains("<place id=\"p1\">"));
        assert!(pnml.contains("<transition id=\"t1\""));
        assert!(pnml.contains("name=\"A\""));
        assert!(pnml.contains("<inscription>"));
    }
}
