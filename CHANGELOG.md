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
- Added details owner of that namespace, for groups and users
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
