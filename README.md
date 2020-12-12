<img src="https://i.imgur.com/Hhj8CeM.png" width="550">

# GitLab Watchman
![Python 2.7 and 3 compatible](https://img.shields.io/pypi/pyversions/gitlab-watchman)
![PyPI version](https://img.shields.io/pypi/v/gitlab-watchman.svg)
![License: MIT](https://img.shields.io/pypi/l/gitlab-watchman.svg)

## About GitLab Watchman

GitLab Watchman is an application that uses the GitLab API to audit GitLab for sensitive data and credentials exposed internally.

### Features
It searches GitLab for internally shared projects and looks at:
- Code
- Commits
- Wiki pages
- Issues
- Merge requests
- Milestones

For the following data:
- GCP keys and service account files
- AWS keys
- Azure keys and service account files
- Google API keys
- Slack API tokens & webhooks
- Private keys (SSH, PGP, any other misc private key)
- Exposed tokens (Bearer tokens, access tokens, client_secret etc.)
- S3 config files
- Tokens for services such as Heroku, PayPal and more
- Passwords in plaintext
- and more

#### Time based searching
You can run GitLab Watchman to look for results going back as far as:
- 24 hours
- 7 days
- 30 days
- All time

This means after one deep scan, you can schedule GitLab Watchman to run regularly and only return results from your chosen timeframe.

### Rules
GitLab Watchman uses custom YAML rules to detect matches in GitLab.

They follow this format:

```yaml
---
filename:
enabled: #[true|false]
meta:
  name:
  author:
  date:
  description: #what the search should find#
  severity: #rating out of 100#
scope: #what to search, any combination of the below#
- blobs
- commits
- milestones
- wiki_blobs
- issues
- merge_requests
test_cases:
  match_cases:
  - #test case that should match the regex#
  fail_cases:
  - #test case that should not match the regex#
strings:
- #search query to use in GitLab#
pattern: #Regex pattern to filter out false positives#
```
There are Python tests to ensure rules are formatted properly and that the Regex patterns work in the `tests` dir

More information about rules, and how you can add your own, is in the file `docs/rules.md`.

### Logging

GitLab Watchman gives the following logging options:
- Log file
- Stdout
- TCP stream

Results are output in JSON format, perfect for ingesting into a SIEM or other log analysis platform.

For file and TCP stream logging, configuration options need to be passed via `.conf` file or environment variable. See the file `docs/logging.md` for instructions on how to set it up.

If no logging option is given, GitLab Watchman defaults to Stdout logging.

## Requirements

### GitLab versions
GitLab Watchman uses the v4 API, and works with GitLab Enterprise Edition versions:
- 13.0 and above - Yes

- GitLab.com - Yes
- 12.0 - 12.10 - Maybe, untested but if using v4 of the API then it could work

### GitLab Licence & Elasticsearch
To search the scopes:
- blobs
- wiki_blobs
- commits

The GitLab instance must have [Elasticsearch](https://docs.gitlab.com/ee/integration/elasticsearch.html) configured, and be running Enterprise Edition with a minimum GitLab Starter or Bronze Licence.

### GitLab personal access token
To run GitLab Watchman, you will need a GitLab personal access token.

You can create a personal access token in the GitLab GUI via Settings -> Access Tokens -> Add a personal access token

The token needs permission for the following scopes:
```
api
```

**Note**: Personal access tokens act on behalf of the user who creates them, so I would suggest you create a token using a service account, otherwise the app will have access to your private repositories.

### GitLab URL

You also need to provide the URL of your GitLab instance.

#### Providing token & URL
GitLab Watchman will first try to get the the GitLab token and URL from the environment variables `GITLAB_WATCHMAN_TOKEN` and `GITLAB_WATCHMAN_URL`, if this fails they will be taken from .conf file (see below).

### .conf file
Configuration options can be passed in a file named `watchman.conf` which must be stored in your home directory. The file should follow the YAML format, and should look like below:
```yaml
gitlab_watchman:
  token: abc123
  url: https://gitlab.example.com
  logging:
    file_logging:
      path:
    json_tcp:
      host:
      port:
```
GitLab Watchman will look for this file at runtime, and use the configuration options from here. If you are not using the advanced logging features, leave them blank.

If you are having issues with your .conf file, run it through a YAML linter.

An example file is in `docs/example.conf`

**Note** If you use any other Watchman applications and already have a `watchman.conf` file, just append the conf data for GitLab Watchman to the existing file.

## Installation
Install via pip

`pip install gitlab-watchman`

Or via source

## Usage
GitLab Watchman will be installed as a global command, use as follows:
```
usage: gitlab-watchman [-h] --timeframe {d,w,m,a} --output
                   {file,stdout,stream} [--version] [--all] [--blobs]
                   [--commits] [--wiki-blobs] [--issues] [--merge-requests]
                   [--milestones] [--comments]

Monitoring GitLab for sensitive data shared publicly

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --all                 Find everything
  --blobs               Search code blobs
  --commits             Search commits
  --wiki-blobs          Search wiki blobs
  --issues              Search issues
  --merge-requests      Search merge requests
  --milestones          Search milestones
  --comments            Search comments

required arguments:
  --timeframe {d,w,m,a}
                        How far back to search: d = 24 hours w = 7 days, m =
                        30 days, a = all time
  --output {file,stdout,stream}
                        Where to send results

  ```

You can run GitLab Watchman to look for everything, and output to default Stdout:

`gitlab-watchman --timeframe a --all`

Or arguments can be grouped together to search more granularly. This will look for commits and milestones for the last 30 days, and output the results to a TCP stream:

`gitlab-watchman --timeframe m --commits --milestones --output stream`

## Other Watchman apps
You may be interested in some of the other apps in the Watchman family:
- [Slack Watchman](https://github.com/PaperMtn/slack-watchman)
- [GitHub Watchman](https://github.com/PaperMtn/github-watchman)

## License
The source code for this project is released under the [GNU General Public Licence](https://www.gnu.org/licenses/licenses.html#GPL). This project is not associated with GitLab.
