# Workflow Pattern Language

> *"A pattern language is a systematic method of creating good quality designs."* — Christopher Alexander

---

## Welcome to the Pattern Language

This book presents a pattern language for workflow processes, organized around the 43 workflow patterns first identified by the Workflow Patterns Initiative (van der Aalst, ter Hofstede, et al., 2003) and recast in the spirit of Christopher Alexander's *A Pattern Language*.

---

## What is a Pattern Language?

A pattern language is a network of patterns, where each pattern:

1. **Describes a problem** that occurs over and over again in our environment
2. **Describes the core of the solution** to that problem
3. **Shows how this solution connects to other patterns**

Patterns are not isolated solutions. They form a language—a system of relationships that allows you to navigate from one pattern to another, building up complex designs from simple, composable pieces.

---

## Why POWL v2?

POWL (Partially Ordered Workflow Language) v2 with its DecisionGraph extension is the most expressive process modeling formalism that:

- Captures all 43 workflow patterns
- Maintains formal soundness guarantees (deadlock freedom, liveness, boundedness)
- Converts directly to executable BPMN 2.0
- Supports both human-readable text notation and programmatic manipulation

---

## How This Book is Organized

This pattern language is organized into seven pattern groups:

| Group | Patterns | Focus |
|-------|----------|-------|
| **Control Flow (Basic)** | 5 | Fundamental routing patterns |
| **Advanced Branching** | 10 | Complex choice and synchronization |
| **Structural** | 10 | Subprocess composition and control |
| **State-Based** | 10 | State-dependent process behavior |
| **Multiple Instance** | 11 | Parallel activity instances |
| **Data** | 5 | Data flow and visibility |
| **Resource** | 10 | Organizational assignment |

---

## Reading This Book

### Start with the Problem

Don't read this book cover-to-cover. Start with the problem you're trying to solve:

1. **Identify your domain**: Control flow? Resource allocation? Data handling?
2. **Scan the pattern group**: Read the context and problem statements
3. **Follow related patterns**: Let the language guide you to deeper patterns

### Use the POWL Notation

Each pattern includes:
- **Problem statement** in natural language
- **Solution** in POWL v2 notation
- **Example** with concrete business process
- **Related patterns** that form the language network

### Trust the Language

As Alexander wrote: *"Each pattern creates the possibility of other patterns, and each pattern depends upon the patterns which come before it."*

When you find a pattern that fits your context, follow its connections to related patterns. The language will guide you to a complete design.

---

## A Note on Completeness

This pattern language includes all 43 workflow patterns from the original YAWL catalog, plus:
- Multi-perspective extensions (organizational, temporal, data)
- POWL v2 DecisionGraph patterns for non-block-structured choice
- Modern workflow patterns from BPMN 2.0 and CMMN

---

## Philosophy

> *"The patterns are not 'designs' in the sense of blueprints. They are more like seeds—generative structures that, when placed in a context, help to generate a design."* — Christopher Alexander

This pattern language is not a catalog of预制 designs. It is a language for generating designs that fit your specific context, constraints, and requirements.

Use these patterns as starting points, not endpoints. Adapt them to your domain. Extend them where they fall short. Most importantly, **use the language**—let the connections between patterns guide your thinking.

---

## Next Steps

- New to patterns? Start with [How to Use These Patterns](./usage.md)
- Want to understand the philosophy? Read [Pattern Language Philosophy](./philosophy.md)
- Ready to design? Jump to [Control Flow Patterns](./patterns/control-flow/sequence.md)
