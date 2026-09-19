# NexusAI

One workspace for specialized AI tasks. Fresh hackathon repository; target demo:
**September 20, 2026 at 20:00 IST**.

## First milestone

The implemented path is **Next.js → FastAPI → LangGraph router → Coding agent → answer + activity trace**.
The default offline provider returns an explicitly labelled fixed fixture. Bedrock
Converse is integrated, but live inference requires your account credentials and an
accessible model. A successful health check does not prove Bedrock access.

| Capability | Current state |
| --- | --- |
| Web workspace, request/error handling, response display | Implemented |
| LangGraph routing + Coding node | Implemented; deterministic keyword routing |
| Activity trace | Actual completed steps returned with the answer; no live streaming yet |
| Offline provider | Fixed connection-test fixture, not AI |
| Bedrock provider | Integrated; needs live account verification |
| PDF upload, vector retrieval, page citations | Planned; not implemented |
| Search API, Research workflow | Planned; not implemented |
| AWS hosting | SAM + Amplify configuration supplied; not deployed |

Future agents return `501 agent_not_implemented` instead of simulated answers.
Coding responses are displayed, never executed. Requests are independent; there is
no conversation memory, user account system, or persistent storage in this milestone.

## Run locally on Windows

Prerequisites: Node.js 22+ and Python 3.13+ (this workstation has Node 24 and Python 3.14).
Open this repository in Cursor. From its root, install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r services/api/requirements-dev.txt
Copy-Item services/api/.env.example services/api/.env
Copy-Item apps/web/.env.example apps/web/.env.local
Push-Location apps/web
npm.cmd ci
Pop-Location
```

Copy environment templates only for the first setup; do not overwrite configured files.
Dependencies and templates have already been installed on the originating workstation.

Terminal 1, from repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:

```powershell
cd apps/web
npm.cmd run dev
```

Open [NexusAI](http://localhost:3000) and run “Write a Python function to reverse a string.”
You should see the fixed sample, the provider label, and completed Router/Coding steps.
API reference: [local OpenAPI docs](http://localhost:8000/docs).

Alternatively, `docker compose up --build` starts both services in offline fixture
mode once Docker is installed. That path does not use your host AWS credentials.
Docker and the cloud template require separate verification; they were not run on
the originating workstation because Docker/AWS SAM were unavailable.

On macOS/Linux use `.venv/bin/python` in place of `.venv\Scripts\python.exe`,
`cp` instead of `Copy-Item`, and `npm` instead of `npm.cmd`.

## Enable Bedrock

Follow [local AWS sign-in and verification](docs/AWS_SETUP.md). The readiness checker
can validate the session without model calls, then test two prompts with `--invoke`.

Configure AWS credentials using your team's normal AWS profile/SSO flow outside the
repository. Set `NEXUS_PROVIDER=bedrock`, `AWS_REGION`, and `BEDROCK_MODEL_ID` in
`services/api/.env`; restart the API. Use a Converse-compatible model or inference
profile available to this account and region. Do not put AWS keys in the frontend.
If using a named profile, set `AWS_PROFILE` in the backend terminal before starting it.

The UI reports the configured provider. A successful chat is the live inference check.
Provider failures remain errors; there is no silent fallback to the offline fixture.
See [deployment instructions](docs/DEPLOYMENT.md) before enabling a public endpoint.

## Verify

```powershell
Push-Location services/api
..\..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
Push-Location apps/web
npm.cmd run typecheck
npm.cmd run build
Pop-Location
```

The backend tests cover the actual compiled graph, request validation, unsupported
agents, CORS, the demo access gate, and the Bedrock adapter with a mocked SDK.
They do not call paid services. `requirements.txt` pins runtime dependencies;
`requirements-dev.txt` pins the complete test environment. The `.in` files document
dependency intent, and `package-lock.json` locks the frontend.

## Repo map and team handoff

```text
apps/web/              Next.js workspace, static export for Amplify
services/api/app/     FastAPI, LangGraph, schemas, Bedrock/offline providers
services/api/tests/   API and provider contract checks
infra/template.yaml  AWS SAM: HTTP API, Lambda, private future document bucket
docs/                Architecture, four-person plan, Cursor prompts, AWS runbook
amplify.yml          Monorepo frontend build configuration
```

- [Four-person task plan and acceptance criteria](docs/TASK_PLAN.md)
- [MVP architecture and planned agent interfaces](docs/ARCHITECTURE.md)
- [Cursor/Codex handoff prompts](docs/CURSOR_HANDOFF.md)
- [AWS deployment and access checks](docs/DEPLOYMENT.md)

Keep the first route green before integrating Search, Document/RAG, then Research.
This milestone uses separate web and API runtimes; agents are modules inside the API,
not independently deployed microservices. A separate RAG service is a later option.

Implementation references: [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api),
[Bedrock Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html),
[Next.js installation](https://nextjs.org/docs/app/getting-started/installation).
