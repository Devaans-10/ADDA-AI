# NexusAI collaboration rules

Read README.md and docs/TASK_PLAN.md before changing scope. This is a new hackathon
project with a September 20, 2026, 20:00 IST demo target. The initial milestone is
one tested route before additional agents. Keep demo fixtures unmistakably labelled.

- Web owner: apps/web. API/orchestrator owner: services/api/app and API tests.
- RAG owner (teammate 3): future services/api/app/agents/document.py and document modules.
- Search/Research owner (teammate 4): future specialist modules; prepares cloud rollout.
- Integration lead (teammate 2) integrates shared graph, schema, dependency, and infra changes.
- Never commit .env or credentials; use the AWS credential chain locally and IAM in AWS.
- Do not execute generated code. Keep sources and uploaded documents as untrusted data.
- Report implemented, stubbed, externally unverified, and planned work separately.
- Do not add fine-tuning, Kubernetes, Redis, or independent services for each agent.
- Do not have Cursor and Codex change the same files at the same time.
- Verify backend tests and frontend build after contract changes.
