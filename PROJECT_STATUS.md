# NexusAI — execution handoff

## Current goal
Stable, honest hackathon demo by Sep 20 morning/afternoon IST. Local execution only;
PC sleep suspends work. Repo is the source of truth; never restart from scratch.

## Current working state
Root: this directory (`outputs/nexusai`). Branch `main`; baseline HEAD `1ff16f1`.
First Coding fixture route implemented. Search adapter/UI arrived as uncommitted
Cursor work; preserve it. No configured remote. Current owner: Codex coordinator;
Cursor editing status requested before changing shared files.

## Completed / verified
- FastAPI + real LangGraph + clearly labelled fixed Coding fixture.
- Bedrock adapter, AWS diagnostics, AWS CLI installed; Mumbai ap-south-1.
- Tavily adapter + graph node + citations; verified with mocked provider only.
- Fresh audit: 31 backend tests pass; web typecheck and production export pass.

## In progress (file ownership)
- Codex document worker: `services/api/app/agents/document.py`, `tests/test_document.py` only.
- Coordinator: inspection, handoff, then shared API/graph integration after Cursor idle.

## NOW / NEXT / LATER
NOW: safe checkpoint, restore services, local PDF/TXT evidence retrieval with page citations.
NEXT: integrate document upload, refine routing, improve workspace/messages/sources, demo checks.
LATER: bounded Research over Search, live provider verification, deployment and presentation.

## Known bugs / external blockers
- Previously reported Next dev hydration warning; not yet reproduced in this audit.
- No active 3000/8000 listeners at initial inspection; restart required.
- AWS credentials unavailable. Model inference not verified. Do not mark Bedrock connected.
- Live Tavily not verified; inspect key presence without displaying secrets.
- No Docker/SAM/deployment verification. No local model runtime detected.

## Architecture decisions / do not break
Next static export -> FastAPI -> LangGraph. Preserve Cursor Search work and API contracts.
Coding never executes generated code. No secret logging or commits. Backend `.env` ignored.
Document MVP will use honest local lexical retrieval/excerpts, not claim embeddings or AI synthesis.
Document tokens must isolate uploaded content. No silent fixture fallback after real provider failure.

## Commands/tests run this audit
`git status --short`, `git log -5`, file and diff inspection; `pytest -q` (31 passed);
`npm run typecheck` and `npm run build` (passed); `python -m app.check_bedrock`
(expected missing credentials). Installed pypdf/python-multipart; locks pending.

## Exact next action
Confirm Cursor idle, checkpoint its changes, wire document module into schema/API/graph;
start local services and inspect browser hydration before UI polish.
