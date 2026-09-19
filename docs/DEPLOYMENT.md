# AWS deployment path

Status: deployment preparation, not a deployed system. The user's AWS account is ready; Bedrock model access still needs checking. Treat `infra/template.yaml` as unvalidated until SAM validation/build and a deployed smoke test succeed. Consult the template and README for exact commands and parameter names.

## 1. Prove Bedrock access locally

1. Use an AWS CLI profile or SSO session; confirm the intended account with `aws sts get-caller-identity`.
2. Choose one AWS region and a Converse-compatible model or inference profile available there. Set `AWS_REGION` and `BEDROCK_MODEL_ID` in backend configuration. Do not assume a model identifier from another account/region works.
3. Verify model prerequisites and invoke a small prompt. Bedrock can initiate third-party model subscription on first invocation; Anthropic may require first-time use-case details. AWS account access alone does not prove permission to invoke the selected model. [Bedrock model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
4. Set `NEXUS_PROVIDER=bedrock`, run the local API, and confirm the UI returns a real Coding response. Keep the fixture mode available for transport troubleshooting.

Never put AWS keys, a Bedrock credential or a search key in `NEXT_PUBLIC_*` variables. Lambda should use its execution role. Scope model invocation permissions to the chosen model/profile and any required destination model resources.

## 2. Deploy the API slice

The intended template creates an API Gateway HTTP API and Python 3.13 Lambda, using Mangum to adapt FastAPI. Validate the template, build with a Lambda-compatible environment, and deploy with AWS SAM. Review created resources and permissions before executing the deployment. A successful template parse does not verify dependency compatibility or IAM.

Install AWS CLI, AWS SAM CLI and Docker first; they were not available on the originating workstation. From repository root, with Docker running:

```powershell
sam validate --lint --template-file infra/template.yaml
sam build --use-container --template-file infra/template.yaml
sam deploy --guided --template-file .aws-sam/build/template.yaml
```

In the guided prompts choose the intended account/region, a stack name such as `nexusai-demo`, exact frontend origin, provider, tested model ID, and a randomly generated demo token of at least 24 characters. Initially use `http://localhost:3000` as the origin if Amplify has not assigned its domain; update it before testing the hosted frontend. Do not commit generated `samconfig.toml` if it contains parameter values. Save the `ApiUrl` output as `NEXT_PUBLIC_API_BASE_URL` in Amplify. An account with insufficient unreserved Lambda concurrency may need a revised concurrency setting before this template can deploy.

Backend configuration:

| Variable | Purpose |
| --- | --- |
| `NEXUS_PROVIDER` | `demo` or `bedrock`; real demo needs verified Bedrock |
| `AWS_REGION` | Chosen region; Lambda provides its runtime region |
| `BEDROCK_MODEL_ID` | Tested chat model or inference profile identifier |
| `ALLOWED_ORIGINS` | Comma-separated exact frontend origins |
| `DEMO_ACCESS_TOKEN` | Optional locally; require a nonempty value for the cloud demo |

Use the frontend's runtime token input; do not bake the access token into static assets. The shared demo token is a temporary access gate, not per-user document isolation. Keep future document sessions separate and server-validated.

The initial Lambda budget is 28 seconds with a 20-second Bedrock SDK read timeout. Keep retries bounded and measure full request time, including cold starts. API Gateway HTTP APIs permit at most 30 seconds per integration. [AWS HTTP API quotas](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-quotas.html)

## 3. Deploy the frontend

Connect the repository to Amplify Hosting and build the `apps/web` package using the supplied build configuration. Set the public API base URL before building. With Next.js `output: 'export'`, publish the generated `out` assets rather than assuming server-side Next.js routes exist. Browser requests go directly to the API. [AWS Next.js deployment guidance](https://docs.aws.amazon.com/amplify/latest/userguide/deploy-nextjs-app.html)

After Amplify assigns the final HTTPS origin, update API CORS configuration to that exact origin and redeploy the API. Rebuild frontend if the API URL changes. Verify preflight and authenticated POST behavior from the deployed page.

## 4. Cloud smoke test

- Health returns a configured mode; this is only a process/configuration check.
- Missing/wrong demo token fails, and the correct token completes a Coding request.
- Two different Coding prompts produce relevant Bedrock output.
- UI displays provider, actual activity, useful network/model errors and current unsupported-agent states.
- Browser assets contain no AWS credentials or provider keys.
- Logs identify failures without recording tokens or full private document contents.
- Note deployed URLs, region, revision and verification time in the demo notes.

No deployed URL should be advertised until this gate passes. Add conservative account budget alerts and API throttling before sharing a broadly accessible demo.

## Later RAG and Research deployment

The initial template reserves a private S3 bucket but the current API does not use it. Add scoped object permissions and upload CORS when the upload path is implemented. The bucket is retained on stack deletion; track it for later cleanup. Use signed uploads so PDF bodies do not traverse API Gateway/Lambda request payload limits. Add backend-only Qdrant and Tavily configuration when those integrations exist. Choose an embedding model separately and verify its dimension against the vector collection.

If ingestion or Research exceeds the HTTP deadline, return a job identifier promptly and store durable job status while a worker runs; the browser polls for completion. This is a measured scope decision, not part of the initial scaffold. Never claim a longer Lambda timeout bypasses the HTTP API deadline.

Keep the known-good Coding deployment available while adding specialists. If cloud provisioning is blocked near the deadline, demonstrate the verified local build and recording honestly, with cloud deployment marked pending.
