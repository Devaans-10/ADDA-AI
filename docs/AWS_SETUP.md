# Connect the local Coding agent to AWS

Keep `NEXUS_PROVIDER=demo` until the live check succeeds. No credentials belong in
chat, source control, or frontend variables.

## Sign in locally

Install AWS CLI v2.32+ using the official AWS installer or the Amazon.AWSCLI winget
package. Open a new terminal after installation. For a personal console account:

```powershell
aws login --profile nexusai
```

Choose the same region shown in your AWS console. Complete sign-in yourself in the
browser. This creates a local profile and temporary credentials outside this repo.
IAM users/roles may require the `SignInLocalDevelopmentAccess` policy from the account
administrator; the project does not modify IAM or upgrade the account automatically.
For IAM Identity Center use `aws configure sso --profile nexusai` followed by
`aws sso login --profile nexusai` instead. For a workshop lab, use its supplied
temporary-credential procedure, including the session token, on your own machine.

[AWS browser-based login documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html)

## Verify without invoking a model

From `services/api`:

```powershell
..\..\.venv\Scripts\python.exe -m app.check_bedrock --profile nexusai --region ap-south-1
```

`ap-south-1` is Mumbai; use `ap-south-2` for Hyderabad if that is your chosen region.
The diagnostic checks AWS identity without printing credentials or account IDs.
It reports missing model configuration until you choose a model. Merely configuring
a model ID does not prove invocation access. A check can exit successfully while live
inference is marked untested; only the report's `ready: true` means both requests succeeded.

## Choose and test a model

In Amazon Bedrock choose a text model or inference profile available in your region
and account. Copy its exact ID into `services/api/.env` as `BEDROCK_MODEL_ID`, and
set `AWS_REGION` to the chosen region. Do not assume every model supports every region.

Then run the same check with `--invoke`. This makes two small model requests, returns
the actual answers for review, and reports whether they succeeded. Model use is metered;
free-tier credits and model eligibility depend on the account. No account upgrade is
part of this setup. Review whether credits cover the selected model before invoking it.

```powershell
..\..\.venv\Scripts\python.exe -m app.check_bedrock --profile nexusai --invoke
```

On success, set `NEXUS_PROVIDER=bedrock` in the backend `.env`. From repository root:

```powershell
$env:AWS_PROFILE='nexusai'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000
```

Stop the old API process before starting the new one. Refresh the workspace and run
two distinct Coding tasks. Keep the same profile in the API terminal as in the check.

[Bedrock API prerequisites](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api-ex-python.html)
and [AWS account plan details](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html).
