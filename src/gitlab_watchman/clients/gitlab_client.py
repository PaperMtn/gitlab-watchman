import calendar
import time
from typing import List, Dict, Any

import requests
from gitlab import Gitlab
from gitlab.const import SearchScope
from gitlab.v4.objects import User
from gitlab.exceptions import (
    GitlabLicenseError,
    GitlabAuthenticationError,
    GitlabGetError,
    GitlabListError
)
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from gitlab_watchman.loggers import StdoutLogger, JSONLogger
from gitlab_watchman.exceptions import (
    GitLabWatchmanAuthenticationError,
    GitLabWatchmanGetObjectError,
    GitLabWatchmanNotAuthorisedError
)

ALL_TIME = calendar.timegm(time.gmtime()) + 1576800000


def exception_handler(func):
    """ Decorator to handle exceptions raised by the GitLab API """
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GitlabAuthenticationError as e:
            raise GitLabWatchmanAuthenticationError(e.error_message) from e
        except (GitlabGetError, GitlabListError, GitlabLicenseError) as e:
            if e.response_code == 403:
                raise GitLabWatchmanNotAuthorisedError(e.error_message, func) from e
            else:
                raise GitLabWatchmanGetObjectError(e.error_message, func) from e
        except IndexError as e:
            raise GitLabWatchmanGetObjectError('Object not found', func) from e
        except Exception as e:
            raise e
    return inner_function


