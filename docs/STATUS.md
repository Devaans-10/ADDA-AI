# First milestone verification

Verified locally on September 19, 2026 on Windows, Node 24.18.0 and Python 3.14.

- Backend: 16 tests passed. Includes real LangGraph invocation in fixture mode,
  validation, unsupported agents, CORS, access token and mocked Bedrock success/failure/timeout.
- Python dependency consistency: passed. Runtime and test dependencies locked.
- Frontend: TypeScript check and production static export passed. npm audit reported
  no vulnerabilities at installation time.
- Browser: actual request from `http://localhost:3000` to local API succeeded, displayed
  fixture disclosure, code, request ID, and Router/Coding activity. Network failure
  and unimplemented Document routing errors were checked. Working fixture restored.
- Layout visually checked in Codex's narrow browser panel; desktop layout has not had
  a separate visual check.
- Test dependency emitted one Starlette/AnyIO deprecation warning; tests passed.

Not verified: real Bedrock inference, Docker builds, SAM validation/container build,
Python 3.13 deployment runtime, AWS deployment, and GitHub CI. No AWS profile or
credentials were available via the local SDK credential chain. No cloud resources
were created. The repository has no remote configured.

PDF/RAG, Search, Research, and live activity streaming are planned rather than implemented.
The next gate is local AWS sign-in and two successful distinct Bedrock Coding prompts.

## Bedrock setup follow-up

User selected Mumbai (`ap-south-1`); backend defaults and local configuration now use
that region. Added a safe local readiness command, specific AWS error messages, and
the CRT dependency required by the SDK's browser-login credential provider. Backend
suite now has 24 passing tests; dependency consistency check passed. Live inference
is still unverified. AWS CLI installation was started through the official winget
package and is awaiting completion of the Windows installer prompt.

## Cursor audit re-verification (19 Sep 2026, ~17:50 IST)

Independent inspection of this tree (not the disposable handoff-test repo).
HEAD `1ff16f1` on `main`, working tree clean, no git remote.

Verified now:
- `pytest -q` in `services/api`: 24 passed, 1 Starlette/AnyIO deprecation warning.
- `npm run typecheck` and `npm run build` in `apps/web`: passed (Next.js 16.3.5 static export).
- Live `GET http://127.0.0.1:8000/health`: `coding: true`, document/search/research `false`, `provider: demo`.
- Live `POST /api/chat` coding prompt: 200, fixture answer, `agent: coding`, activity Router + Coding agent.
- Live PDF/search/research keyword prompts: HTTP 501 `agent_not_implemented`.
- Browser `http://localhost:3000`: API connected, Run task shows fixture, Coding agent label, activity steps.
- AWS CLI present: `aws-cli/2.36.49`. Docker and AWS SAM CLIs are not installed.
- `apps/web/.env.local` is missing; frontend used the documented `http://localhost:8000` default.

Not verified: live Bedrock inference, Docker compose, SAM/Amplify deploy, GitHub CI.
Observed in Next.js dev: hydration error overlay (`app/page.tsx` Workspace, red "1 Issue" badge).
The chat path still completed. Production `out/` was not re-served in a browser.
