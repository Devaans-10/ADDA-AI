# Team plan: demo by September 20, 2026, 8 PM IST

The first deliverable is a verified browser → API → LangGraph → Coding → response path. Do not begin parallel feature integration until that path works. The final target is four specialists with real tools and a deployed demo; this scaffold does not claim that target is already complete.

## Four owners

| Owner | Files and responsibility | Acceptance gate |
| --- | --- | --- |
| Teammate 1 — interface | `apps/web/**`; composer, answer rendering, activity, upload and citation presentation | Browser completes a real request; loading/error/501 states are clear; source links are usable; no secret bundled |
| Teammate 2 — orchestrator / integration lead | `services/api/app/**` shared API, graph, schemas and provider code, excluding specialist files assigned below; owns integration | Demo and Bedrock Coding work; input errors, unknown agents, provider failures and routing are tested; no accidental network calls in demo tests |
| Teammate 3 — documents | New `services/api/app/agents/document.py`, document-specific modules and tests; coordinate route/schema changes with owner 2 | A text PDF yields correct page citations; unsupported question abstains; malformed/oversized files fail; separate sessions cannot cross-retrieve |
| Teammate 4 — search / research | New `services/api/app/agents/search.py`, `research.py`, related tools/tests; owns cloud rollout with owner 2 reviewing | Search calls real API; Research reuses it and returns grounded citations; deadlines enforced; deployed smoke tests pass |

Owner 2 alone merges changes to shared dependencies, graph wiring, schemas, root environment templates and infrastructure. Specialist owners submit precise dependency and schema requests. Teammate 4 prepares infrastructure changes in a separate branch and owner 2 integrates them. Each teammate uses one branch/worktree; do not let Cursor and Codex concurrently edit the same files.

Cursor handles each owner's bounded feature edits and local debugging. Codex coordinates the API contract, reviews diffs, integration tests and deployment troubleshooting. See `CURSOR_HANDOFF.md` for staged copyable prompts. Humans decide scope cuts and validate demo claims.

## Integration schedule (IST)

| Deadline | Deliverable / decision |
| --- | --- |
| Sep 19, 7 PM | First route verified locally; record known-good revision; check AWS identity, region and one Bedrock invocation |
| Sep 19, 9 PM | Deploy the Coding slice to AWS; resolve IAM/CORS/build problems while scope is small |
| Sep 20, 12 PM | Merge Document and Search independently with evidence tests; no combined all-at-once merge |
| Sep 20, 2 PM | Merge bounded Research; freeze API contract and dependencies |
| Sep 20, 4 PM | Feature freeze. Deploy final candidate; remove or explicitly label unfinished capabilities |
| Sep 20, 6 PM | Deployment hard stop. Verify three demo scenarios, access token, citations and failure states from a second browser |
| Sep 20, 7 PM | Record backup demo, save screenshots and prepare a short architecture explanation |
| Sep 20, 8 PM | Submit working URL, repository and recording |

If starting later, compress feature work, not the final two-hour demo buffer. If Bedrock is blocked tonight, continue the explicitly labeled fixture path for integration and prioritize account/model access before adding UI polish. A fixture-only app is not a completed AI demo.

## First-route gate

1. Install dependencies and copy environment examples locally; no credentials in Git.
2. Start API in demo mode and web frontend. Send a Coding prompt from the browser.
3. Verify the network request succeeds and the answer, provider label and returned activity render.
4. Verify explicit Document/Search/Research requests show the current unsupported status.
5. Run backend tests and frontend production build.
6. Switch backend to Bedrock using local AWS credentials; verify a real prompt, then a second materially different prompt. Do not infer readiness from health.

## Final demonstration

- Coding: ask for a small function and a correction; show relevant generated code.
- Document: upload the team's short PDF, ask a supported question, open the cited page; ask one unsupported question.
- Search / Research: ask a time-sensitive question, show retrieved source links and actual activity; explain the bounds on research.

Keep a known-good local build and recording. Present only tested functionality as complete. Track remaining tasks as `planned`, `implemented`, `verified locally`, or `verified deployed`; those are distinct states.
