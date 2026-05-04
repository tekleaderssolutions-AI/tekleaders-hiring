# Phase 3 & 4 Roadmap: Agentic AI Mastery

This document outlines the specific technical implementations planned for the next phases of **Hirix**. We will evolve the system from a "Static Pipeline" to a "Dynamic Agentic Engine" by strictly following the project's Hexagonal Architecture.

---

## 1. Dynamic Orchestration with LangGraph
**Goal**: Move from a hardcoded 17-step pipeline to a dynamic graph where the Agent can "decide" its next move.

*   **Implementation (Layer 4 — Application)**: Create a `MatchingGraph` using **LangGraph**.
*   **Agentic Logic**: 
    1.  Agent receives a Candidate and a JD.
    2.  Agent "Reasons" about the skill gap.
    3.  Agent decides to "Re-parse" a specific section of the resume if data is missing (Self-Correction).
    4.  Agent outputs the final score.

## 2. Advanced Observability (Reasoning Traces)
**Goal**: Store the "Chain of Thought" (CoT) for every AI decision.

*   **Implementation (Layer 6 — Data)**: Add a `reasoning_trace` JSONB column to the `MemoryModel` and `CandidateModel`.
*   **Implementation (Layer 2 — Adapters)**: Update the LLM Agents to output their internal reasoning steps alongside the structured data.
*   **Value**: In the UI, recruiters can click "See Why" and view a bulleted list of the AI's logic for that specific candidate.

## 3. Human-in-the-Loop (HITL) Architecture
**Goal**: Create a reliable verification system where humans and AI collaborate.

*   **Implementation (Layer 5 — Domain)**: Add a `verification_status` Enum to the `Candidate` and `Job` entities (`AI_GENERATED`, `HUMAN_VERIFIED`, `REJECTED`).
*   **Implementation (Layer 1 — API)**: Create a `PATCH /verify/{id}` endpoint.
*   **Logic**: Data is not used for "Matching" until a human marks it as `VERIFIED`.

## 4. Multi-Tool Reasoning (The "Hands" of the Agent)
**Goal**: Allow the Agent to search the database and the web.

*   **Implementation (Layer 2 — Adapters)**: Create a `SearchTool` that connects to the Vector DB.
*   **Implementation (Layer 4 — Application)**: Give the Agent access to this tool.
*   **Example**: User asks: *"Find me candidates similar to John Doe."* The Agent will reason: *"I need John Doe's skills first (Tool 1), then I will search for similar embeddings (Tool 2)."*

## 5. Automated Evaluation Framework (Evals)
**Goal**: Ensure that model updates (e.g., moving from GPT-4o to Claude 3.5 Sonnet) don't break accuracy.

*   **Implementation (New Testing Layer)**: Create a `/tests/evals/` directory.
*   **Logic**: A script will run the Parser against a "Gold Set" of 50 resumes.
*   **Metric**: Use **Levenshtein Distance** for text extraction and **Cosine Similarity** for skill matching to score the AI's accuracy (Goal: >95%).

---

### 🗺️ Architecture Summary for New Features

| Feature | Layer Affected | Impact |
| :--- | :--- | :--- |
| **LangGraph** | Layer 4 (Application) | High — Changes how requests are processed. |
| **Reasoning Traces** | Layer 6 (Data) | Medium — Simple DB migration. |
| **Verification Flow** | Layer 5 (Domain) | High — Changes business logic. |
| **Search Tool** | Layer 2 (Adapters) | Medium — New external connection. |
| **Evaluation Suite** | Cross-cutting / Test | Low — No impact on production code. |
