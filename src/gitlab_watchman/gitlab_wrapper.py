import calendar
import dataclasses
import json
import os
import re
import time
import requests
import yaml
import multiprocessing
from requests.exceptions import HTTPError
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import quote

from . import logger as logger
from . import signature
from .gitlab_objects import note
from .gitlab_objects import snippet
from .gitlab_objects import project
from .gitlab_objects import blob
from .gitlab_objects import wiki_blob
from .gitlab_objects import file
from .gitlab_objects import commit
from .gitlab_objects import user
from .gitlab_objects import merge_request
from .gitlab_objects import milestone
from .gitlab_objects import issue

ALL_TIME = calendar.timegm(time.gmtime()) + 1576800000


class GitLabAPIClient(object):

    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url.rstrip('\\')
        self.per_page = 100
        self.session = session = requests.session()
        session.mount(self.base_url, HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=1)))
        session.headers.update({'Authorization': f'Bearer {self.token}'})

    def make_request(self, url, params=None, data=None, method='GET', verify_ssl=True):
        try:
            relative_url = '/'.join((self.base_url, 'api/v4', url))
            response = self.session.request(method, relative_url, params=params, data=data, verify=verify_ssl)
            response.raise_for_status()

            return response

        except HTTPError as http_error:
            if response.status_code == 400:
                if response.json().get('message').get('error'):
                    raise Exception(response.json().get('message').get('error'))
                else:
                    raise http_error
            elif response.status_code == 502 or response.status_code == 500:
                print('Retrying...')
                time.sleep(30)
                response = self.session.request(method, relative_url, params=params, data=data, verify=verify_ssl)
                response.raise_for_status()

                return response
            elif response.status_code == 429:
                print('Rate limit hit, cooling off...')
                time.sleep(30)
                response = self.session.request(method, relative_url, params=params, data=data, verify=verify_ssl)
                response.raise_for_status()

                return response
            else:
                raise http_error

        except Exception as e:
            print(e)

    def get_user_by_id(self, user_id: str) -> json:
        """ Get a GitLab user by their ID

        Args:
            user_id: ID of the user
        Returns:
            JSON object containing user data
        """
        return self.make_request(f'users/{user_id}').json()

    def get_user_by_username(self, username: str) -> json:
        """ Get a GitLab user by their username

        Args:
            username: Username of the user
        Returns:
            JSON object containing user data
        """
        return self.make_request(f'users?username={username}').json()

    def get_token_user(self) -> json:
        """ Get the details of the user who's token is being used

        Returns:
            JSON object containing user data
        """
        return self.make_request('user').json()

    def get_licence_info(self) -> json:
        """ Get information on the GitLab licence

        Returns:
            JSON object containing licence information
        """
        return self.make_request('license').json()

    def get_project(self, project_id: str) -> json:
        """ Get a GitLab project by its ID

        Args:
            project_id: ID of the project to return
        Returns:
            JSON object with project information
        """
        return self.make_request(f'projects/{project_id}').json()

    def get_variables(self, project_id: str) -> json:
        """ Get publicly available CICD variables for a project

        Args:
            project_id: ID of the project to search
        Returns:
            JSON object containing variable information
        """
        return self.make_request(f'projects/{project_id}/variables').json()

    def get_project_members(self, project_id: str) -> json:
        """ Get members of a project

        Args:
            project_id: ID of the project to retrieve
        Returns:
            JSON object containing project members
        """
        return self.make_request(f'projects/{project_id}/members').json()

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
        return self.make_request(f'projects/{project_id}/repository/files/{path}').json()

    def get_group_members(self, group_id: str) -> json:
        """ Get members of a GitLab group

        Args:
            group_id: ID of the group to get members for
        Returns:
            JSON object with group member information
        """
        return self.make_request(f'groups/{group_id}/members').json()

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
        return self.make_request(f'projects/{project_id}/repository/commits/{commit_id}').json()

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
        return self.make_request(f'projects/{project_id}/wikis/{slug}').json()

    def global_search(self,
                      search_term: str = '',
                      search_scope: str = '') -> list[json]:
        """ Wrapper for the GitLab advanced search API. Uses search term and scope to
        decide what to search for.

        Args:
            search_term: Search string to use
            search_scope: Scope of what to look for (blobs, commits etc.)
        Returns:
            List containing JSON objects with matches for the search string
        """

        results = []
        page = 1
        params = {
            'scope': search_scope,
            'search': search_term,
            'per_page': self.per_page,
            'page': ''
        }

        response = self.make_request('search', params=params)
        page_count = response.headers.get('X-Total-Pages')

        if page_count:
            while page <= int(page_count):
                params = {
                    'scope': search_scope,
                    'search': search_term,
                    'per_page': self.per_page,
                    'page': page
                }
                r = self.make_request('search', params=params).json()
                for value in r:
                    results.append(value)
                page += 1
        else:
            params = {
                'scope': search_scope,
                'search': search_term,
            }
            r = self.make_request('search', params=params).json()
            for value in r:
                results.append(value)

        return results

    def get_all_projects(self) -> list:
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

        response = self.make_request('projects', params=params)
        while 'link' in response.headers:
            next_url = response.headers.get('link')
            params = {
                'pagination': 'keyset',
                'per_page': self.per_page,
                'order_by': 'id',
                'sort': 'asc',
                'id_after': next_url.split('id_after=')[1].split('&')[0]
            }
            response = self.make_request('projects', params=params)
            for value in response.json():
                results.append(value)

        return results


