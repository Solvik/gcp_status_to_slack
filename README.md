GCP Status to Slack
====

Stupid script that fetch https://status.cloud.google.com JSON feed and notify a Slack channel about certain services.


Configuration
==

```
GCP_INCIDENTS_URL = 'https://status.cloud.google.com/incidents.json'
GCP_STATUS_URL = 'https://status.cloud.google.com'

LAST_RUN_FILE = '/tmp/gcp_slack.run'

# Available services are:
# 'appengine', 'bigquery',  'cloud-dataflow',  'cloud-datastore',  'cloud-dev-tools',  'cloud-functions',  'cloud-iam',  'cloud-ml',  'cloud-networking',  'cloud-pubsub',  'cloud-spanner',  'cloud-sql',  'compute',  'container-engine',  'developers-console',  'google-stackdriver',  'storage',  'support'
GCP_SERVICES = [
    'cloud-networking',
    'compute',
    'storage',
    'container-engine',
    ]

SLACK_HOOKS_SERVICE = 'https://hooks.slack.com/services/XXXXXX/ZZZZZZZZZZZZZZZZZZZZZZ'

SLACK_CHANNELS = [
	      '#monitoring',
	      ]
SLACK_USERNAME = 'GCP Status'
```