import calendar
import json
import time
import requests
from requests.exceptions import HTTPError
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import quote
from typing import List, Dict

from gitlab_watchman import exceptions
from gitlab_watchman.loggers import StdoutLogger, JSONLogger


ALL_TIME = calendar.timegm(time.gmtime()) + 1576800000


class GitLabAPIClient(object):

    def __init__(self,
                 token: str,
                 base_url: str,
                 logger: StdoutLogger | JSONLogger):
        self.token = token
        self.base_url = base_url.rstrip('\\')
        self.per_page = 100
        self.session = session = requests.session()
        session.mount(self.base_url,
                      HTTPAdapter(
                          max_retries=Retry(
                              total=5,
                              backoff_factor=0.3,
                              status_forcelist=[500, 502, 503, 504])))
        session.headers.update({'Authorization': f'Bearer {self.token}'})

        if isinstance(logger, JSONLogger):
            self.logger = None
        else:
            self.logger = logger

    def _make_request(self,
                      url: str,
                      params=None,
                      data=None,
                      method='GET',
                      verify_ssl=True):
        try:
            relative_url = '/'.join((self.base_url, 'api/v4', url))
            response = self.session.request(method, relative_url, params=params, data=data, verify=verify_ssl)
            response.raise_for_status()

            return response

        except HTTPError as http_error:
            if response.status_code == 400:
                if response.json().get('message').get('error') == 'Scope not supported without Elasticsearch!':
                    raise exceptions.ElasticsearchMissingError(params.get('scope'))
                else:
                    raise http_error
            elif response.status_code == 429:
                if self.logger:
                    self.logger.log(
                        mes_type='WARNING',
                        message='Rate limit hit, cooling off for 90 seconds...')
                else:
                    print('Rate limit hit, cooling off for 90 seconds...')

                time.sleep(90)
                response = self.session.request(method, relative_url, params=params, data=data, verify=verify_ssl)
                response.raise_for_status()

                return response
            else:
                raise
        except:
            raise

    def _get_pages(self, url, params):
        first_page = self._make_request(url, params)
        yield first_page.json()
        num_pages = int(first_page.headers.get('X-Total-Pages'))

        for page in range(2, num_pages + 1):
            params['page'] = str(page)
            next_page = self._make_request(url, params=params).json()
            yield next_page

    def page_api_search(self,
                        url: str,
                        search_scope: str = None,
                        search_term: str = None) -> List[Dict]:
        """ Wrapper for GitLab API methods that use page number based pagination
        Args:
            search_scope:
            search_term:
            url: API endpoint to use
        Returns:
            A list of dict objects with responses
        """

        results = []
        params = {
            'per_page': self.per_page,
            'page': '',
            'scope': search_scope,
            'search': search_term,
        }

        for page in self._get_pages(url, params):
            results.append(page)

        return [item for sublist in results for item in sublist]

    def get_user_by_id(self, user_id: str) -> json:
        """ Get a GitLab user by their ID

        Args:
            user_id: ID of the user
        Returns:
            JSON object containing user data
        """
        return self._make_request(f'users/{user_id}').json()

    def get_user_by_username(self, username: str) -> json:
        """ Get a GitLab user by their username

        Args:
            username: Username of the user
        Returns:
            JSON object containing user data
        """
        return self._make_request(f'users?username={username}').json()

    def get_token_user(self) -> json:
        """ Get the details of the user who's token is being used

        Returns:
            JSON object containing user data
        """
        return self._make_request('user').json()

    def get_licence_info(self) -> json:
        """ Get information on the GitLab licence

        Returns:
            JSON object containing licence information
        """
        return self._make_request('license').json()

    def get_metadata(self) -> Dict:
        """ Get GitLab project metadata

        Returns:
            JSON object with GitLab instance information
        """
        return self._make_request(f'metadata').json()

    def get_user_info(self) -> Dict:
        """ Get information on the authenticated user

        Returns:
            JSON object with user information
        """
        return self._make_request(f'user').json()

    def get_instance_level_variables(self) -> Dict:
        """ Get any instance-level CICD variables

        Returns:
            JSON object with variable information
        """
        return self._make_request(f'admin/ci/variables').json()

    def get_personal_access_tokens(self) -> Dict:
        """ Get personal access tokens available to this user

        Returns:
            JSON object with token information
        """
        return self._make_request(f'personal_access_tokens').json()

    def get_personal_access_token_value(self, token_id: str) -> Dict:
        """ Get the value of a personal access token

        Returns:
            JSON object with token information
        """
        return self._make_request(f'personal_access_tokens/{token_id}').json()

    def get_authed_access_token_value(self) -> Dict:
        """ Get the value of a personal access token

        Returns:
            JSON object with token information
        """
        return self._make_request(f'personal_access_tokens/self').json()

    def get_all_users(self) -> List[Dict]:
        """ Get all users in the GitLab instance

        Returns:
            JSON object with user information
        """
        return self.page_api_search('users?active=true&without_project_bots=true')

    def get_project(self, project_id: str) -> json:
        """ Get a GitLab project by its ID

        Args:
            project_id: ID of the project to return
        Returns:
            JSON object with project information
        """
        return self._make_request(f'projects/{project_id}').json()

    def get_variables(self, project_id: str) -> json:
        """ Get publicly available CICD variables for a project

        Args:
            project_id: ID of the project to search
        Returns:
            JSON object containing variable information
        """
        return self._make_request(f'projects/{project_id}/variables').json()

    def get_project_members(self, project_id: str) -> json:
        """ Get members of a project

        Args:
            project_id: ID of the project to retrieve
        Returns:
            JSON object containing project members
        """
        return self._make_request(f'projects/{project_id}/members').json()

    def get_file(self,
                 project_id: str,
                 path: str,
                 ref: str) -> json:
        """ Get a file stored in a project

        Args:
            project_id: ID of the project to retrieve
            path: URL encoded full path to file
            ref: The name of branch, tag or commit
        Returns:
            JSON object with file information
        """
        path = ''.join((quote(path, safe=''), '?ref=', ref))
        return self._make_request(f'projects/{project_id}/repository/files/{path}').json()

    def get_group_members(self, group_id: str) -> json:
        """ Get members of a GitLab group

        Args:
            group_id: ID of the group to get members for
        Returns:
            JSON object with group member information
        """
        return self._make_request(f'groups/{group_id}/members').json()

    def get_commit(self,
                   project_id: str,
                   commit_id: str) -> json:
        """ Get commit information

        Args:
            project_id: ID for the project the commit exists in
            commit_id: ID of the commit
        Returns:
            JSON object containing commit data
        """
        return self._make_request(f'projects/{project_id}/repository/commits/{commit_id}').json()

    def get_wiki_page(self,
                      project_id: str,
                      slug: str) -> json:
        """

        Args:
            project_id: ID of the project the wiki page is in
            slug: URL slug for the wiki page
        Returns:
            JSON object containing wiki data

        """
        return self._make_request(f'projects/{project_id}/wikis/{slug}').json()

    def global_search(self,
                      search_term: str = '',
                      search_scope: str = '') -> List[Dict]:
        """ Wrapper for the GitLab advanced search API. Uses search term and scope to
        decide what to search for.

        Args:
            search_term: Search string to use
            search_scope: Scope of what to look for (blobs, commits etc.)
        Returns:
            List containing JSON objects with matches for the search string
        """
        return self.page_api_search('search', search_scope=search_scope, search_term=search_term)

    def get_all_projects(self) -> List[Dict]:
        """ Get all public projects. Uses keyset pagination, which currently
         is only available for the Projects resource in the GitLab API

        Returns:
            List of all projects
        """

        results = []

        params = {
            'pagination': 'keyset',
            'per_page': self.per_page,
            'order_by': 'id',
            'sort': 'asc'
        }

        response = self._make_request('projects', params=params)
        while 'link' in response.headers:
            next_url = response.headers.get('link')
            params = {
                'pagination': 'keyset',
                'per_page': self.per_page,
                'order_by': 'id',
                'sort': 'asc',
                'id_after': next_url.split('id_after=')[1].split('&')[0]
            }
            response = self._make_request('projects', params=params)
            for value in response.json():
                results.append(value)

        return results

    def get_all_groups(self) -> List[Dict]:
        """ Get all groups in the GitLab instance

        Returns:
            JSON object with group information
        """
        return self.page_api_search('groups?all_available=true')
