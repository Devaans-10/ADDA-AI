# Team plan — September 20, 2026

Aim for a stable morning/afternoon demo, preserving the final submission deadline of **20:00 IST today**. The initial Coding route is complete; document retrieval and attached-document Research now work locally. [PROJECT_STATUS.md](../PROJECT_STATUS.md) owns the live handoff and exact next action.

## NOW — protect the working demo

| Owner | Owned work | Acceptance |
| --- | --- | --- |
| Teammate 1 — frontend | `apps/web/**` | Upload/sample flow, citation cards, code copy, responsive layout and clear error/provider states work in browser |
| Teammate 2 — integration lead | Shared API/graph/schema/config/dependencies; final merge | Full backend suite and web checks pass after consolidation; original Cursor edits preserved |
| Teammate 3 — documents | `services/api/app/agents/document.py` and document tests | Budget/page citation and abstention demo pass; token isolation and limits pass; process-local limitations disclosed |
| Teammate 4 — services and demo | Search/Research modules/tests; cloud proposal and demo preparation | Attached-document Research passes; external readiness is labeled accurately; recording and pitch ready |

Only the integration lead merges shared graph, schema, dependency and infrastructure changes. Cursor is being paused while Codex consolidates the isolated MVP worktree; resume only with distinct file ownership. One branch/worktree per active owner. Never ask Cursor and Codex to edit the same files concurrently.

1. Complete the combined regression run and update verification status.
2. Consolidate `codex/hackathon-mvp` with the original repository without overwriting Cursor work or local environment settings.
3. Run [DEMO.md](../DEMO.md) in the consolidated copy and keep a known-good revision.

## NEXT — time-box external readiness

- After the user's pending approval, make two small Bedrock requests using named profile `nexusai`. STS already passed; model inference has not.
- If a Tavily key becomes available, test a real Search request and a bounded web Research request. Otherwise retain the visible key-needed state.
- Decide whether to deploy the verified Coding/Search subset or first add shared document storage. The prepared Lambda template intentionally disables local documents. Do not describe that subset as the full local MVP.
- Validate/build infrastructure and smoke-test any deployment before announcing a URL. Docker, SAM and hosting have not been verified.

| Time (IST today) | Gate |
| --- | --- |
| Morning/early afternoon | Stable local demo and consolidated repository |
| By 14:00 | External-provider decision and API freeze; cut unavailable extras |
| By 16:00 | Feature freeze; only demo blockers and deployment fixes |
| By 18:00 | Deployment hard stop; keep a working local fallback |
| By 19:00 | Recording, screenshots, pitch and submission materials ready |
| 20:00 | Final submission |

If a gate has already passed, prioritize the working recording and final checks. Do not consume the final two-hour buffer adding features.

## LATER — after the hackathon baseline

Private S3 originals and shared metadata, semantic embeddings/vector retrieval, OCR, durable history and longer asynchronous Research. No fine-tuning, Kubernetes or Redis. Existing older Cursor prompts are planning material; actual code and PROJECT_STATUS take precedence over their future-feature assumptions.

Acceptance is evidence, not a checkbox: label each feature implemented, verified locally, externally unverified, or verified deployed. Do not claim four live AI agents, semantic RAG or AWS deployment from this local build.