def initiate_gitlab_connection() -> GitLabAPIClient:
    """ Create a GitLab API client object

    Returns:
        GitLab API client object
    """

    try:
        token = os.environ['GITLAB_WATCHMAN_TOKEN']
    except KeyError:
        with open(f'{os.path.expanduser("~")}/watchman.conf') as yaml_file:
            config = yaml.safe_load(yaml_file)

        token = config.get('gitlab_watchman').get('token')

    try:
        url = os.environ['GITLAB_WATCHMAN_URL']
    except KeyError:
        with open(f'{os.path.expanduser("~")}/watchman.conf') as yaml_file:
            config = yaml.safe_load(yaml_file)

        url = config.get('gitlab_watchman').get('url')

    return GitLabAPIClient(token, url)


def _convert_time(timestamp: str) -> int:
    """Convert ISO 8601 timestamp to epoch """

    pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
    return int(time.mktime(time.strptime(timestamp, pattern)))


def _deduplicate(input_list: list) -> list[dict]:
    """ Removes duplicates where results are returned by multiple queries
    Nested class handles JSON encoding for dataclass objects

    Args:
        input_list: List of dataclass objects
    Returns:
        List of JSON objects with duplicates removed
    """

    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

    json_set = {json.dumps(dictionary, sort_keys=True, cls=EnhancedJSONEncoder) for dictionary in input_list}

    return [json.loads(t) for t in json_set]


def _split_to_chunks(input_list, no_of_chunks):
    """Split the input list into n amount of chunks"""

    return (input_list[i::no_of_chunks] for i in range(no_of_chunks))


def find_group_owners(group_members: list) -> list:
    """ Return all users who are both active and group Owners

    Args:
        group_members: Members of a GitLab group
    Returns:
        List of owners of a group
    """

    member_list = []
    for user in group_members:
        if user.get('state') == 'active' and user.get('access_level') == 50:
            member_list.append({
                'user_id': user.get('id'),
                'name': user.get('name'),
                'username': user.get('username'),
                'access_level': 'Owner'
            })

    return member_list


def find_user_owner(user_list: list) -> list:
    """ Return user who owns a namespace

    Args:
        user_list: List of users
    Returns:
        List of formatted users owning a namespace
    """

    owner_list = []
    for user in user_list:
        owner_list.append({
            'user_id': user.get('id'),
            'name': user.get('name'),
            'username': user.get('username'),
            'state': user.get('state')
        })

    return owner_list


