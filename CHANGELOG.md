## 2.0.0 - 2022-04-01
### Added:
- New scopes for finding exposed data in:
  - notes
  - snippets
- Docker image now available from the Docker hub, or by building from source. (Credit [@adioss](https://github.com/adioss) for the inspiration)
- Complete rewrite of the codebase to make searching faster and more efficient.
  - More modern packaging and distribution.
- Logs now include more data
- Additional signatures added to find more leaked data
- Updated logo to play nicely with dark mode displays

### Removed:
**Breaking changes:**
- Logging to file and TCP stream - logs to stdout like a true 12 factor app. Reroute stdout as you see fit. --output 
- .conf file for configuration options. Pass the environment variables `GITLAB_WATCHMAN_TOKEN` and `GITLAB_WATCHMAN_URL`


## 1.4.0 - 2020-12-24
### Added:
- Refactor of rules into directories for easier management
- Multiprocessing implemented for searching for matches. GitLab Watchman now splits regex filtering between the cores available on the device, meaning the more cores you have, the faster searching should run.
- Handling for GitLab API rate limiting, backing off when the rate limit is hit. The rate limit may be more likely to come into effect with multiprocessing
- Rules added to search for:
  - Cloudflare tokens
  - Facebook API tokens
  - GitHub API tokens
  - Mailchimp API tokens
  - Mailgun API tokens
  - Shodan API tokens
  - Stripe API tokens
  - Twilio API tokens
  - Microsoft NuGet keys


## 1.3.0 - 2020-12-12
### Added:
- Add more information about the namespaces a project is in to logs
- Added owner details of that namespace, for groups and users
- Time based searching now looks at the time a file was committed, not when a project was active, which greatly reduces multiples of the same detection because a project is active but a file has not been modified.
- Rules added:
    - SSH private keys
    - Mastercard datacash tokens
    - Heroku tokens
    - PagerDuty tokens

### Removed:
- Enhanced logging that includes nested information, such as namespace owners, means that CSV logging is no longer practical. CSV logging has been removed and JSON via STDOUT is now the default option.

## 1.2.0 - 2020-11-16
### Added:
- More data on namespaces added to logs
- Better search queries for existing rules to filter out false positives

### Removed:
- CICD variable search no longer works due to GitLab API now only allowing owners of a project to search it for variables. It has been removed.

### Fixed:
- Bug on outputting match string for blobs/wiki-blobs

## 1.1.0 - 2020-11-14
### Fixed
- Retry added for occasional Requests HTTPSConnectionPool error

### Added
- Exact regex string match added to output from message searches

## 1.0.0 - 2020-10-01
Release
