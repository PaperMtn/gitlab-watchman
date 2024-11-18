## [3.1.0] - 2024-11-18
### Added
- Signatures now loaded into memory instead of being saved to disk. This allows for running on read-only filesystems.
- Ability to disable signatures by their ID in the watchman.conf config file.
  - These signatures will not be used when running Slack Watchman
  - Signature IDs for each signature can be found in the Watchman Signatures repository
- Tests for Docker build
- Enhanced deduplication of findings
  - The same match should not be returned multiple times within the same scope. E.g. if a token is found in a commit, it should not be returned multiple times in the same commit.
- All dates are now converted and logged in UTC
- Unit tests added for models and utils

### Changed
- Package management and deployment moved to Poetry
- Docker build process improved using multi-stage builds. The Dockerfile now doesn't contain any unnecessary files, and is much smaller.
- Refactor to separate GitLab client and Watchman processing into modules
- Refactor to implement [python-gitlab](https://python-gitlab.readthedocs.io/) library for GitLab API calls, instead of the custom client used previously.
  - This change gives more efficient and easier to read code, is more reliable, and also allows for enhancements to be added more easily in the future.

### Fixed
- Error when searching wiki-blobs
  - There would often be failures when trying to find projects or groups associated with blobs. This is now fixed by adding logic to check if the blob is associated with a project or group, and get the correct information accordingly.
- URL encoding for wiki-blobs where the URL contains special characters
- Error when enumerating pages when there is no `X-Total-Pages` header

## [3.0.0] - 2023-05-15
This major version release brings multiple updates to GitLab Watchman in usability, functionality and behind the scenes improvements.
### Added
- Support for centralised signatures from the [Watchman Signatures repository](https://github.com/PaperMtn/watchman-signatures)
  - This makes it much easier to keep the signature base for all Watchman applications up to date, and to add functionality to GitLab Watchman with new signatures. New signatures are downloaded, and updates to existing signatures are applied, at runtime, meaning GitLab Watchman will always be using the most up to date signatures.
- Major UI overhaul
  - A lot of feedback said GitLab Watchman was hard to read. This version introduces new terminal optimised logging as a logging option, as well as JSON formatting. This formatting is now the default when running with no output option selected, and is a lot easier for humans to read. Also, colours!
- Enumeration options added
  - GitLab Watchman now gathers more information from an instance. Useful if your use case is more red than blue...
    - Instance metadata output to terminal 
    - Information on the user you are authenticated as, and the token you are using, including what permissions it has.
    - All instance users output to CSV
    - All instance projects output to CSV
    - All instance groups output to CSV
- Option choose between verbose or succinct logging when using JSON output. Default is succinct.
- Debug logging option
### Removed
- Local/custom signatures - Centralised signatures mean that user-created custom signatures can't be used with GitLab Watchman for Enterprise Grid anymore. If you have made a signature you think would be good for sharing with the community, feel free to add it to the Watchman Signatures repository, so it can be used in all Watchman applications

## [2.0.0] - 2022-03-22
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

- Logging to file and TCP stream - logs to stdout like a true 12 factor app. Reroute stdout as you see fit. --output 
- .conf file for configuration options. Pass the environment variables `GITLAB_WATCHMAN_TOKEN` and `GITLAB_WATCHMAN_URL`

**Breaking changes:**
- The --output flag is no longer required, and therefore not supported


## [1.4.0] - 2020-12-24
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


## [1.3.0] - 2020-12-12
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

## [1.2.0] - 2020-11-16
### Added:
- More data on namespaces added to logs
- Better search queries for existing rules to filter out false positives

### Removed:
- CICD variable search no longer works due to GitLab API now only allowing owners of a project to search it for variables. It has been removed.

### Fixed:
- Bug on outputting match string for blobs/wiki-blobs

## [1.1.0] - 2020-11-14
### Fixed
- Retry added for occasional Requests HTTPSConnectionPool error

### Added
- Exact regex string match added to output from message searches

## [1.0.0] - 2020-10-01
Release
