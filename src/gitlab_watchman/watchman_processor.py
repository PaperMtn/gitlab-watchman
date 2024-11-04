import calendar
import re
import time
import multiprocessing
from typing import List, Dict

from gitlab_watchman.loggers import JSONLogger, StdoutLogger
from gitlab_watchman.utils import convert_time, deduplicate_results, split_to_chunks
from gitlab_watchman.models import (
    signature,
    note,
    snippet,
    blob,
    wiki_blob,
    file,
    commit,
    user,
    merge_request,
    milestone,
    issue,
    project
)
from gitlab_watchman.clients.gitlab_client import GitLabAPIClient

ALL_TIME = calendar.timegm(time.gmtime()) + 1576800000


def initiate_gitlab_connection(token: str,
                               url: str,
                               logger: StdoutLogger | JSONLogger) -> GitLabAPIClient:
    """ Create a GitLab API client object

    Returns:
        GitLab API client object
    """

    try:
        return GitLabAPIClient(token, url, logger)
    except Exception as e:
        raise e


def find_group_owners(group_members: List[Dict]) -> List[Dict]:
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


def find_user_owner(user_list: List[Dict]) -> List[Dict]:
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
           log_handler: StdoutLogger | JSONLogger,
           sig: signature.Signature,
           scope: str,
           verbose: bool,
           timeframe: int = ALL_TIME) -> List[Dict]:
    """ Uses the Search API to get search results for the given scope. These results are then split into (No of cores -
    1) number of chunks, and Multiprocessing is then used to concurrently filter them against Regex using the relevant
    worker function

    Args:
        gitlab: GitLab API object
        log_handler: Logger object for outputting results
        sig: Signature object
        scope: What sort of GitLab objects to search
        verbose: Whether to use verbose logging or not
        timeframe: Timeframe to search in
    Returns:
        List of JSON formatted results if any are found
    """

    results = []

    for query in sig.search_strings:
        for pattern in sig.patterns:
            regex = re.compile(pattern)
            search_result_list = gitlab.global_search(query, search_scope=scope)
            query_formatted = query.replace('"', '')
            log_handler.log('INFO',
                            f'{len(search_result_list)} {scope} found matching search term: {query_formatted}')
            result = multiprocessing.Manager().list()

            chunks = multiprocessing.cpu_count() - 1
            list_of_chunks = split_to_chunks(search_result_list, chunks)

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
                                            args=(
                                                gitlab,
                                                search_list,
                                                regex,
                                                timeframe,
                                                result,
                                                verbose
                                            ))
                processes.append(p)
                p.start()

            for process in processes:
                process.join()

            results.append(list(result))

    if results:
        results = deduplicate_results([item for sublist in results for item in sublist])
        log_handler.log('INFO', f'{len(results)} total matches found after filtering')
        return results
    else:
        log_handler.log('INFO', 'No matches found after filtering')


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
                 blob_list: List[Dict],
                 regex: re.Pattern,
                 timeframe: int,
                 results: List,
                 verbose: bool,
                 **kwargs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of blobs to find matches against the regex

    Args:
        gitlab: GitLab API object
        blob_list: List of blobs to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging or not
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
                gitlab.get_commit(blob_object.project_id, file_object.commit_id))
            if convert_time(commit_object.committed_date) > (now - timeframe) and regex.search(str(blob_object.data)):
                match_string = regex.search(str(blob_object.data)).group(0)
                if not verbose:
                    setattr(blob_object, 'data', None)
                results.append({
                    'match_string': match_string,
                    'blob': blob_object,
                    'commit': commit_object,
                    'project': _populate_project_owners(gitlab, project_object),
                    'file': file_object
                })
    return results


