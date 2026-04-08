# Changelog

All notable changes to pm4wasm will be documented in this file.

## [26.4.7] - 2026-04-07

### Added
- **LLM Integration**: Natural language to POWL generation using Vercel AI SDK v7
  - Multi-provider support: Groq, OpenAI, Anthropic
  - Domain-specific few-shot demos (5 domains: loan_approval, software_release, ecommerce, manufacturing, healthcare)
  - Automatic validation and refinement loop (up to 3 iterations)
- **Code Generation**: Generate workflow code from POWL models
  - n8n JSON workflows
  - Temporal Go workflows
  - Camunda BPMN XML
  - YAWL v6 XML
- **Validation**: POWL structure validation with soundness checking
- **WASM Functions**:
  - `validate_powl_structure()` - Validate POWL models
  - `get_demos_for_domain()` - Get few-shot examples
  - `generate_code_from_powl()` - Code generation

### Changed
- **License**: Changed from AGPL-3.0 to Apache-2.0 (matching pm4py)
- **Versioning**: Adopted CalVer (Calendar Versioning) - v26.4.7 = 2026 April, week 7, build 7
- **Dependencies**: Updated to latest Vercel AI SDK v7.0.0-beta.72

### Fixed
- TypeScript strict mode compliance (zero `any` types, no unused variables)
- Vercel AI SDK v7 API compatibility
- Provider factory pattern for Groq, OpenAI, Anthropic

### Technical Details
- **Build**: `wasm-pack` for Rust → WASM, `vite` for TypeScript bundling
- **Browser Support**: 100% browser-native, no server required
- **Type Safety**: Full TypeScript strict mode, comprehensive type definitions

## [0.2.0] - 2025-04-07

### Added
- Initial WASM bindings for POWL v2
- Process model parsing and validation
- Petri net conversion
- Conformance checking with token replay
- Event log parsing (XES, CSV)
- Footprints extraction
- Model simplification

[26.4.7]: https://github.com/seanchatmangpt/pm4wasm/releases/tag/v26.4.7
[0.2.0]: https://github.com/seanchatmangpt/pm4wasm/releases/tag/v0.2.0