class GitLabAPIClient:

    @exception_handler
    def __init__(self,
                 token: str,
                 base_url: str,
                 logger: StdoutLogger | JSONLogger):
        self.token = token
        self.base_url = base_url.rstrip('\\')
        self.logger = logger
        self.session = session = requests.session()
        session.mount(self.base_url,
                      HTTPAdapter(
                          max_retries=Retry(
                              total=5,
                              backoff_factor=0.3,
                              status_forcelist=[500, 502, 503, 504])))
        session.headers.update({'Authorization': f'Bearer {self.token}'})
        self.gitlab_client = Gitlab(
            url=self.base_url,
            private_token=self.token,
            session=self.session,
            per_page=100,
            retry_transient_errors=True)
        self.gitlab_client.auth()

        if isinstance(logger, JSONLogger):
            self.logger = None
        else:
            self.logger = logger



    @exception_handler
    def get_user_info(self) -> Dict[str, Any]:
        """ Get information on the authenticated user

        Returns:
            User object with user information
        """
        return self.gitlab_client.user.asdict()

    @exception_handler
    def get_all_users(self) -> List[User]:
        """ Get all users in the GitLab instance

        Returns:
            User object with user information
        """
        return self.gitlab_client.users.list(get_all=True, active=True, without_project_bots=True)

    @exception_handler
    def get_user_by_username(self, username: str) -> Dict[str, Any] | None:
        """ Get a GitLab user by their username

        Args:
            username: Username of the user
        Returns:
            User object containing user data
        """
        return self.gitlab_client.users.list(username=username)[0].asdict()

    @exception_handler
    def get_settings(self) -> Dict[str, Any]:
        """ Get the settings for the GitLab instance

        Returns:
            JSON object with settings
        """
        return self.gitlab_client.settings.get().asdict()

    @exception_handler
    def get_licence(self) -> Dict[str, Any]:
        """ Get the licence for the GitLab instance

        Returns:
            JSON object with metadata
        """
        return self.gitlab_client.get_license()

    @exception_handler
    def get_metadata(self) -> Dict[str, Any]:
        """ Get GitLab project metadata

        Returns:
            JSON object with GitLab instance information
        """
        return self.session.get(f'{self.base_url}/api/v4/metadata').json()

    @exception_handler
    def get_instance_level_variables(self) -> List[Any]:
        """ Get any instance-level CICD variables

        Returns:
            JSON object with variable information
        """

        return self.gitlab_client.variables.list(as_list=True)

    @exception_handler
    def get_authed_access_token_value(self) -> Dict:
        """ Get the value of a personal access token

        Returns:
            JSON object with token information
        """
        return self.session.get(f'{self.base_url}/api/v4/personal_access_tokens/self').json()

    @exception_handler
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """ Get a GitLab project by its ID

        Args:
            project_id: ID of the project to return
        Returns:
            JSON object with project information
        """
        return self.gitlab_client.projects.get(project_id).asdict()

    @exception_handler
    def get_all_projects(self) -> List[Dict]:
        """ Get all GitLab projects.

        Returns:
            List of all projects
        """
        projects = self.gitlab_client.projects.list(all=True, as_list=True)
        return [project.asdict() for project in projects]

    @exception_handler
    def get_project_members(self, project_id: str) -> List[Dict[str, Any]]:
        """ Get members of a project

        Args:
            project_id: ID of the project to retrieve
        Returns:
            RESTObject object containing project members
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        members = self.gitlab_client.projects.get(project_id).members.list(as_list=True)
        return [member.asdict() for member in members]

    @exception_handler
    def get_file(self,
                 project_id: str,
                 path: str,
                 ref: str) -> Dict[str, Any]:
        """ Get a file stored in a project

        Args:
            project_id: ID of the project to retrieve
            path: URL encoded full path to file
            ref: The name of branch, tag or commit
        Returns:
            JSON object with the file information
        """
        return self.gitlab_client.projects.get(project_id).files.get(
            file_path=path, ref=ref).asdict()

    @exception_handler
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """ Get a GitLab group by its ID

        Args:
            group_id: ID of the group to return
        Returns:
            Dict with group information
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        return self.gitlab_client.groups.get(group_id).asdict()

    @exception_handler
    def get_all_groups(self) -> List[Dict]:
        """ Get all groups visible to the authenticated user

        Returns:
            Dict with group information
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        groups = self.gitlab_client.groups.list(as_list=True)
        return [group.asdict() for group in groups]

    @exception_handler
    def get_group_members(self, group_id: str) -> List[Dict]:
        """ Get members of a GitLab group

        Args:
            group_id: ID of the group to get members for
        Returns:
            Dict object with group member information
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        members = self.gitlab_client.groups.get(group_id).members.list(as_list=True)
        return [member.asdict() for member in members]

    @exception_handler
    def get_commit(self,
                   project_id: str,
                   commit_id: str) -> Dict[str, Any]:
        """ Get commit information

        Args:
            project_id: ID for the project the commit exists in
            commit_id: ID of the commit
        Returns:
            Dict object containing commit data
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        return self.gitlab_client.projects.get(project_id).commits.get(commit_id).asdict()

    @exception_handler
    def get_wiki_page(self,
                      project_id: str,
                      slug: str) -> Dict[str, Any]:
        """ Get a wiki page from a project

        Args:
            project_id: ID of the project the wiki page is in
            slug: URL slug for the wiki page
        Returns:
            JSON object containing wiki data
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        return self.gitlab_client.projects.get(project_id).wikis.get(slug).asdict()

    @exception_handler
    def global_search(self,
                      search_term: str = '',
                      search_scope: str = '') -> List[Dict[str, Any]]:
        """ Search using the GitLab advanced search API. Uses search term and scope to
        decide what to search for.

        Args:
            search_term: Search string to use
            search_scope: Scope of what to look for. One of:
                - blobs
                - commits
                - issues
                - merge_requests
                - wiki_blobs
                - milestones
                - notes
                - snippet_titles
        Returns:
            List containing Dict objects with matches for the search string
        Raises:
            GitLabWatchmanNotAuthorisedError: If the user is not authorized to access the resource
            GitLabWatchmanGetObjectError: If an error occurs while getting the object
        """
        scope_map = {
            'blobs': SearchScope.BLOBS,
            'commits': SearchScope.COMMITS,
            'issues': SearchScope.ISSUES,
            'merge_requests': SearchScope.MERGE_REQUESTS,
            'wiki_blobs': SearchScope.WIKI_BLOBS,
            'milestones': SearchScope.MILESTONES,
            'notes': SearchScope.PROJECT_NOTES,
            'snippet_titles': SearchScope.GLOBAL_SNIPPET_TITLES,
        }

        return self.gitlab_client.search(
            search=search_term,
            scope=scope_map.get(search_scope, SearchScope.BLOBS),
            all=True,
            as_list=True,
            per_page=100)
