import calendar
import multiprocessing
import re
import time
import traceback
import hashlib
from multiprocessing import Queue
from dataclasses import dataclass
from typing import List, Dict, Optional

from requests.exceptions import SSLError

from gitlab_watchman.clients.gitlab_client import GitLabAPIClient
from gitlab_watchman.exceptions import GitLabWatchmanAuthenticationError
from gitlab_watchman.loggers import JSONLogger, StdoutLogger, init_logger
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
    project,
    group
)
from gitlab_watchman.utils import (
    convert_to_epoch,
    deduplicate_results,
    split_to_chunks
)

ALL_TIME = calendar.timegm(time.gmtime()) + 1576800000


@dataclass
class WorkerArgs:
    """ Dataclass for multiprocessing arguments """
    gitlab_client: GitLabAPIClient
    search_result_list: List[Dict]
    regex: re.Pattern[str]
    timeframe: int
    results_list: List[Dict]
    verbose: bool
    log_queue: Optional[Queue] = None
    log_handler: Optional[JSONLogger | StdoutLogger] = None


def initiate_gitlab_connection(token: str,
                               url: str) -> GitLabAPIClient:
    """ Create a GitLab API client object

    Returns:
        GitLab API client object
    Raises:
        GitLabWatchmanAuthenticationError: If an error occurs while creating the GitLab API client object
    """

    try:
        return GitLabAPIClient(token, url)
    except SSLError as e:
        raise GitLabWatchmanAuthenticationError('SSL Error: Please check your GitLab URL and try again') from e
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
    for user_dict in group_members:
        if user_dict.get('state') == 'active' and user_dict.get('access_level') == 50:
            member_list.append({
                'user_id': user_dict.get('id'),
                'name': user_dict.get('name'),
                'username': user_dict.get('username'),
                'access_level': 'Owner'
            })

    return member_list


def log_listener(log_queue: Queue, logging_type: str, debug: bool):
    """ Listener for use in multiprocessing queued logging

    Args:
        log_queue: Queue object
        logging_type: Type of logging to use
        debug: Whether to use debug level logging or not
    """
    log_handler = init_logger(logging_type, debug)
    while True:
        record = log_queue.get()
        if record is None:
            break
        level, message = record
        log_handler.log(level, message)


def search(gitlab: GitLabAPIClient,
           logging_type: str,
           log_handler: JSONLogger | StdoutLogger,
           debug: bool,
           sig: signature.Signature,
           scope: str,
           verbose: bool,
           timeframe: int = ALL_TIME) -> List[Dict] | None:
    """ Use the appropriate search function to search GitLab based on the contents
    of the signature file

    Args:
        gitlab: GitLab API object
        logging_type: Type of logging to use
        log_handler: Logger object
        debug: Whether to use debug level logging or not
        sig: Signature object
        scope: What sort of GitLab objects to search
        verbose: Whether to use verbose logging
        timeframe: Timeframe in seconds
    Returns:
        List of search results from GitLab API or None

    """
    results = []

    if logging_type == 'json':
        log_queue = Queue()
        log_process = multiprocessing.Process(target=log_listener, args=(log_queue, logging_type, debug))
        log_process.start()

    for query in sig.search_strings:
        for pattern in sig.patterns:
            regex = re.compile(pattern)
            search_results = gitlab.global_search(query, search_scope=scope)
            query_formatted = query.replace('"', '')
            if search_results:
                if logging_type == 'json':
                    log_queue.put(('INFO', f'{len(search_results)} {scope} '
                                           f'found matching search term: {query_formatted}'))
                else:
                    log_handler.log('INFO', f'{len(search_results)} {scope} '
                                            f'found matching search term: {query_formatted}')

                result = multiprocessing.Manager().list()

                chunks = multiprocessing.cpu_count() - 1
                list_of_chunks = split_to_chunks(search_results, chunks)

                processes = []

                target_func_dict = {
                    'blobs': _blob_worker,
                    'wiki_blobs': _wiki_blob_worker,
                    'commits': _commit_worker,
                    'snippet_titles': _snippet_worker,
                    'issues': _issue_worker,
                    'milestones': _milestone_worker,
                    'merge_requests': _merge_request_worker,
                    'notes': _note_worker,
                }
                target_func = target_func_dict.get(scope, _blob_worker)

                for search_list in list_of_chunks:
                    multipro_args = WorkerArgs(
                        gitlab_client=gitlab,
                        search_result_list=search_list,
                        regex=regex,
                        timeframe=timeframe,
                        results_list=result,
                        verbose=verbose
                    )
                    if logging_type == 'json':
                        multipro_args.log_queue = log_queue
                    else:
                        multipro_args.log_handler = log_handler
                    p = multiprocessing.Process(target=target_func, args=(multipro_args,))
                    processes.append(p)
                    p.start()

                for process in processes:
                    process.join()

                results.append(list(result))
            else:
                if logging_type == 'json':
                    log_queue.put(('INFO', f'No {scope} found matching search term: {query_formatted}'))
                else:
                    log_handler.log('INFO', f'No {scope} found matching search term: {query_formatted}')
    if results:
        results = deduplicate_results([item for sublist in results for item in sublist])
        if logging_type == 'json':
            log_queue.put(('INFO', f'{len(results)} total matches found after filtering'))
            log_queue.put(None)
            log_process.join()
        else:
            log_handler.log('INFO', f'{len(results)} total matches found after filtering')
        return results
    else:
        if logging_type == 'json':
            log_queue.put(('INFO', 'No matches found after filtering'))
            log_queue.put(None)
            log_process.join()
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
            project_object.namespace.owner = user.create_from_dict(namespace_user)
            project_object.namespace.members = None

    return project_object