def search(gitlab: GitLabAPIClient,
           log_handler: logger.StdoutLogger,
           sig: signature.Signature,
           scope: str,
           timeframe: int = ALL_TIME) -> list:
    """ Uses the Search API to get search results for the given scope. These results are then split into (No of cores -
    1) number of chunks, and Multiprocessing is then used to concurrently filter them against Regex using the relevant
    worker function

    Args:
        gitlab: GitLab API object
        log_handler: Logger object for outputting results
        sig: Signature object
        scope: What sort of GitLab objects to search
        timeframe: Timeframe to search in
    Returns:
        List of JSON formatted results if any are found
    """

    results = []

    for query in sig.strings:
        regex = re.compile(sig.pattern)
        search_result_list = gitlab.global_search(query, search_scope=scope)
        query_formatted = query.replace('"', '')
        log_handler.log_info(
            f'{len(search_result_list)} {scope} found matching search term: {query_formatted}')
        result = multiprocessing.Manager().list()

        chunks = multiprocessing.cpu_count() - 1
        list_of_chunks = _split_to_chunks(search_result_list, chunks)

        processes = []

        if scope == 'blobs':
            target = _blob_worker
        elif scope == 'wiki_blobs':
            target = _wiki_blob_worker
        elif scope == 'commits':
            target = _commit_worker
        elif scope == 'issues':
            target = _issue_worker
        elif scope == 'milestones':
            target = _milestone_worker
        elif scope == 'notes':
            target = _note_worker
        elif scope == 'snippet_titles':
            target = _snippet_worker
        else:
            target = _merge_request_worker

        for search_list in list_of_chunks:
            p = multiprocessing.Process(target=target,
                                        args=(gitlab, search_list, regex, timeframe, result))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()

        results.append(list(result))

    if results:
        results = _deduplicate([item for sublist in results for item in sublist])
        log_handler.log_info(f'{len(results)} total matches found after filtering')
        return results
    else:
        log_handler.log_info('No matches found after filtering')


def _populate_project_owners(gitlab: GitLabAPIClient,
                             project_object: project.Project) -> project.Project:
    """ Populates a given project with either the user who owns it if the namespace kind == user,
    or members of the group who are owners if the namespace kind == group

    Args:
        gitlab: GitLab API object
        project_object: Project to populate the owners of
    Returns:
        Project object with owners populated
    """

    if project_object.namespace.kind == 'group':
        group_members = gitlab.get_group_members(project_object.namespace.id)
        owners = find_group_owners(group_members)
        if owners:
            owner_list = []
            for owner in owners:
                owner_list.append(user.create_from_dict(owner))
            project_object.namespace.members = owners
            project_object.namespace.owner = None
    elif project_object.namespace.kind == 'user':
        namespace_user = gitlab.get_user_by_username(project_object.namespace.full_path)
        if namespace_user:
            project_object.namespace.owner = user.create_from_dict(namespace_user[0])
            project_object.namespace.members = None

    return project_object


def _blob_worker(gitlab: GitLabAPIClient,
                 blob_list: list,
                 regex: re.Pattern,
                 timeframe: int,
                 results: list) -> list:
    """ MULTIPROCESSING WORKER - Iterates through a list of blobs to find matches against the regex

    Args:
        gitlab: GitLab API object
        blob_list: List of blobs to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for b in blob_list:
        blob_object = blob.create_from_dict(b)
        project_object = project.create_from_dict(gitlab.get_project(blob_object.project_id))
        file_object = file.create_from_dict(gitlab.get_file(blob_object.project_id, blob_object.path, blob_object.ref))
        if file_object:
            commit_object = commit.create_from_dict(
                gitlab.get_commit(blob_object.project_id, file_object.last_commit_id))
            if _convert_time(commit_object.committed_date) > (now - timeframe) and regex.search(str(blob_object.data)):
                results.append({
                    'match_string': regex.search(str(blob_object.data)).group(0),
                    'blob': blob_object,
                    'commit': commit_object,
                    'project': _populate_project_owners(gitlab, project_object),
                    # 'file': file_object
                })

    return results


def _wiki_blob_worker(gitlab: GitLabAPIClient,
                      blob_list: list,
                      regex: re.Pattern,
                      timeframe: int,
                      results: list) -> list:
    """ MULTIPROCESSING WORKER - Iterates through a list of wiki_blobs to find matches against the regex

    Args:
        gitlab: GitLab API object
        blob_list: List of wiki_blobs to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for wb in blob_list:
        wikiblob_object = wiki_blob.create_from_dict(wb)
        project_object = project.create_from_dict(gitlab.get_project(wikiblob_object.project_id))
        if _convert_time(project_object.last_activity_at) > (now - timeframe) and regex.search(
                str(wikiblob_object.data)):
            results.append({
                'match_string': regex.search(str(wikiblob_object.data)).group(0),
                'wiki_blob': wikiblob_object,
                'project': _populate_project_owners(gitlab, project_object),
            })

    return results


