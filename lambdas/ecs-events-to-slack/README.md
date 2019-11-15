# Lambda script for ECS event notifications in Slack

This is an [AWS Lambda](https://aws.amazon.com/lambda/) script that processes
ECS events and sends them to a Slack channel via a webhook url. The webhook url
for the Slack channel can be set via a `SLACK_WEBHOOK_URL` environment
variable or managed through SecretsManager, in which case the name of the
secret is set via a `SECRETMANAGER_SECRET_NAME` environment variable.

Since some environment variables contains secrets, you can create a list of
environment variables to redact from the Slack event. Set the `ENV_EXCLUDES`
to a comma separated list of environment variables to redact. Example: 
`ENV_EXCLUDES=DB_KEY,CIRCLE_KEY`

This repo also maintains a `notify.zip` file which is an archive of the requests
pip package as required by the script and must be included in the deployment
package. Upon approval and merges to the `master` branch, CircleCI syncs the
package to a public S3 bucket to be referenced in lambda functions.
