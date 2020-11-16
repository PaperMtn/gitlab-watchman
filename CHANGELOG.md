## 1.2.0 - 2020-11-16
###Added:
- More data on namespaces added to logs
- Better search queries for existing rules to filter out false positives
###Removed:
- CICD variable search no longer works due to GitLab API now only allowing owners of a project to search it for variables. It has been removed.
###Fixed:
- Bug on outputting match string for blobs/wiki-blobs

## 1.1.0 - 2020-11-14
### Fixed
- Retry added for occasional Requests HTTPSConnectionPool error
### Added
- Exact regex string match added to output from message searches

## 1.0.0 - 2020-10-01
Release