def _commit_worker(gitlab: GitLabAPIClient,
                   commit_list: list,
                   regex: re.Pattern,
                   timeframe: int,
                   results: list) -> list:
    """ MULTIPROCESSING WORKER - Iterates through a list of commits to find matches against the regex

    Args:
        gitlab: GitLab API object
        commit_list: List of commits to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())

    for c in commit_list:
        commit_object = commit.create_from_dict(c)
        if _convert_time(commit_object.committed_date) > (now - timeframe) and \
                regex.search(str(commit_object.message)):
            project_object = project.create_from_dict(gitlab.get_project(commit_object.project_id))
            results.append({
                'match_string': regex.search(str(commit_object.message)).group(0),
                'commit': commit_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _issue_worker(gitlab: GitLabAPIClient,
                  issue_list: list,
                  regex: re.Pattern,
                  timeframe: int,
                  results: list):
    """ MULTIPROCESSING WORKER - Iterates through a list of issues to find matches against the regex

    Args:
        gitlab: GitLab API object
        issue_list: List of issues to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for i in issue_list:
        issue_object = issue.create_from_dict(i)
        if _convert_time(issue_object.updated_at) > (now - timeframe) and \
                regex.search(str(issue_object.description)):
            project_object = project.create_from_dict(gitlab.get_project(issue_object.project_id))
            results.append({
                'match_string': regex.search(str(issue_object.description)).group(0),
                'issue': issue_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _milestone_worker(gitlab: GitLabAPIClient,
                      milestone_list: list,
                      regex: re.Pattern,
                      timeframe: int,
                      results: list):
    """ MULTIPROCESSING WORKER - Iterates through a list of milestones to find matches against the regex

    Args:
        gitlab: GitLab API object
        milestone_list: List of milestones to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for m in milestone_list:
        milestone_object = milestone.create_from_dict(m)
        if _convert_time(milestone_object.updated_at) > (now - timeframe) and \
                regex.search(str(milestone_object.description)):
            project_object = project.create_from_dict(gitlab.get_project(milestone_object.project_id))
            results.append({
                'match_string': regex.search(str(milestone_object.description)).group(0),
                'milestone': milestone_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _merge_request_worker(gitlab: GitLabAPIClient,
                          merge_request_list: list,
                          regex: re.Pattern,
                          timeframe: int,
                          results: list):
    """ MULTIPROCESSING WORKER - Iterates through a list of merge requests to find matches against the regex

    Args:
        gitlab: GitLab API object
        merge_request_list: List of merge requests to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for mr in merge_request_list:
        mr_object = merge_request.create_from_dict(mr)
        if _convert_time(mr_object.updated_at) > (now - timeframe) and \
                regex.search(str(mr_object.description)):
            project_object = project.create_from_dict(gitlab.get_project(mr_object.project_id))
            results.append({
                'match_string': regex.search(str(mr_object.description)).group(0),
                'merge_request': mr_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _note_worker(gitlab_object: GitLabAPIClient,
                 note_list: list,
                 regex: re.Pattern,
                 timeframe: int,
                 results: list):
    """ MULTIPROCESSING WORKER - Iterates through a list of notes to find matches against the regex

    Args:
        note_list: List of notes to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for n in note_list:
        note_object = note.create_from_dict(n)
        if _convert_time(note_object.created_at) > (now - timeframe) and \
                regex.search(str(note_object.body)):
            results.append({
                'note': note_object,
                'match_string': regex.search(str(note_object.body)).group(0)
            })

    return results


def _snippet_worker(gitlab_object: GitLabAPIClient,
                    snippet_list: list,
                    regex: re.Pattern,
                    timeframe: int,
                    results: list):
    """ MULTIPROCESSING WORKER - Iterates through a list of snippets to find matches against the regex

    Args:
        snippet_list: List of notes to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for s in snippet_list:
        snippet_object = snippet.create_from_dict(s)
        if _convert_time(snippet_object.created_at) > (now - timeframe) and \
                (regex.search(str(snippet_object.title)) or regex.search(str(snippet_object.description))):
            if regex.search(str(snippet_object.title)):
                match_string = regex.search(str(snippet_object.title)).group(0)
            else:
                match_string = regex.search(str(snippet_object.description)).group(0)
            results.append({
                'snippet': snippet_object,
                'match_string': match_string
            })

    return results
