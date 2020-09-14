<img src="https://i.imgur.com/Hhj8CeM.png" width="550">

# GitLab Watchman

GitLab Watchman is an application that uses the GitLab API to audit GitLab for sensitive data and credentials exposed internally.

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
- Slack API tokens
- Private keys (SSH, PGP, any other misc private key)
- Exposed tokens (Bearer tokens, access tokens, client_secret etc.)
- S3 config files
- Passwords in plaintext
- CICD variables exposed publicly