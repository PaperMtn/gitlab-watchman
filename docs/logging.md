# Logging
GitLab Watchman gives the following logging options:
- CSV
- Log file
- Stdout
- TCP stream

## CSV logging
CSV logging is the default logging option if no other output method is given at runtime.

Results for each search are output as CSV files in your current working directory.

## JSON formatted logging
All other logging options output their logs in JSON format. Here is an example:

```
{"localtime": "2020-01-01 00:00:00,000", "level": "NOTIFY", "source": "GitLab Watchman", "scope": "blobs", "type": "Interesting Potentially Sensitive Files", "severity": "70", "detection": {"basename": "vendor/k8s.io/kubernetes/vendor/github.com/abbot/go-http-auth/test", "blob_id": null, "data": ".........", "path": "westeros_inc/lannister_docs/my.htpasswd", "project_id": 1001, "project_name": "westeros_inc", "project_url": "https://gitlab.westeros.inc/...."}}
```
This should contain all of the information you require to ingest these logs into a SIEM, or other log analysis platform.


### File logging
File logging saves JSON formatted logs to a file.

The path where you want to output the file needs to be passed when running GitLab Watchman. This can be done via the .conf file:
```
gitlab_watchman:
  token: abc123
  url: https://gitlab.example.com
  logging:
    file_logging:
      path: /var/put_my_logs_here/
    json_tcp:
      host:
      port:
```
Or by setting your log path in the environment variable: `GITLAB_WATCHMAN_LOG_PATH`

If file logging is selected as the output option, but no path is give, GitLab Watchman defaults to the user's home directory.

The filename will be `gitlab_watchman.log`

Note: GitLab Watchman does not handle the rotation of the file. You would need a solution such as logrotate for this.

### Stdout logging
Stdout logging sends JSON formatted logs to Stdout, for you to capture however you want.

### TCP stream logging
With this option, JSON formmatted logs are sent to a destination of your choosing via TCP

You will need to pass GitLab Watchman a host and port to receive the logs, either via .conf file:

```
gitlab_watchman:
  token: abc123
  url: https://gitlab.example.com
  logging:
    file_logging:
      path:
    json_tcp:
      host: localhost
      port: 9020
```
Or by setting the environment variables `GITLAB_WATCHMAN_HOST` and `GITLAB_WATCHMAN_PORT`
