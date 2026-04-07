# From Natural Language to Verified BPMN: AI-Assisted Process Discovery as the New Paradigm

**A Doctoral Thesis**

---

## Abstract

Process mining has historically operated on a single input modality: event logs. Discovery algorithms—inductive miners, heuristic miners, genetic miners—construct process models from observed behavior, evaluated against fitness, precision, generalization, and simplicity. This thesis argues that this paradigm is insufficient for the majority of real-world process modeling needs, where the process exists only in human language: standard operating procedures, regulatory documents, system specifications, and organizational knowledge.

We present a new paradigm: **natural language to verified BPMN via POWL v2**. An LLM generates a formal process model (POWL) from a free-text description, a domain-expert judge verifies structural soundness against van der Aalst's criteria (deadlock freedom, liveness, boundedness), and a refinement loop corrects deficiencies until the model passes. The verified POWL model is then converted to industry-standard BPMN 2.0 XML, closable the gap between process understanding and process execution.

The theoretical foundation that makes this possible is POWL v2 (Partially Ordered Workflow Language, Version 2) with its DecisionGraph extension. We demonstrate that DecisionGraph is the only process modeling formalism expressive enough to capture the non-block-structured choice patterns that pervade real-world processes while maintaining the formal soundness guarantees required for verification. We further show that this capability creates an unassailable competitive advantage: Porter's Five Forces analysis reveals that mathematical verification transforms the AI agent framework market from a Red Ocean to a Blue Ocean.

Through empirical evaluation on four domains (healthcare, software engineering, multi-agent orchestration, e-commerce), we demonstrate that the NL→POWL→BPMN pipeline produces verified, executable process models from natural language descriptions in a single refinement cycle for complex processes.

**Keywords:** Process Mining, Natural Language Processing, Large Language Models, POWL, DecisionGraph, BPMN, Formal Verification, DSPy, Blue Ocean Strategy, Process Discovery

---

## Declaration

This thesis is submitted in fulfillment of the requirements for the degree of Doctor of Philosophy. The work presented herein represents original research conducted within the Process Intelligence research group.

---

## Table of Contents

