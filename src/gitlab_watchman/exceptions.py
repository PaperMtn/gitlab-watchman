from typing import Dict, Any

class GitLabWatchmanError(Exception):
    """ Base class for exceptions in GitLab Watchman.
    """
    pass

class ElasticsearchMissingError(GitLabWatchmanError):
    """ Exception raised when Elasticsearch is not enabled on the instance.
    """

    def __init__(self, scope):
        self.scope = scope
        self.message = f'Elasticsearch is not configured, unable to use the search API for the scope: {self.scope}'
        super().__init__(self.message)


class MissingEnvVarError(GitLabWatchmanError):
    """ Exception raised when an environment variable is missing.
    """

    def __init__(self, env_var):
        self.env_var = env_var
        self.message = f'Missing Environment Variable: {self.env_var}'
        super().__init__(self.message)


class GitLabWatchmanAuthenticationError(GitLabWatchmanError):
    """ Exception raised when unable to authenticate to GitLab.
    """

    def __init__(self, error_message: str):
        super().__init__('Unable to authenticate to GitLab: ' + error_message)
        self.error_message = error_message


class GitLabWatchmanGetObjectError(GitLabWatchmanError):
    """ Exception raised when an error occurs while getting a GitLab API object.
    """

    def __init__(self, error_message: str, func):
        super().__init__(f'GitLab get object error: {error_message} - Function: {func.__name__}')
        self.error_message = error_message


class GitLabWatchmanNotAuthorisedError(GitLabWatchmanError):
    """ Exception raised when the authenticated user is not authorized to access the
        resource on the GitLab API.
    """

    def __init__(self, error_message: str, func):
        super().__init__(f'Not authorised: {error_message} - {func.__name__}')
        self.error_message = error_message