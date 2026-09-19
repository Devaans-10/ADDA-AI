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
