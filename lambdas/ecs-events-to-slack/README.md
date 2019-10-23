# Lambda script for ECS event notifications in Slack

This is an [AWS Lambda](https://aws.amazon.com/lambda/) script that processes
ECS events and sends them to a Slack channel via a webhook url. The webhook url
for the Slack channel can we set via a `SLACK_WEBHOOK_URL` environment
variable or managed through SecretsManager, in which case the name of the
secret is set via a `SECRETMANAGER_SECRET_NAME` environment variable.

This repo also maintains a `notify.zip` file which is an archive of the requests
pip package as required by the script and must be included in the deployment
package. Upon approval and merges to the `master` branch, CircleCI syncs the
package to a public S3 bucket to be referenced in lambda functions.