def _blob_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of blobs to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                                    GitLab client, search list, regex pattern,
                                    timeframe, results list, verbosity flag, and log handler.
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for blob_dict in args.search_result_list:
        try:
            blob_object = blob.create_from_dict(blob_dict)
            project_object = project.create_from_dict(args.gitlab_client.get_project(blob_object.project_id))
            file_object = file.create_from_dict(
                args.gitlab_client.get_file(blob_object.project_id, blob_object.path, blob_object.ref))
            if file_object:
                commit_object = commit.create_from_dict(
                    args.gitlab_client.get_commit(blob_object.project_id, file_object.commit_id))
                if convert_to_epoch(commit_object.committed_date) > (now - args.timeframe) and args.regex.search(
                        str(blob_object.data)):
                    match_string = args.regex.search(str(blob_object.data)).group(0)
                    if not args.verbose:
                        setattr(blob_object, 'data', None)
                    watchman_id = hashlib.md5(f'{match_string}.{file_object.file_path}'.encode()).hexdigest()
                    args.results_list.append({
                        'match_string': match_string,
                        'blob': blob_object,
                        'commit': commit_object,
                        'project': _populate_project_owners(args.gitlab_client, project_object),
                        'file': file_object,
                        'watchman_id': watchman_id
                    })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _wiki_blob_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of wiki_blobs to find matches against the regex.

    Args:
        args: Multiprocessing arguments containing the
                                    GitLab client, search list, regex pattern,
                                    timeframe, results list, verbosity flag, and log handler.
    Returns:
        List[Dict]: Multiprocessing list to be combined by the parent process.
    """

    for wb_dict in args.search_result_list:
        try:
            wikiblob_object = wiki_blob.create_from_dict(wb_dict)
            project_wiki = False
            group_wiki = False
            if wb_dict.get('project_id'):
                project_object = project.create_from_dict(args.gitlab_client.get_project(wb_dict.get('project_id')))
                project_wiki = True
            if wb_dict.get('group_id'):
                group_object = group.create_from_dict(args.gitlab_client.get_group(wb_dict.get('group_id')))
                group_wiki = True

            if args.regex.search(
                    str(wikiblob_object.data)):
                match_string = args.regex.search(str(wikiblob_object.data)).group(0)
                if not args.verbose:
                    setattr(wikiblob_object, 'data', None)
                watchman_id = hashlib.md5(f'{match_string}.{wikiblob_object.path}'.encode()).hexdigest()
                results_dict = {
                    'match_string': match_string,
                    'wiki_blob': wikiblob_object,
                    'group_wiki': group_wiki,
                    'project_wiki': project_wiki,
                    'watchman_id': watchman_id
                }
                if project_wiki:
                    results_dict['project'] = _populate_project_owners(args.gitlab_client, project_object)
                if group_wiki:
                    results_dict['group'] = group_object
                args.results_list.append(results_dict)
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _commit_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of commits to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                                    GitLab client, search list, regex pattern,
                                    timeframe, results list, verbosity flag, and log handler.
    Returns:
        List of JSON formatted results if any are found
    """

    now = calendar.timegm(time.gmtime())

    for commit_dict in args.search_result_list:
        try:
            commit_object = commit.create_from_dict(commit_dict)
            if convert_to_epoch(commit_object.committed_date) > (now - args.timeframe) and \
                    args.regex.search(str(commit_object.message)):
                project_object = project.create_from_dict(args.gitlab_client.get_project(commit_object.project_id))
                match_string = args.regex.search(str(commit_object.message)).group(0)
                watchman_id = hashlib.md5(f'{match_string}.{commit_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'match_string': match_string,
                    'commit': commit_object,
                    'project': _populate_project_owners(args.gitlab_client, project_object),
                    'watchman_id': watchman_id
                })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _issue_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of issues to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                                    GitLab client, search list, regex pattern,
                                    timeframe, results list, verbosity flag, and log handler.
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for issue_dict in args.search_result_list:
        try:
            issue_object = issue.create_from_dict(issue_dict)
            if convert_to_epoch(issue_object.updated_at) > (now - args.timeframe) and \
                    args.regex.search(str(issue_object.description)):
                match_string = args.regex.search(str(issue_object.description)).group(0)
                if not args.verbose:
                    setattr(issue_object, 'description', None)
                project_object = project.create_from_dict(args.gitlab_client.get_project(issue_object.project_id))
                watchman_id = hashlib.md5(f'{match_string}.{issue_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'match_string': match_string,
                    'issue': issue_object,
                    'project': _populate_project_owners(args.gitlab_client, project_object),
                    'watchman_id': watchman_id
                })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _milestone_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of milestones to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for milestone_dict in args.search_result_list:
        try:
            milestone_object = milestone.create_from_dict(milestone_dict)
            if convert_to_epoch(milestone_object.updated_at) > (now - args.timeframe) and \
                    args.regex.search(str(milestone_object.description)):
                project_object = project.create_from_dict(args.gitlab_client.get_project(milestone_object.project_id))
                match_string = args.regex.search(str(milestone_object.description)).group(0)
                if not args.verbose:
                    setattr(milestone_object, 'description', None)
                watchman_id = hashlib.md5(f'{match_string}.{milestone_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'match_string': match_string,
                    'milestone': milestone_object,
                    'project': _populate_project_owners(args.gitlab_client, project_object),
                    'watchman_id': watchman_id
                })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _merge_request_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of merge requests to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                                    GitLab client, search list, regex pattern,
                                    timeframe, results list, verbosity flag, and log handler.
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for mr_dict in args.search_result_list:
        try:
            mr_object = merge_request.create_from_dict(mr_dict)
            if convert_to_epoch(mr_object.updated_at) > (now - args.timeframe) and \
                    args.regex.search(str(mr_object.description)):
                project_object = project.create_from_dict(args.gitlab_client.get_project(mr_object.project_id))
                match_string = args.regex.search(str(mr_object.description)).group(0)
                if not args.verbose:
                    setattr(mr_object, 'description', None)
                watchman_id = hashlib.md5(f'{match_string}.{mr_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'match_string': match_string,
                    'merge_request': mr_object,
                    'project': _populate_project_owners(args.gitlab_client, project_object),
                    'watchman_id': watchman_id
                })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _note_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of notes to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                GitLab client, search list, regex pattern,
                timeframe, results list, verbosity flag, and log handler.
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    try:
        for note_dict in args.search_result_list:
            note_object = note.create_from_dict(note_dict)
            if convert_to_epoch(note_object.created_at) > (now - args.timeframe) and \
                    args.regex.search(str(note_object.body)):
                match_string = args.regex.search(str(note_object.body)).group(0)
                watchman_id = hashlib.md5(f'{match_string}.{note_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'note': note_object,
                    'match_string': match_string,
                    'watchman_id': watchman_id
                })
    except Exception as e:
        if args.log_handler:
            args.log_handler.log('WARNING', e)
            args.log_handler.log('DEBUG', traceback.format_exc())
        else:
            args.log_queue.put('WARNING', e)
            args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list


