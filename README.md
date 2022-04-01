<img src="https://i.imgur.com/6uh3Gh4.png" width="550">

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

#### Time based searching
You can run GitLab Watchman to look for results going back as far as:
- 24 hours
- 7 days
- 30 days
- All time

This means after one deep scan, you can schedule GitLab Watchman to run regularly and only return results from your chosen timeframe.

### Signatures
GitLab Watchman uses custom YAML signatures to detect matches in GitLab.

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
- notes
- snippet_titles
test_cases:
  match_cases:
  - #test case that should match the regex#
  fail_cases:
  - #test case that should not match the regex#
strings:
- #search query to use in GitLab#
pattern: #Regex pattern to filter out false positives#
```
There are Python tests to ensure signatures are formatted properly and that the Regex patterns work in the `tests` dir

More information about signatures, and how you can add your own, is in the file `docs/signatures.md`.

### Logging

Results are output to stdout in JSON format, perfect for ingesting into a SIEM or other log analysis platform.

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

Or build from source yourself, which is useful for if you intend to add your own signatures:

Download the release source files, then from the top level repository run:
```shell
python3 -m build
python3 -m pip install --force-reinstall dist/*.whl
```

## Docker Image

GitLab Watchman is also available from the Docker hub as a Docker image:

`docker pull papermountain/gitlab-watchman:latest`

You can then run GitLab Watchman in a container, making sure you pass the required environment variables:

```
// help
docker run --rm papermountain/gitlab-watchman -h

// scan all
docker run --rm -e GITLAB_WATCHMAN_TOKEN=abc123 -e GITLAB_WATCHMAN_URL=https://example.gitlab.com papermountain/gitlab-watchman --timeframe a --all
docker run --rm --env-file .env papermountain/gitlab-watchman --timeframe a --all
```

## Usage
GitLab Watchman will be installed as a global command, use as follows:
```
usage: gitlab-watchman [-h] --timeframe {d,w,m,a} [--version] [--all] [--blobs] [--commits] [--wiki-blobs] [--issues] [--merge-requests] [--milestones] [--notes] [--snippets]

Monitoring GitLab for sensitive data shared publicly

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --all                 Find everything
  --blobs               Search code blobs
  --commits             Search commits
  --wiki-blobs          Search wiki blobs
  --issues              Search issues
  --merge-requests      Search merge requests
  --milestones          Search milestones
  --notes               Search notes
  --snippets            Search snippets

  ```

## Other Watchman apps
You may be interested in some of the other apps in the Watchman family:
- [Slack Watchman](https://github.com/PaperMtn/slack-watchman)
- [Slack Watchman for Enterprise Grid](https://github.com/PaperMtn/slack-watchman-enterprise-grid)
- [GitHub Watchman](https://github.com/PaperMtn/github-watchman)
- [Trello Watchman](https://github.com/PaperMtn/trello-watchman)

## License
The source code for this project is released under the [GNU General Public Licence](https://www.gnu.org/licenses/licenses.html#GPL). This project is not associated with GitLab.
