<img src="https://i.imgur.com/6uh3Gh4.png" width="550">

# GitLab Watchman
![Python 2.7 and 3 compatible](https://img.shields.io/pypi/pyversions/gitlab-watchman)
![PyPI version](https://img.shields.io/pypi/v/gitlab-watchman.svg)
![License: MIT](https://img.shields.io/pypi/l/gitlab-watchman.svg)

## About GitLab Watchman

GitLab Watchman is an application that uses the GitLab API to detect exposed secrets and personal data. It also enumerates the GitLab instance for any useful information.

### Features

#### Secrets Detection
It searches GitLab for internally shared projects and looks at:
- Code
- Commits
- Wiki pages
- Issues
- Merge requests
- Milestones
- Notes
- Snippets

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

##### Time based searching
You can run GitLab Watchman to look for results going back as far as:
- 24 hours
- 7 days
- 30 days
- All time

This means after one deep scan, you can schedule GitLab Watchman to run regularly and only return results from your chosen timeframe.

#### Enumeration
GitLab Watchman can enumerate potentially useful information from a GitLab instance:
- Instance metadata
- Information on the calling user/token being used
- Output all users to CSV file
- Output all projects to CSV file
- Output all groups to CSV file

### Signatures
GitLab Watchman uses custom YAML signatures to detect matches in GitLab. These signatures are pulled from the central [Watchman Signatures repository](https://github.com/PaperMtn/watchman-signatures). Slack Watchman automatically updates its signature base at runtime to ensure its using the latest signatures to detect secrets.

### Logging

GitLab Watchman gives the following logging options:
- Terminal-friendly Stdout
- JSON to Stdout

GitLab Watchman defaults to terminal-friendly stdout logging if no option is given. This is designed to be easier for humans to read.

JSON logging is also available, which is perfect for ingesting into a SIEM or other log analysis platforms.

JSON formatted logging can be easily redirected to a file as below:
```commandline
gitlab-watchman --timeframe a --all --output json >> gitlab_watchman_log.json 
```

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
GitLab Watchman will get the GitLab token and URL from the environment variables `GITLAB_WATCHMAN_TOKEN` and `GITLAB_WATCHMAN_URL`.

## Installation
You can install the latest stable version via pip:

`python3 -m pip install gitlab-watchman`

Or build from source yourself. Download the release source files, then from the top level repository run:
```shell
python3 -m build
python3 -m pip install --force-reinstall dist/*.whl
```

## Usage
GitLab Watchman will be installed as a global command, use as follows:
```
usage: gitlab-watchman [-h] --timeframe {d,w,m,a} [--output {json,stdout}] [--version] [--all] [--blobs] [--commits] [--wiki-blobs] [--issues]
                   [--merge-requests] [--milestones] [--notes] [--snippets] [--enumerate] [--debug] [--verbose]

Finding exposed secrets and personal data in GitLab

options:
  -h, --help            show this help message and exit
  --output {json,stdout}, -o {json,stdout}
                        Where to send results
  --version, -v         show program's version number and exit
  --all, -a             Find everything
  --blobs, -b           Search code blobs
  --commits, -c         Search commits
  --wiki-blobs, -w      Search wiki blobs
  --issues, -i          Search issues
  --merge-requests, -mr
                        Search merge requests
  --milestones, -m      Search milestones
  --notes, -n           Search notes
  --snippets, -s        Search snippets
  --enumerate, -e       Enumerate this GitLab instance for users, groups, projects.Output will be saved to CSV files
  --debug, -d           Turn on debug level logging
  --verbose, -V         Turn on more verbose output for JSON logging. This includes more fields, but is larger

required arguments:
  --timeframe {d,w,m,a}
                        How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time

  ```

## Other Watchman apps
You may be interested in the other apps in the Watchman family:
- [Slack Watchman](https://github.com/PaperMtn/slack-watchman)
- [Slack Watchman for Enterprise Grid](https://github.com/PaperMtn/slack-watchman-enterprise-grid)
- [GitHub Watchman](https://github.com/PaperMtn/github-watchman)

## License
The source code for this project is released under the [GNU General Public Licence](https://www.gnu.org/licenses/licenses.html#GPL). This project is not associated with GitLab.
