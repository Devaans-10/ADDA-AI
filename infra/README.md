# Cloud configuration status

`template.yaml` is the first API deployment path, not evidence of an AWS deployment.
It runs FastAPI through Mangum on Lambda, with an HTTP API and a private encrypted
S3 bucket reserved for future uploads. The current API does not use the bucket.

Before deploying, validate with AWS SAM, configure an accessible Bedrock model,
and follow `../docs/DEPLOYMENT.md`. The shared demo token protects model calls;
it is a limited hackathon gate, not per-user authentication. Restrict allowed origins
and keep the token out of frontend build variables and source control. API Gateway
throttles and reserved Lambda concurrency limit simultaneous requests, not total spend.

The IAM model resources permit foundation models and inference profiles to support
initial model selection and cross-region profiles. Narrow them to the chosen model
and profile ARNs once the access check succeeds. No S3 access is granted to the API yet.
The bucket is retained when the stack is deleted and must be cleaned up separately.

The web build is static (`apps/web/out`); there is no Next.js server proxy. Configure
`NEXT_PUBLIC_API_BASE_URL` at Amplify build time, then rebuild when its value changes.
The API handles CORS, including preflight requests. Research jobs must move to an
asynchronous contract if they cannot reliably finish within the HTTP API time budget.
