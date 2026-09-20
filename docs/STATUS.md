## Professional workspace refinement — latest Codex pass

- Audited Cursor changes in the active MVP copy before editing. Preserved the startup script, configured Search key, optional Tavily summary and all backend contracts.
- Replaced dark promotional layout with a neutral light workspace, smaller navigation, focused composer, result-first hierarchy and contextual activity panel. Removed remote font loading.
- Verified Coding fixture, PDF budget/page 2, four-step document Research, mobile navigation and history selection in the browser. Browser error/warning log empty. Desktop/mobile overflow checks passed.
- Backend suite: 71 passed. Final frontend typecheck and production build passed.
- No new live Search or Bedrock call in this pass. Earlier Cursor live Search verification remains historical evidence. Deployment remains user-owned and unverified.

# Verification scope — September 20, 2026

## Frontend redesign (20 Sep 2026, ~15:00 IST)

Redesigned `apps/web` in `outputs/nexusai-mvp` as a dark multi-agent workspace. Backend contracts were not changed. No new npm/Python dependencies. `.env` files were not modified.

- Typecheck passed. Production `next build` passed (static `/`).
- Browser on `http://127.0.0.1:3000` → API `http://127.0.0.1:8000`: Coding fixture (labelled demo, not Bedrock), live Search with 5 real Tavily HTTPS cards, sample PDF budget Q&A (INR 180,000 / page 2), TXT upload Q&A (page 1), Research plan → collect → brief (4 citations), activity timeline, 5 sequential history items, code-block copy fallback, loading/error, 654px and 1440×900 layouts. No horizontal overflow. No Next.js error overlay.
- Still blocked for claims: live Bedrock, AWS deployment.

## Canonical local demo (20 Sep 2026, ~14:20 IST)

Stabilized `outputs/nexusai-mvp` onto **UI `http://127.0.0.1:3000` → API `http://127.0.0.1:8000`**. See [DEMO_GUIDE.md](../DEMO_GUIDE.md).

- Stale listeners on 3002 and 8000–8008 (including the Search-disabled 8001 process) were stopped.
- `/health` on 8000: `provider: demo`, `document: true`, `search: true`.
- Browser judge flow on 3000: Coding fixture, live Search with five HTTPS source cards, sample PDF budget Q&A (INR 180,000 / page 2), attached-document Research, activity panel, five-item session history. API traffic used only `127.0.0.1:8000`.
- Backend: 71 passed. Frontend typecheck and production build passed.
- Still blocked for claims: live Bedrock, AWS deployment. Split checkouts remain unconsolidated.

[PROJECT_STATUS.md](../PROJECT_STATUS.md) is the current execution handoff. This file summarizes evidence and limitations without preserving an obsolete conversation log.

## NOW — verified locally

- Core backend suite: 71 tests passed.
- Frontend type check and production static build passed.
- Browser document and attached-document Research flows completed; no console errors were observed in those checks.
- Coding fixture, document retrieval/page citations and bounded Research are implemented. Live service adapters are tested with mocked providers.
- AWS CLI is installed. Named profile `nexusai` passed STS identity verification; the default profile is not signed in.

Document behavior is lexical/extractive, without embeddings or AI synthesis. Research organizes two evidence checks and cited excerpts. Search is live on the canonical API when `/health` reports `search: true`.

## NEXT — externally unverified

- Bedrock live inference: unverified. Do not copy credentials into documentation or infer model access from STS.
- Docker build/run, AWS SAM validation/build, Lambda runtime and Amplify hosting: unverified. No deployment has occurred and no Git remote is configured.
- Full cloud document support: not implemented. The Lambda template disables documents because the current store is process-local.

Work is isolated on `codex/hackathon-mvp` in `outputs/nexusai-mvp` while the coordinator preserves and consolidates the original repository's Cursor edits. Do not run simultaneous edits in both copies or assume consolidation is complete.

## LATER

Durable storage, embeddings/vector retrieval, OCR, streaming activity, persistent task history and asynchronous expanded Research. None should be presented as current functionality.