def _snippet_worker(args: WorkerArgs) -> List[Dict]:
    """ MULTIPROCESSING WORKER - Iterates through a list of snippets to find matches against the regex

    Args:
        args: Multiprocessing arguments containing the
                GitLab client, search list, regex pattern,
                timeframe, results list, verbosity flag, and log handler.
    Returns:
        Multiprocessing list to be combined by the parent process
    """

    now = calendar.timegm(time.gmtime())
    for snippet_dict in args.search_result_list:
        try:
            snippet_object = snippet.create_from_dict(snippet_dict)
            if convert_to_epoch(snippet_object.created_at) > (now - args.timeframe) and \
                    (args.regex.search(str(snippet_object.title)) or
                     args.regex.search(str(snippet_object.description))):
                if args.regex.search(str(snippet_object.title)):
                    match_string = args.regex.search(str(snippet_object.title)).group(0)
                else:
                    match_string = args.regex.search(str(snippet_object.description)).group(0)
                if not args.verbose:
                    setattr(snippet_object, 'description', None)
                watchman_id = hashlib.md5(f'{match_string}.{snippet_object.id}'.encode()).hexdigest()
                args.results_list.append({
                    'snippet': snippet_object,
                    'match_string': match_string,
                    'watchman_id': watchman_id
                })
        except Exception as e:
            if args.log_handler:
                args.log_handler.log('WARNING', e)
                args.log_handler.log('DEBUG', traceback.format_exc())
            else:
                args.log_queue.put('WARNING', e)
                args.log_queue.put('DEBUG', traceback.format_exc())
    return args.results_list