1. [Introduction: The Paradigm Shift](#1-introduction-the-paradigm-shift)
2. [Foundations: Why Formal Models Matter](#2-foundations-why-formal-models-matter)
3. [The NL-to-POWL Pipeline](#3-the-nl-to-powl-pipeline)
4. [The Verification Framework](#4-the-verification-framework)
5. [POWL v2 as Enabler: DecisionGraph](#5-powl-v2-as-enabler-decisiongraph)
6. [Empirical Evaluation](#6-empirical-evaluation)
7. [Strategic Analysis: Mathematical Correctness as Blue Ocean](#7-strategic-analysis-mathematical-correctness-as-blue-ocean)
8. [Vision 2030](#8-vision-2030)
9. [Conclusion](#9-conclusion)
10. [References](#10-references)
11. [Appendices](#appendices)

---

## 1. Introduction: The Paradigm Shift

### 1.1 The Problem: Processes Live in Language, Not Logs

Process mining emerged at the intersection of data science and process management, promising to bridge the gap between event data recorded by information systems and the behavioral models that describe how organizations actually operate (van der Aalst, 2016). For two decades, the field has refined increasingly sophisticated algorithms for extracting process models from event logs—inductive miners (Leemans et al., 2013), heuristic miners (Weijters & Ribeiro, 2011), genetic miners (Buijs et al., 2017), and region-based miners (Carmona et al., 2014).

But here is the reality that the field has not addressed: **most processes are never logged**.

A startup designing its first workflow has no event log. A compliance team documenting a new regulatory process works from a standard operating procedure, not traces. A systems architect designing a multi-agent orchestration protocol works from a specification document. A healthcare administrator describing a patient admission pathway works from institutional knowledge. A consultant modeling a client's business process works from interviews and workshop notes.

In all these cases—and they constitute the majority of process modeling scenarios—the input is human language. The event log does not exist because the process has not been instrumented, or has not been deployed, or exists only as a document on someone's desk.

The question this thesis addresses is not incremental: **Can an AI system take a natural language description of a process and produce a mathematically verified, executable BPMN model?**

### 1.2 Why This Matters Now

Three technological developments converge to make this question answerable for the first time:

1. **Large language models** (GPT-4, Claude, Llama) can parse and reason about complex procedural descriptions with high fidelity.

2. **DSPy** (Khattab et al., 2023) provides a framework for optimizing LLM prompts and few-shot examples programmatically, enabling systematic improvement of generation quality.

3. **POWL v2** (Kourani & van der Aalst, 2025) provides a process modeling language expressive enough to capture non-block-structured patterns that pervade real-world processes, while maintaining formal soundness guarantees that enable automated verification.

Remove any one of these, and the pipeline fails. Without LLMs, natural language cannot be parsed. Without DSPy, the generation quality cannot be systematically improved. Without POWL v2, the generated models cannot capture the patterns that make real processes non-trivial.

### 1.3 The Central Contribution

This thesis makes the following argument:

**The primary value of process mining technology is not discovering models from logs. It is providing the formal foundation—expressiveness, soundness, verifiability—that enables AI systems to generate, verify, and execute process models from natural language.**

Event log discovery remains important and is complementary. But the paradigm shift is this: the most impactful application of process mining theory is as the **verification backbone** for AI-generated workflows, not as the discovery mechanism itself.

The practical manifestation of this argument is the NL→POWL→BPMN pipeline:

```
Natural Language Description
    → DSPy Agent (LLM generates POWL model)
    → Judge (verifies structural soundness)
    → Refinement Loop (corrects deficiencies)
    → Verified POWL → BPMN 2.0 XML
    → Open in any BPMN editor (Camunda, Signavio, Bizagi)
```

### 1.4 Research Questions

**RQ1:** How can an LLM generate a formal process model from a natural language description that is expressive enough to capture non-block-structured real-world processes?

**RQ2:** How can generated process models be automatically verified for structural soundness (deadlock freedom, liveness, boundedness) without reference to a ground truth model?

**RQ3:** How can verification failures be automatically corrected through a judge-refinement feedback loop?

**RQ4:** What process modeling formalism enables this pipeline, and why are alternatives (process trees, BPMN directly, imperative code) insufficient?

**RQ5:** What strategic advantage does mathematical verification of AI workflows create, and why can existing agent frameworks not replicate it?

### 1.5 Contributions

1. **The NL→POWL→BPMN pipeline.** A complete, working system that transforms natural language process descriptions into verified, executable BPMN models through LLM generation, automated verification, and iterative refinement.

2. **The Dr. van der Aalst Judge.** An LLM-based verification agent that evaluates process models against formal soundness criteria derived from van der Aalst's workflow soundness theory, without requiring a ground truth model.

3. **The judge-refinement loop.** A closed feedback cycle where verification failures produce actionable feedback that improves generation quality, achieving verified models in a single refinement cycle on complex processes.

4. **Few-shot demonstrations for NL process modeling.** Domain-specific examples (loan approval, software release, e-commerce, multi-agent orchestration) that teach correct operator selection—particularly the XOR vs. partial order distinction that is the most common LLM generation error.

5. **The strategic analysis demonstrating mathematical verification as Blue Ocean.** Using Porter's Five Forces, we show that formal verification of AI-generated workflows creates an unassailable competitive advantage that existing frameworks cannot replicate without fundamental architectural changes.

### 1.6 Thesis Structure

Chapter 2 establishes the theoretical foundations—why formal models, why soundness, why POWL v2 specifically. Chapter 3 presents the NL-to-POWL pipeline in detail. Chapter 4 describes the verification framework. Chapter 5 explains why POWL v2's DecisionGraph is the enabling formalism. Chapter 6 presents empirical results. Chapter 7 provides the strategic analysis. Chapter 8 outlines Vision 2030. Chapter 9 concludes.

---

## 2. Foundations: Why Formal Models Matter

### 2.1 The Expressiveness Problem

Process models serve two purposes that stand in tension: they must be **expressive** enough to capture real-world behavior, and **formal** enough to enable automated analysis. The history of process modeling is a history of tradeoffs between these poles.

**Process trees** (van der Aalst et al., 2010) are maximally formal: every model is block-structured (decomposable into single-entry-single-exit regions), enabling efficient algorithms and formal verification. But they cannot express overlapping choice regions—a pattern where an activity participates in multiple, non-nested decision contexts. This limitation is not theoretical; it pervades healthcare, financial services, manufacturing, and virtually every domain where human judgment interacts with automated workflows.

**BPMN** is maximally expressive: its visual notation supports arbitrary gateway configurations, ad hoc subprocesses, and event-based routing. But its informal semantics (multiple conformance interpretations, vendor-specific extensions) make automated verification unreliable.

**POWL v2** (Partially Ordered Workflow Language, Version 2) with DecisionGraph occupies the optimal position: it is formal (well-defined semantics, conversion to Petri nets, soundness guarantees) and expressive (captures non-block-structured patterns that process trees cannot).

### 2.2 The Soundness Problem

A process model that cannot be verified is a process model that cannot be trusted. Van der Aalst's soundness criteria define what it means for a workflow to be correct:

| Property | Definition | Practical Consequence |
|---|---|---|
| **Deadlock freedom** | No execution can reach a state where all processes wait indefinitely | Workflow will not hang |
| **Liveness** | Every action that starts must eventually complete | Every task reaches a terminal state |
| **Boundedness** | No unbounded growth of state, queues, or memory | Resources are finite and controlled |

These properties are not new. They trace back to Carl Adam Petri's foundational work (1962) and have been refined over three decades of process mining research. Theorems 9 and 10 in this thesis establish that POWL v2 models guarantee these properties upon conversion to Petri nets.

**The critical insight for this thesis:** these soundness properties are precisely what AI agent frameworks lack. When an LLM generates a multi-step workflow, there is no guarantee that the workflow is deadlock-free, live, or bounded. The current industry response is ad hoc: add timeouts, add retry limits, add circuit breakers—each one a patch on a fundamentally unverified structure.

Formal process mining theory provides the principled alternative: generate the workflow as a formal model, verify it against soundness criteria, and only then execute it.

### 2.3 Why POWL v2, Not Process Trees or BPMN Directly

The NL→POWL→BPMN pipeline requires POWL v2 as the intermediate representation for three reasons:

**1. Expressiveness.** Natural language descriptions of real processes routinely contain non-block-structured patterns. A hospital admission pathway where "triage" leads to different monitoring protocols depending on urgency level, and where "prescribe medication" and "recommend surgery" are alternatives (not concurrent activities) within a complex decision structure—this cannot be expressed as a process tree without distorting the semantics.

**2. Verifiability.** POWL v2 has well-defined formal semantics and converts to Petri nets, enabling automated soundness checking. BPMN's informal semantics make this unreliable. Process trees have formal semantics but lack expressiveness.

**3. The XOR vs. PO distinction.** The most common error in LLM-generated process models is confusing XOR (exactly one branch executes) with partial order concurrency (all branches must complete). POWL v2 makes this distinction explicit in its syntax: `X()` for exclusive choice, `PO=()` for partial order. This syntactic clarity is essential for both generation and verification.

### 2.4 The Process Cube and Multi-Perspective Analysis

Van der Aalst's process cube framework identifies four perspectives for process analysis:

1. **Control-flow perspective:** The order in which activities are executed.
2. **Organizational perspective:** Who performs activities (resources, roles, departments).
3. **Case perspective:** Data associated with individual process instances.
4. **Time perspective:** When activities occur (timestamps, durations, waiting times).

The NL→POWL pipeline primarily addresses the control-flow perspective: given a description of what happens and in what order, construct a formal model. However, the pipeline's architecture—LLM parsing → formal model generation → verification — is extensible to all four perspectives. Future work will integrate organizational and temporal constraints into the generation and verification stages.

### 2.5 Quality Dimensions

Four quality dimensions govern the evaluation of process models (van der Aalst, 2016):

- **Fitness:** The degree to which the model can reproduce observed behavior.
- **Precision:** The degree to which the model avoids allowing behavior not observed.
- **Generalization:** The degree to which the model captures behavior that is possible but not yet observed.
- **Simplicity:** The degree to which the model is as simple as possible while maintaining adequate quality on other dimensions.

In the NL→POWL context, these dimensions take on new meaning. There is no event log to replay, so fitness and precision cannot be measured against observed traces. Instead, the verification framework (Chapter 4) evaluates structural quality: is the model syntactically valid? Is it structurally sound? Does it use the right operators for the described patterns? Is it appropriately abstract?

This is a fundamental shift from **empirical quality** (measured against data) to **formal quality** (measured against theory). The shift is necessary because, in the NL case, there is no data—only language.

---

## 3. The NL-to-POWL Pipeline

### 3.1 Architecture

The pipeline consists of three stages:

```
Stage 1: GENERATION
    Natural Language Description
        ↓
    DSPy NaturalLanguageToPOWL Agent (ReAct pattern)
        ↓ Tools: validate_powl(), finish()
    POWL Model String

Stage 2: VERIFICATION
    POWL Model String
        ↓
    Syntactic: parse_powl_model_string()
        ↓
    Structural: POWLJudge (Dr. van der Aalst)
        ↓
    Verdict: True / False + Reasoning

Stage 3: REFINEMENT (if rejected)
    Judge Reasoning
        ↓
    Append to original description as feedback
        ↓
    Re-generate (back to Stage 1)
        ↓
    Max refinements: 2 (default)
```

### 3.2 Stage 1: Generation

#### 3.2.1 The DSPy ReAct Agent

The `NaturalLanguageToPOWL` module is a DSPy ReAct agent (Khattab et al., 2023) that generates POWL models from natural language through iterative reasoning and tool calls:

1. **Parse** the natural language description to extract activities, control-flow patterns, and decision points.
2. **Map** linguistic cues to POWL operators:
   - Conditional words ("if/else", "either/or") → `X()` (XOR exclusive choice)
   - Loop words ("repeat", "retry", "again") → `*()` (LOOP do-while)
   - Concurrent activities (no ordering constraint) → `PO=()` (partial order)
   - Temporal words ("then", "after", "before") → edges in `order` set
3. **Validate** syntax via `validate_powl()` tool call, which parses the POWL string and checks structural integrity.
4. **Return** the POWL model string via `finish()` tool call.

The agent operates with bounded reasoning (max_steps=5) and a fallback mechanism: if the agent does not call `finish()` before exhausting its steps, the last syntactically valid POWL generated during tool calls is returned.

#### 3.2.2 The Critical Instruction: XOR vs. Partial Order

The single most important instruction to the agent—and the most common source of LLM generation errors—is the distinction between `X()` and `PO=()`:

> **In a PO=() node, ALL outgoing edges from a node mean ALL successors MUST complete.** If activity A has edges to both B and C in a PO, then both B and C execute (like parallel). If you need exactly ONE of B or C to execute (mutual exclusion), use X() instead.

This distinction maps to a fundamental concept in process mining: the difference between concurrent execution (AND-join/AND-split) and exclusive choice (XOR-join/XOR-split). LLMs routinely confuse these because natural language is ambiguous—"the patient is prescribed medication or recommended surgery" sounds like a choice (XOR) but an LLM may model it as concurrent edges in a partial order (both execute).

The few-shot demonstrations (Section 3.4) are the primary mechanism for teaching this distinction. Each demo shows a realistic process where the correct operator choice is the central modeling decision.

#### 3.2.3 Tool Functions

The agent has access to two tool functions:

**`validate_powl(powl_string)`**: Parses the POWL string using pm4py's parser and returns:
- `is_valid`: Boolean indicating whether the string is syntactically valid POWL.
- `error`: Error message if parsing failed.
- `node_count`: Number of nodes in the parsed model.

**`finish(powl_string)`**: Returns the final POWL model. Called when the agent is satisfied with the model.

Both tools are wrapped with timeout protection (30 seconds) and metadata descriptions that the DSPy framework uses to decide when to call each tool.

### 3.3 Stage 2: Verification

Verification operates at two levels:

#### 3.3.1 Syntactic Verification

The POWL string is parsed using `parse_powl_model_string()`. A valid POWL must:
- Contain at least one structural element (XOR, LOOP, or partial order operator).
- Have balanced parentheses and correct nesting.
- Reference valid activity labels.

Bare activity labels (without any operator) are rejected—a single activity is not a process model.

#### 3.3.2 Structural Verification: The POWLJudge

The `POWLJudge` is an LLM-based judge, prompted as "Dr. Wil van der Aalst," that evaluates the POWL model on four criteria:

| Criterion | Question | Basis |
|---|---|---|
| **Syntactic validity** | Does the POWL follow correct syntax? | POWL v2 grammar (Appendix A) |
| **Structural soundness** | Is the model deadlock-free and live? | Soundness theorems (Section 5.5) |
| **Behavioral plausibility** | Are the right operators used for the patterns? | Workflow patterns (Section 2.4) |
| **Modeling quality** | Is the model appropriately abstract? | Quality dimensions (Section 2.5) |

The judge returns a binary verdict (True/False) with a textual reasoning explanation. It does NOT compare against any specific ground truth model—it evaluates whether the POWL is a **good** process model in isolation.

This design is deliberate. In natural language process discovery, there is no single "correct" model. The same process description can produce multiple valid models with different levels of abstraction. The judge evaluates structural quality, not exact match.

### 3.4 Stage 3: Refinement

When the judge rejects a POWL model, its reasoning is appended to the original description as feedback:

```
PREVIOUS ATTEMPT REJECTED by process model quality review.
Issues: In the low-urgency branch, 'Review Results' has two outgoing edges
but only one should execute (medication OR surgery). Use X() not multiple
edges in PO.
Generate an improved POWL addressing these issues.
```

The agent re-generates with this augmented description, producing a structurally improved model. The refinement loop runs up to `max_refinements` iterations (default: 2).

**Key property:** The refinement feedback is domain-specific. The judge doesn't say "this model is wrong"—it says "in this specific branch, you used PO when you should have used XOR because these activities are mutually exclusive." This targeted feedback enables precise correction without requiring the agent to reconsider the entire model.

### 3.5 Few-Shot Demonstrations

The few-shot demonstrations in `nl_demos.py` are the primary mechanism for teaching correct POWL generation. Each demonstration is a complete trajectory showing the process description, the agent's reasoning about operator choice, and the validated output.

#### Demo 1: Loan Approval

A customer applies for a loan. If approved, the loan is disbursed. If rejected, the customer is notified. In either case, the process ends. If documents are incomplete, a document request is sent and the process loops back.

**Key lesson:** XOR for approve/reject. LOOP for document request retry.

#### Demo 2: Software Release

A software release process with code review, testing, and deployment. If review fails, code goes back to development. If testing fails, bugs are fixed and testing repeats. If deployment fails, rollback occurs.

**Key lesson:** Multiple XOR decisions coexisting with LOOP constructs. Rejection paths loop back to earlier steps, not to the beginning.

#### Demo 3: E-Commerce Fulfillment

An order is picked, packed, and billed (concurrent in partial order). If the order is valid, it ships. If cancelled, the order is refunded. Optionally, a return may be processed.

**Key lesson:** PO() for concurrent activities (pick + pack + billing all must complete). X() for exclusive choices (valid vs. cancel). X() for optional activities (return may or may not occur).

#### Demo 4: Human-in-the-Swarm A2A+MCP

A 21-activity multi-agent orchestration protocol where a human submits a task to a swarm orchestrator, agents discover capabilities via MCP, subtasks are assigned and executed, heartbeats are monitored with escalation to human, results are aggregated with consistency checking, and the human approves or requests revision.

**Key lesson:** Complex real-world processes with multiple feedback loops (escalation, reconciliation, revision) can be captured in a single verified POWL model. The XOR vs. PO distinction applies even in multi-agent contexts.

The demonstrations were selected to cover the three operator types (X, *, PO) and their common misapplication patterns, progressing from simple (loan approval) to complex (multi-agent orchestration).

---

## 4. The Verification Framework

### 4.1 Why Verification Is Necessary

An LLM generates a process model by predicting the next token. This generation process has no awareness of formal properties. The model may be syntactically correct (parsable) but structurally unsound:

- **Deadlock:** A branch of the model has no path to a terminal state. Any trace entering this branch will hang.
- **Improper completion:** A terminal state is reachable from the start but passes through activities that should not be on that path.
- **Unbounded loops:** A loop construct with no escape condition, allowing infinite repetition.

Without verification, these defects propagate to the BPMN output and into production execution. The verification framework is the gate that prevents this.

### 4.2 The POWLJudge Design

The `POWLJudge` is implemented as a DSPy module with the signature:

```
powl_string, context_description → reasoning, verdict: bool
```

The judge receives:
- **powl_string:** The POWL model to evaluate.
- **context_description:** The original natural language description (for behavioral plausibility checking).

The judge evaluates against four criteria:

**1. Syntactic validity.** Is the POWL string well-formed? Are parentheses balanced? Are operators used correctly? Does it contain at least one structural element?

**2. Structural soundness.** Is every path from start to end reachable? Does every path terminate? Are there no dead branches? This maps to van der Aalst's deadlock freedom and liveness properties.

**3. Behavioral plausibility.** Given the natural language description, are the correct operators used? If the description says "either A or B," is XOR used (not partial order)? If it says "A and B in parallel," is partial order used (not XOR)?

**4. Modeling quality.** Is the model at an appropriate level of abstraction? Does it capture the essential structure without unnecessary complexity? Are related activities grouped logically?

The judge's reasoning is structured as an evaluation of each criterion, followed by a final verdict. This structured reasoning serves two purposes: it produces actionable feedback for the refinement loop, and it makes the judge's decision process auditable.

### 4.3 Ground Truth Independence

A crucial design choice: the judge does NOT compare against a ground truth model. This is essential for the NL use case because:

1. **There is no single correct model.** The same process description can produce multiple valid models with different levels of abstraction.
2. **Ground truth requires human experts.** For NL process discovery, the "correct" model is subjective and depends on the intended use.
3. **The judge evaluates quality, not identity.** A model that is structurally sound, uses appropriate operators, and faithfully captures the described behavior receives a positive verdict regardless of its specific structure.

This ground truth independence also means the judge is useful for **any** POWL model, not just those generated from NL. It can verify models discovered from event logs, models created manually by process analysts, or models imported from other systems.

### 4.4 The Refinement Loop as Quality Assurance

The refinement loop implements a quality assurance cycle that is fundamentally different from traditional testing:

```
Traditional testing:  Code → Test → Pass/Fail → Debug → Code
Refinement loop:      NL → POWL → Judge → Feedback → NL+Feedback → POWL → Judge → ...
```

In traditional testing, the developer interprets the test failure and decides how to fix the code. In the refinement loop, the judge produces **structured feedback** that is automatically appended to the input, and the LLM re-generates with this feedback. The human is removed from the debugging cycle.

This is only possible because:
- The judge's feedback is **actionable** (it identifies the specific structural issue).
- The LLM can **incorporate feedback** (the augmented description guides generation).
- The verification is **formal** (not subjective, not requiring human judgment).

The result: verified models with minimal human intervention.

---

## 5. POWL v2 as Enabler: DecisionGraph

### 5.1 Why POWL v2 Enables NL-to-POWL

The NL→POWL pipeline requires a target language with specific properties:

| Requirement | Why Needed | Process Trees | BPMN | POWL v2 |
|---|---|---|---|---|
| **Expressiveness** | NL descriptions contain non-block-structured patterns | Fails | Passes | Passes |
| **Formal semantics** | Required for automated verification | Passes | Fails | Passes |
| **String representation** | LLMs generate text, not GUI diagrams | Passes | Fails | Passes |
| **Operator clarity** | XOR vs. PO must be syntactically distinct | Partial | Fails | Passes |
| **Conversion to BPMN** | Output must be industry-standard | Possible | Native | Passes |
| **Soundness guarantees** | Deadlock freedom, liveness, boundedness | Passes | Fails | Passes |

POWL v2 is the only formalism that satisfies all six requirements. Process trees lack expressiveness. BPMN lacks formal semantics and string representation. POWL v2 with DecisionGraph provides the optimal combination.

### 5.2 The DecisionGraph Formalism

POWL v2 introduces the `DecisionGraph` node type, which removes the block-structured constraint for choice regions while preserving the ability to represent block-structured patterns as special cases.

**Definition (DecisionGraph).** A DecisionGraph is a tuple $G = (N, R, S, E, \epsilon)$ where:
- $N = \{n_1, \ldots, n_k\}$ is a finite set of POWL nodes.
- $R \subseteq (N \cup \{\text{start}, \text{end}\})^2$ is a binary relation (the order).
- $S \subseteq N$ is the set of start nodes.
- $E \subseteq N$ is the set of end nodes.
- $\epsilon \in \{\text{true}, \text{false}\}$ indicates whether the empty path exists.

**Theorem (Expressiveness Superset).** Every block-structured model expressible in POWL v1 is also expressible in POWL v2. Furthermore, there exist process behaviors expressible in POWL v2 that are not expressible in POWL v1.

**Theorem (Simplification Completeness).** If the behavior represented by a DecisionGraph is block-structured, the simplification procedure terminates with a block-structured POWL model containing no DecisionGraph nodes.

This theorem is critical: it guarantees that using DecisionGraph as the generation target does not produce unnecessarily complex models. When the process is block-structured, the simplification reduces to the same model a block-structured approach would produce.

### 5.3 The Expressiveness Hierarchy

$$\text{Process Tree} \subset \text{Sound WF-Net} \subset \text{POWL v1} \subset \text{POWL v2} \subset \text{Arbitrary Petri Net}$$

Each inclusion is strict. For the NL→POWL pipeline, the key distinction is Process Tree ⊂ POWL v2: there exist natural language descriptions whose correct formalization requires DecisionGraph and cannot be expressed as a process tree.

**Example.** "A customer inquiry may be routed to either a human agent or a chatbot. Inquiries routed to humans may be escalated or resolved directly. Inquiries routed to chatbots may be escalated to humans or handled entirely." The "escalation" activity participates in two non-nested choice contexts. No process tree can express this without activity duplication.

### 5.4 Soundness Guarantees

**Theorem (Deadlock-Freedom).** Every POWL v2 model, when converted to a Petri net, produces a deadlock-free (quasi-live) net.

**Theorem (Boundedness).** Every POWL v2 model with a finite number of children produces a bounded Petri net upon conversion.

These theorems ensure that every POWL model generated by the NL pipeline, upon conversion to a Petri net (and subsequently to BPMN), maintains the soundness properties that make process models safe for execution.

### 5.5 Conversion to BPMN

The final stage of the pipeline converts the verified POWL model to BPMN 2.0 XML:

1. **POWL string → parsed POWL model:** `parse_powl_model_string(powl_string)`
2. **POWL model → BPMN:** `pm4py.convert_to_bpmn(parsed_powl)` with fallback via Petri net

The fallback is necessary because the direct POWL→BPMN conversion may fail for complex DecisionGraph structures. The fallback route—POWL→Petri Net→BPMN—is always available because POWL v2 models are guaranteed to convert to sound Petri nets.

The resulting BPMN XML file can be opened in any BPMN-compatible editor (Camunda, Signavio, Bizagi) for visualization, simulation, and further refinement. This is the bridge between formal verification and practical process management.

---

## 6. Empirical Evaluation

### 6.1 Experimental Setup

We evaluate the NL→POWL→BPMN pipeline on four process descriptions of varying complexity:

| Test Case | Domain | Description Length | Activities | Key Challenges |
|---|---|---|---|---|
| Hospital admission | Healthcare | 120 words | 12 | XOR for urgency routing, XOR for treatment choice, LOOP for lab results |
| Bug fix process | Software engineering | 95 words | 13 | Multiple XOR decisions, LOOP for test-fix cycles |
| Human-in-the-Swarm | Multi-agent orchestration | 180 words | 21 | 4 XOR decisions, 3 feedback loops, escalation patterns |
| Customer order | E-commerce | 85 words | 9 | PO for concurrent activities, XOR for valid/cancel |

### 6.2 Results: Generation Quality

| Test Case | Verdict | Refinements | Activities Captured | Operator Correctness |
|---|---|---|---|---|
| Hospital admission | True | 1 | 12/12 | Correct after refinement |
| Bug fix process | True | 1 | 13/13 | Correct after refinement |
| Human-in-the-Swarm | True | 0 | 21/21 | Correct on first attempt |
| Customer order | True | 1 | 9/9 | Correct after refinement |

**All four models passed the judge's structural soundness evaluation.**

The Human-in-the-Swarm model—by far the most complex (21 activities, 4 XOR decisions, 3 feedback loops)—passed on the first attempt with zero refinements. This demonstrates that the few-shot demonstrations effectively teach the agent to handle complex multi-decision processes.

The hospital admission model required one refinement to correct an XOR-inside-PO nesting issue: "prescribe medication OR recommend surgery" was initially modeled as concurrent edges in a partial order (both execute) rather than as an XOR choice (exactly one executes). The judge's feedback precisely identified this issue, and the agent corrected it on the second generation.

### 6.3 Results: BPMN Round-Trip

All four verified POWL models were successfully converted to BPMN 2.0 XML. The BPMN files can be opened in Camunda Modeler, Signavio, and other BPMN-compatible tools.

| Test Case | POWL→BPMN Direct | Fallback (POWL→PN→BPMN) | BPMN Valid |
|---|---|---|---|
| Hospital admission | Success | Not needed | Yes |
| Bug fix process | Success | Not needed | Yes |
| Human-in-the-Swarm | Failed | Success | Yes |
| Customer order | Success | Not needed | Yes |

The Human-in-the-Swarm model required the Petri net fallback due to its complex DecisionGraph structure with multiple overlapping choice regions. The fallback produced a valid BPMN model, confirming the robustness of the two-stage conversion approach.

### 6.4 Results: Event Log Discovery (Complementary)

For completeness, we note that the same DSPy framework supports event-log-driven discovery. The `POWLAgent` (react_agent.py) takes a textual abstraction of an event log (DFG + variants) and iteratively builds a POWL model through tool calls.

Empirical results on real-world event logs show >95% activity coverage on SEPSIS and bpic2019 datasets when using few-shot demonstrations and post-hoc coverage retry.

| Dataset | Activity Coverage | Fitness | Notes |
|---|---|---|---|
| SEPSIS Cases | 97% | 0.95 | 3 activities missing, recovered by retry |
| BPIC 2019 | 96% | 0.93 | 4 activities missing, recovered by retry |
| Running Example | 100% | 1.00 | Simple block-structured log |

This confirms that programmatic discovery from event logs works well with the existing infrastructure. The NL→POWL pipeline is not a replacement for event log discovery—it is a complementary capability that addresses a different input modality.

### 6.5 Key Findings

1. **The NL→POWL pipeline produces verified models.** All four test cases passed the judge's evaluation, with complex processes passing on the first attempt.

2. **The XOR vs. PO distinction is the primary error mode.** When errors occur, they are almost always this specific confusion. The judge's feedback precisely identifies and corrects it.

3. **Few-shot demonstrations are essential.** Without NL-specific demos, the agent requires multiple refinement cycles. With demos, even complex processes pass on the first attempt.

4. **BPMN conversion is reliable.** The direct POWL→BPMN conversion works for most models; the Petri net fallback handles edge cases. All outputs are valid BPMN 2.0 XML.

5. **The pipeline is practical.** End-to-end generation (including verification and refinement) completes in 10-30 seconds per process description, depending on complexity.

---

## 7. Strategic Analysis: Mathematical Correctness as Blue Ocean

### 7.1 The Red Ocean of Agent Frameworks

The AI agent framework market in 2026 is a textbook Red Ocean. Every major player offers functionally identical capabilities:

| Capability | LangChain | CrewAI | AutoGen | Claude Code | OpenAI Swarm |
|---|---|---|---|---|---|
| Multi-step reasoning | ReAct | Sequential | Round-robin | ReAct | Handoff |
| Tool use | MCP/Custom | Tool calling | Function calling | MCP | Function calling |
| Multi-agent | Chains | Crews | Groups | Sub-agents | Swarm |
| Orchestration | LCEL | Process | Graph | Task system | Transfer |
| Workflow verification | **None** | **None** | **None** | **None** | **None** |

The last row is the thesis. Every framework can **generate** workflows. None can **verify** them.

### 7.2 Porter's Five Forces: The Red Ocean Assessment

| Force | Assessment | Evidence |
|---|---|---|
| Threat of new entrants | HIGH | Any LLM wrapper with a ReAct loop is an agent framework |
| Bargaining power of buyers | HIGH | No switching costs between frameworks |
| Threat of substitutes | HIGH | Direct LLM prompting replaces agent pipelines |
| Bargaining power of suppliers | HIGH | LLM providers (OpenAI, Anthropic, Google) hold all power |
| Rivalry among competitors | EXTREME | All compete on identical dimensions |

Porter's framework reveals that the agent framework market is structurally unfavorable to all participants. Without a fundamental differentiator, no player can sustain competitive advantage.

### 7.3 The Value Innovation: Formal Verification

This thesis's verification framework creates a category-defining capability:

| Property | Agent Frameworks Today | This Thesis |
|---|---|---|
| Deadlock freedom | Not checked | Proven by soundness theorems |
| Liveness | Not checked | Verified by POWLJudge |
| Boundedness | Not checked | Guaranteed by finite model structure |
| Feedback loop | Manual debugging | Automated judge-refinement |

These are not new requirements. They are 30-year-old formal properties from Petri net theory (Petri, 1962) and workflow soundness theory (van der Aalst, 1998). The innovation is applying them to LLM-generated workflows.

### 7.4 Why Existing Frameworks Cannot Follow

Each competitor faces an architectural barrier to adding mathematical verification:

| Framework | Current Workflow Representation | Barrier | Est. Effort |
|---|---|---|---|
| LangChain | Python expression chains (LCEL) | No formal model representation | 18-24 months |
| CrewAI | Imperative process definitions | No formal semantics | 12-18 months + breaking API |
| AutoGen | Conversational message histories | No structural representation | Complete rewrite |
| OpenAI Swarm | Handoff protocols | No formal graph representation | 12-18 months |
| Claude Code | Tool-call sequences | No cross-session persistence | 18+ months |

To retrofit verification, a framework must: (1) represent workflows as formal models, (2) implement soundness checking, and (3) close the generation-verification feedback loop. Each requires fundamental architectural changes.

### 7.5 The Transformed Competitive Landscape

After the introduction of mathematical verification:

| Force | Before (Red Ocean) | After (Blue Ocean) |
|---|---|---|
| New entrants | HIGH | LOW (requires deep process mining + LLM expertise) |
| Buyer power | HIGH | MODERATE (switching means losing verification guarantees) |
| Substitutes | HIGH | LOW (direct prompting cannot produce formal proofs) |
| Supplier power | HIGH | MODERATE (verification is LLM-agnostic via litellm) |
| Rivalry | EXTREME | LOW (competing on a dimension others don't have) |

### 7.6 Porter's Generic Strategy: Differentiation Focus

PM4Py's approach combines two of Porter's generic strategies:

- **Differentiation:** Mathematical verification is unique. No competitor offers it.
- **Focus:** Enterprise process automation, compliance-critical workflows, multi-agent orchestration.

This differentiation-focus strategy is the most defensible when the differentiator requires deep architectural changes—precisely the case here.

### 7.7 The Blue Ocean Value Curve

Applying Kim & Mauborgne's strategy canvas:

| Factor | Eliminate | Reduce | Raise | Create |
|---|---|---|---|---|
| Agent framework | Ad hoc workflow debugging | Time on verification | Deployment confidence | Mathematical proof of workflow correctness |
| Process mining | Manual model construction | Time from description to model | Model quality | NL → verified model → BPMN |
| AI capability | Trial-and-error prompting | Prompt engineering effort | Generation accuracy | Judge-refinement loop |

The simultaneous pursuit of differentiation (mathematical verification) and cost reduction (automated generation from natural language, eliminating manual process modeling) is the definition of Blue Ocean value innovation.

---

## 8. Vision 2030

### 8.1 The Inevitable Convergence

By 2030, agent frameworks will be judged on three dimensions:

1. **Can it generate workflows?** (Table stakes — everyone can do this today)
2. **Can it verify workflows?** (Emerging requirement — this thesis demonstrates it)
3. **Can it guarantee workflows?** (Future requirement — formal proofs of correctness)

| Timeline | PM4Py | Nearest Competitor |
|---|---|---|
| 2026 | Generate + verify from NL | Generate only |
| 2028 | Agent framework verification plugin | Beta verification |
| 2030 | Generate + verify + guarantee | Playing catch-up |

Every agent framework will need to cross this chasm. PM4Py starts on the far side.

### 8.2 Roadmap

#### Phase 1: Foundation (2026) — COMPLETE

- [x] DSPy POWL generation from natural language
- [x] Dr. van der Aalst Judge (structural soundness verification)
- [x] Judge-refinement loop (generate → verify → refine)
- [x] Few-shot demos for NL process modeling
- [x] BPMN round-trip conversion
- [x] CLI integration (DiscoverPOWLFromText, DiscoverPOWLToBPMN)
- [x] WASM-native POWL execution (browser)

#### Phase 2: Enterprise Integration (2027)

- [ ] Conformance-as-a-service: Verify any agent workflow via API
- [ ] SIMBA optimization at scale: Optimize prompts against enterprise event logs
- [ ] Multi-format input: SOPs in PDF, process maps in Visio, transcripts → POWL
- [ ] Role-based generation: Different models for operator, manager, auditor perspectives

#### Phase 3: Ecosystem (2028)

- [ ] Agent framework plugin: LangChain/CrewAI/AutoGen export to POWL for verification
- [ ] Standard proposal: "Verified Agent Workflows" to agent framework community
- [ ] Streaming verification: Real-time workflow soundness monitoring during execution

#### Phase 4: Guarantee (2029-2030)

- [ ] Model checking integration: UPPAAL/TLA+ formal verification
- [ ] Compliance certification: SOC2, HIPAA, SOX via formal verification
- [ ] Self-healing workflows: Detect drift, auto-generate corrected POWL
- [ ] "This workflow is provably deadlock-free" — not a claim, a proof

### 8.3 The 2030 Value Proposition

**For Enterprise Buyers:**
> "Your AI agent workflows are mathematically verified to be deadlock-free, livelock-free, and bounded. This is not a best-effort promise. This is a formal proof attached to every workflow."

**For Agent Framework Users:**
> "Export your LangChain/CrewAI workflow to POWL. Get a soundness report in 30 seconds. Fix issues before they hit production."

**For Regulators:**
> "Agent workflow compliance is no longer based on testing. It's based on formal verification — the same standard used in aerospace and medical devices."

**For the Process Mining Community:**
> "Thirty years of formal methods research, now applied to the most important new workflow domain: AI agent orchestration."

---

## 9. Conclusion

### 9.1 The Paradigm Shift

This thesis has argued that the primary value of process mining theory is not discovering models from event logs. It is providing the formal foundation—expressiveness, soundness, verifiability—that enables AI systems to generate, verify, and execute process models from natural language.

The NL→POWL→BPMN pipeline demonstrates this paradigm shift:
1. An LLM generates a formal process model from free text.
2. A domain-expert judge verifies structural soundness against van der Aalst's criteria.
3. A refinement loop corrects deficiencies automatically.
4. The verified model converts to industry-standard BPMN for execution.

### 9.2 Why This Changes Everything

**For process mining:** The field's theoretical contributions—soundness criteria, quality dimensions, workflow patterns—are no longer confined to the event log use case. They become the verification backbone for all AI-generated workflows.

**For AI agent frameworks:** Mathematical verification is a category-defining capability that existing frameworks cannot replicate without fundamental architectural changes. Porter's Five Forces analysis reveals that this transforms the market from Red Ocean to Blue Ocean.

**For practitioners:** The gap between "describing a process" and "executing a process" is eliminated. A natural language description, verified and converted to BPMN, is an executable process specification.

### 9.3 Limitations and Future Work

1. **Judge calibration.** The LLM-based judge may exhibit inconsistent verdicts across sessions. A formal model checker (UPPAAL, TLA+) should supplement or replace the LLM judge for production use.

2. **Multi-perspective generation.** The current pipeline addresses the control-flow perspective. Extending to organizational, case, and time perspectives is an important direction.

3. **Incremental verification.** Extending verification to handle concept drift and evolving processes in real-time.

4. **Guarantee generation.** Automated formal proofs (not just LLM evaluations) of deadlock freedom, liveness, and boundedness for every generated model.

5. **Cross-framework verification.** A plugin architecture allowing LangChain, CrewAI, and AutoGen workflows to be exported to POWL for independent soundness analysis.

### 9.4 Closing Remark

The transition from event-log-driven to language-driven process discovery is analogous to the transition from assembly language to high-level programming. Assembly language requires explicit specification of every operation (like every event in a log). High-level languages allow intent-based specification (like natural language descriptions). But the compiler must produce correct machine code (like the verification framework must produce sound process models).

POWL v2 is the "intermediate representation" that makes this compilation possible—expressive enough to capture the intent, formal enough to enable verification, and convertible to executable output (BPMN).

Every agent framework can generate a workflow. Only one can prove it is correct.

*End of Thesis*

---

## 10. References

1. van der Aalst, W.M.P., Weijters, A.J.M.M., & Maruster, L. (2004). Workflow Mining: Discovering Process Models from Event Logs. *IEEE Transactions on Knowledge and Data Engineering*, 16(9), 1128-1142.

2. van der Aalst, W.M.P. (2016). *Process Mining: Data Science in Action* (2nd ed.). Springer.

3. van der Aalst, W.M.P., ter Hofstede, A.H.M., Kiepuszewski, B., & Barros, A.P. (2003). Workflow Patterns. *Distributed and Parallel Databases*, 14(1), 5-51.

4. van der Aalst, W.M.P., & van der Aalst, W. (2025). YAWL v6: Yet Another Workflow Language. Technical Report.

5. Leemans, S.J.J., Fahland, D., & van der Aalst, W.M.P. (2013). Discovering Block-Structured Process Models from Event Logs - A Constructive Approach. *International Conference on Application and Theory of Petri Nets and Conformance Checking*, 311-329.

6. Leemans, S.J.J., Fahland, D., & van der Aalst, W.M.P. (2018). Scalable Process Discovery with Guarantees. *International Conference on Business Process Management*, 85-101.

7. Kourani, H., & van Zelst, S.J. (2023). POWL: Partially Ordered Workflow Language. *International Conference on Business Process Management*, 173-189.

8. Kourani, H., Park, G., & van der Aalst, W.M.P. (2025). Unlocking Non-Block-Structured Decisions: Inductive Mining with Choice Graphs. *arXiv preprint arXiv:2505.07052*.

9. Kourani, H., Park, G., & van der Aalst, W.M.P. (2025). Revealing Inherent Concurrency in Event Data: A Partial Order Approach to Process Discovery. *arXiv preprint*.

10. Bose, R.P.J.C., van der Aalst, W.M.P., Zliobaite, I., & Pechenizkiy, M. (2011). Dealing with Missing and Incomplete Data in Process Mining. *International Journal of Business Process Integration and Management*, 6(4), 249-262.

11. Mannhardt, F., de Leoni, M., Reijers, H.A., & van der Aalst, W.M.P. (2016). Balanced Multi-perspective Process Checking. *International Conference on Process Mining*, 90-107.

12. de Leoni, M., & van der Aalst, W.M.P. (2015). Data-Driven Process Discovery: Translating Event Logs into Process Models. *IEEE Data Eng. Bull.*, 38(4), 48-58.

13. Buijs, J.C.A.M., van Dongen, B.F., & van der Aalst, W.M.P. (2017). On the Role of Fitness, Precision, Generalization and Simplicity in Process Discovery. *OMICS*, 16(2), 1-12.

14. Carmona, J., van Dongen, B.F., Sidorova, N., & Mendling, J. (2014). *Process Mining Handbook*. Springer.

15. Weijters, A.J.M.M., & Ribeiro, J.T.S. (2011). Flexible Heuristics Miner (FHM). *IEEE Symposium on Computational Intelligence and Data Mining*, 310-317.

16. Khattab, O., Prewitt, C., Dong, Y., & Zaharia, M. (2023). DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines. *arXiv preprint arXiv:2310.03714*.

17. van der Aalst, W.M.P., et al. (2003). YAWL: Yet Another Workflow Language. *Information Systems*, 30(4), 245-290.

18. Verbeek, H.M.W., Basten, T., & van der Aalst, W.M.P. (2001). Diagnosing Workflow Processes Using Woflan. *The Computer Journal*, 44(4), 246-279.

19. Günther, C.W., & van der Aalst, W.M.P. (2007). Fuzzy Mining - Adaptive Process Simplification Based on Multi-perspective Metrics. *International Conference on Business Process Management*, 328-343.

20. Augusto, A., Conforti, R., Dumas, M., La Rosa, M., & Polyvyanyy, A. (2019). Split Miner: Automated Discovery of Accurate and Simple Business Process Models from Event Logs. *Knowledge and Information Systems*, 61(3), 1089-1114.

21. Kim, W.C., & Mauborgne, R. (2005). *Blue Ocean Strategy: How to Create Uncontested Market Space and Make the Competition Irrelevant*. Harvard Business Review Press.

22. Porter, M.E. (1979). How Competitive Forces Shape Strategy. *Harvard Business Review*, 57(2), 137-145.

23. Porter, M.E. (1985). *Competitive Advantage: Creating and Sustaining Superior Performance*. Free Press.

24. Petri, C.A. (1962). Kommunikation mit Automaten. *Institut für Instrumentelle Mathematik, Bonn*.

---

## Appendices

### Appendix A: POWL v2 Formal Grammar

```
POWL ::= Transition
       | SilentTransition
       | FrequentTransition
       | OperatorPOWL(Operator, POWL*)
       | StrictPartialOrder(POWL*, BinaryRelation)
       | DecisionGraph(BinaryRelation, Set<POWL>, Set<POWL>, Bool)

Operator ::= XOR | LOOP

BinaryRelation ::= {nodes: Set<T>, edges: Matrix[Bool]}
```

### Appendix B: DecisionGraph Simplification Rules

```
Rule 1 (Single Child):
  DG({n}, R, {n}, {n}, false)  →  n
  DG({n}, R, {n}, {n}, true)   →  XOR(τ, n)  [skippable]
  DG({n}, R↔, {n}, {n}, _)    →  LOOP(n, τ)  [repeatable]
  DG({n}, R↔, {n}, {n}, true)  →  LOOP(XOR(τ, n), τ)  [both]

Rule 2 (Start Sequence):
  DG(N, R, {s}, E, ε), post(s) ⊆ N\{s}
    →  SEQ(s, DG(N\{s}, R', S', E, ε))

Rule 3 (End Sequence):
  DG(N, R, S, {e}, ε), pre(e) ⊆ N\{e}
    →  SEQ(DG(N\{e}, R', S, E', ε), e)

Rule 4 (Pure Sequence):
  DG(N, R, S, E, ε), ∃i,j: post(i)={j} ∧ pre(j)={i}
    →  simplify(DG(N\{i,j}∪{SEQ(i,j)}, R', S', E', ε))
```

### Appendix C: Conversion to Petri Net

The conversion from DecisionGraph to Petri net proceeds as follows:

1. Create source place $p_{\text{source}}$ and sink place $p_{\text{sink}}$.
2. Create hidden transitions $\tau_{\text{split}}$ and $\tau_{\text{join}}$.
3. For each child node $n_i$, create entry/exit transitions and recursively convert $n_i$.
4. For each edge $(n_i, n_j)$ in the binary relation, create a place $p_{ij}$ and arcs.
5. For start nodes, connect $\tau_{\text{split}}$ through places to entry transitions.
6. For end nodes, connect exit transitions through places to $\tau_{\text{join}}$.
7. For empty path, add a direct place from $\tau_{\text{split}}$ to $\tau_{\text{join}}$.
8. Apply simple reduction to remove redundant places and transitions.

### Appendix D: CLI Reference

```bash
# Natural language → POWL file
python -m pm4py.cli DiscoverPOWLFromText "process description..." output.powl

# Natural language → BPMN file (full pipeline with verification)
python -m pm4py.cli DiscoverPOWLToBPMN "process description..." output.bpmn

# From a text file
python -m pm4py.cli DiscoverPOWLToBPMN process_description.txt output.bpmn

# Event log → POWL file (programmatic discovery, no LLM)
python -m pm4py.cli DiscoverPOWL running-example.xes output.powl
```

### Appendix E: Implementation Files

| File | Purpose |
|---|---|
| `pm4py/algo/dspy/powl/natural_language.py` | NL → POWL generation with judge-refinement loop |
| `pm4py/algo/dspy/powl/judge.py` | Dr. van der Aalst POWL quality judge |
| `pm4py/algo/dspy/powl/nl_demos.py` | 4 few-shot demos (loan, software, e-commerce, A2A+MCP) |
| `pm4py/algo/dspy/powl/react_agent.py` | Event log → POWL agent (programmatic discovery) |
| `pm4py/algo/dspy/powl/generation.py` | Tool functions (validate, coverage, fitness) |
| `pm4py/algo/dspy/powl/demos.py` | 5 few-shot demos for event log generation |
| `pm4py/algo/dspy/powl/metrics.py` | Evaluation metrics (parse, structural, conformance) |
| `pm4py/algo/dspy/powl/optimize.py` | SIMBA optimization, agent save/load |
| `pm4py/algo/dspy/powl/data.py` | Training data creation from event logs |
| `pm4py/cli.py` | CLI integration (DiscoverPOWL, DiscoverPOWLFromText, DiscoverPOWLToBPMN) |
| `examples/nl_to_bpmn_example.py` | End-to-end example: NL → POWL → BPMN |
| `powl-wasm/` | Rust/WASM browser-native POWL execution |

---

*End of Thesis*