def _wiki_blob_worker(gitlab: GitLabAPIClient,
                      blob_list: List[Dict],
                      regex: re.Pattern,
                      timeframe: int,
                      results: List,
                      verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of wiki_blobs to find matches against the regex

    Args:
        gitlab: GitLab API object
        blob_list: List of wiki_blobs to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging or not
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for wb in blob_list:
        wikiblob_object = wiki_blob.create_from_dict(wb)
        project_object = project.create_from_dict(gitlab.get_project(wikiblob_object.project_id))
        if convert_time(project_object.last_activity_at) > (now - timeframe) and regex.search(
                str(wikiblob_object.data)):
            match_string = regex.search(str(wikiblob_object.data)).group(0)
            if not verbose:
                setattr(wikiblob_object, 'data', None)
            results.append({
                'match_string': match_string,
                'wiki_blob': wikiblob_object,
                'project': _populate_project_owners(gitlab, project_object),
            })

    return results


def _commit_worker(gitlab: GitLabAPIClient,
                   commit_list: List[Dict],
                   regex: re.Pattern,
                   timeframe: int,
                   results: List,
                   verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of commits to find matches against the regex

    Args:
        gitlab: GitLab API object
        commit_list: List of commits to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose searching or not
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())

    for c in commit_list:
        commit_object = commit.create_from_dict(c)
        if convert_time(commit_object.committed_date) > (now - timeframe) and \
                regex.search(str(commit_object.message)):
            project_object = project.create_from_dict(gitlab.get_project(commit_object.project_id))
            results.append({
                'match_string': regex.search(str(commit_object.message)).group(0),
                'commit': commit_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _issue_worker(gitlab: GitLabAPIClient,
                  issue_list: List[Dict],
                  regex: re.Pattern,
                  timeframe: int,
                  results: List,
                  verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of issues to find matches against the regex

    Args:
        gitlab: GitLab API object
        issue_list: List of issues to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for i in issue_list:
        issue_object = issue.create_from_dict(i)
        if convert_time(issue_object.updated_at) > (now - timeframe) and \
                regex.search(str(issue_object.description)):
            match_string = regex.search(str(issue_object.description)).group(0)
            if not verbose:
                setattr(issue_object, 'description', None)
            project_object = project.create_from_dict(gitlab.get_project(issue_object.project_id))
            results.append({
                'match_string': match_string,
                'issue': issue_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _milestone_worker(gitlab: GitLabAPIClient,
                      milestone_list: List[Dict],
                      regex: re.Pattern,
                      timeframe: int,
                      results: List,
                      verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of milestones to find matches against the regex

    Args:
        gitlab: GitLab API object
        milestone_list: List of milestones to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for m in milestone_list:
        milestone_object = milestone.create_from_dict(m)
        if convert_time(milestone_object.updated_at) > (now - timeframe) and \
                regex.search(str(milestone_object.description)):
            project_object = project.create_from_dict(gitlab.get_project(milestone_object.project_id))
            match_string = regex.search(str(milestone_object.description)).group(0)
            if not verbose:
                setattr(milestone_object, 'description', None)
            results.append({
                'match_string': match_string,
                'milestone': milestone_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _merge_request_worker(gitlab: GitLabAPIClient,
                          merge_request_list: List[Dict],
                          regex: re.Pattern,
                          timeframe: int,
                          results: List,
                          verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of merge requests to find matches against the regex

    Args:
        gitlab: GitLab API object
        merge_request_list: List of merge requests to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for mr in merge_request_list:
        mr_object = merge_request.create_from_dict(mr)
        if convert_time(mr_object.updated_at) > (now - timeframe) and \
                regex.search(str(mr_object.description)):
            project_object = project.create_from_dict(gitlab.get_project(mr_object.project_id))
            match_string = regex.search(str(mr_object.description)).group(0)
            if not verbose:
                setattr(mr_object, 'description', None)
            results.append({
                'match_string': match_string,
                'merge_request': mr_object,
                'project': _populate_project_owners(gitlab, project_object)
            })

    return results


def _note_worker(gitlab_object: GitLabAPIClient,
                 note_list: List[Dict],
                 regex: re.Pattern,
                 timeframe: int,
                 results: List,
                 verbose: bool) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of notes to find matches against the regex

    Args:
        note_list: List of notes to process
        regex: Regex pattern to search for
        timeframe: Timeframe to search in
        results: List of output results
        verbose: Whether to use verbose logging
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for n in note_list:
        note_object = note.create_from_dict(n)
        if convert_time(note_object.created_at) > (now - timeframe) and \
                regex.search(str(note_object.body)):
            match_string = regex.search(str(note_object.body)).group(0)
            results.append({
                'note': note_object,
                'match_string': match_string
            })

    return results


def _snippet_worker(gitlab_object: GitLabAPIClient,
                    snippet_list: List[Dict],
                    regex: re.Pattern,
                    timeframe: int,
                    results: List,
                    verbose: bool) -> List[Dict]:
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
        if convert_time(snippet_object.created_at) > (now - timeframe) and \
                (regex.search(str(snippet_object.title)) or regex.search(str(snippet_object.description))):
            if regex.search(str(snippet_object.title)):
                match_string = regex.search(str(snippet_object.title)).group(0)
            else:
                match_string = regex.search(str(snippet_object.description)).group(0)

            if not verbose:
                setattr(snippet_object, 'description', None)
            results.append({
                'snippet': snippet_object,
                'match_string': match_string
            })

    return results
