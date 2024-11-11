import argparse
import calendar
import datetime
import multiprocessing
import os
import sys
import time
import traceback
from dataclasses import dataclass
from importlib import metadata
from typing import List

from gitlab_watchman import watchman_processor
from gitlab_watchman.clients.gitlab_client import GitLabAPIClient
from gitlab_watchman.signature_downloader import SignatureDownloader
from gitlab_watchman.exceptions import (
    GitLabWatchmanError,
    GitLabWatchmanGetObjectError,
    GitLabWatchmanNotAuthorisedError,
    GitLabWatchmanAuthenticationError,
    ElasticsearchMissingError,
    MissingEnvVarError
)
from gitlab_watchman.loggers import (
    JSONLogger,
    StdoutLogger,
    log_to_csv,
    init_logger
)
from gitlab_watchman.models import (
    signature,
    user,
    project,
    group
)


@dataclass
class SearchArgs:
    """ Dataclass to hold search arguments """
    gitlab_client: GitLabAPIClient
    sig_list: List[signature.Signature]
    timeframe: int
    logging_type: str
    log_handler: JSONLogger | StdoutLogger
    debug: bool
    verbose: bool
    scopes: List[str]


def search(search_args: SearchArgs, sig: signature.Signature, scope: str):
    """ Use the appropriate search function to search GitLab based on the contents
    of the signature file. Output results to stdout

    Args:
        search_args: SearchArgs object
        sig: Signature object
        scope: What sort of GitLab objects to search
    """

    try:
        OUTPUT_LOGGER.log('INFO', f'Searching for {sig.name} in {scope}')

        results = watchman_processor.search(
            gitlab=search_args.gitlab_client,
            logging_type=search_args.logging_type,
            log_handler=search_args.log_handler,
            debug=search_args.debug,
            sig=sig,
            scope=scope,
            verbose=search_args.verbose,
            timeframe=search_args.timeframe)
        if results:
            for log_data in results:
                OUTPUT_LOGGER.log(
                    'NOTIFY',
                    log_data,
                    scope=scope,
                    severity=sig.severity,
                    detect_type=sig.name,
                    notify_type='result')
    except ElasticsearchMissingError as e:
        OUTPUT_LOGGER.log('WARNING', e)
        OUTPUT_LOGGER.log('DEBUG', traceback.format_exc())
    except Exception as e:
        raise e


def perform_search(search_args: SearchArgs):
    """ Helper function to perform the search for each signature and each scope

    Args:
        search_args: SearchArgs object
    """

    for sig in search_args.sig_list:
        if sig.scope:
            for scope in search_args.scopes:
                if scope in sig.scope:
                    search(search_args, sig, scope)


def validate_variables() -> bool:
    """ Validate whether GitLab Watchman environment variables have been set

    Returns:
        True if both variables are set
    """

    required_vars = ['GITLAB_WATCHMAN_TOKEN', 'GITLAB_WATCHMAN_URL']

    for var in required_vars:
        if var not in os.environ:
            raise MissingEnvVarError(var)

    return True


# pylint: disable=too-many-locals, missing-function-docstring, global-variable-undefined
# pylint: disable=too-many-branches, disable=too-many-statements
def main():
    global OUTPUT_LOGGER
    try:
        start_time = time.time()
        project_metadata = metadata.metadata('gitlab-watchman')
        parser = argparse.ArgumentParser(description='Finding exposed secrets and personal data in GitLab')
        required = parser.add_argument_group('required arguments')
        required.add_argument('--timeframe', choices=['d', 'w', 'm', 'a'], dest='time',
                              help='How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time',
                              required=True)
        parser.add_argument('--output', '-o', choices=['json', 'stdout'], dest='logging_type',
                            help='Where to send results')
        parser.add_argument('--version', '-v', action='version',
                            version=f'GitLab Watchman: {project_metadata.get("version")}')
        parser.add_argument('--all', '-a', dest='everything', action='store_true',
                            help='Find everything')
        parser.add_argument('--blobs', '-b', dest='blobs', action='store_true',
                            help='Search code blobs')
        parser.add_argument('--commits', '-c', dest='commits', action='store_true',
                            help='Search commits')
        parser.add_argument('--wiki-blobs', '-w', dest='wiki', action='store_true',
                            help='Search wiki blobs')
        parser.add_argument('--issues', '-i', dest='issues', action='store_true',
                            help='Search issues')
        parser.add_argument('--merge-requests', '-mr', dest='merge', action='store_true',
                            help='Search merge requests')
        parser.add_argument('--milestones', '-m', dest='milestones', action='store_true',
                            help='Search milestones')
        parser.add_argument('--notes', '-n', dest='notes', action='store_true',
                            help='Search notes')
        parser.add_argument('--snippets', '-s', dest='snippets', action='store_true',
                            help='Search snippets')
        parser.add_argument('--enumerate', '-e', dest='enum', action='store_true',
                            help='Enumerate this GitLab instance for users, groups, projects.'
                                 'Output will be saved to CSV files')
        parser.add_argument('--debug', '-d', dest='debug', action='store_true', help='Turn on debug level logging')
        parser.add_argument('--verbose', '-V', dest='verbose', action='store_true',
                            help='Turn on more verbose output for JSON logging. '
                                 'This includes more fields, but is larger')

        args = parser.parse_args()
        everything = args.everything
        blobs = args.blobs
        commits = args.commits
        logging_type = args.logging_type
        wiki = args.wiki
        issues = args.issues
        merge = args.merge
        milestones = args.milestones
        notes = args.notes
        snippets = args.snippets
        verbose = args.verbose
        debug = args.debug
        enum = args.enum

        tf_options = {
            'd': 86400,
            'w': 604800,
            'm': 2592000,
            'a': calendar.timegm(time.gmtime()) + 1576800000
        }
        timeframe = tf_options.get(args.time)

        OUTPUT_LOGGER = init_logger(logging_type, debug)

        validate_variables()
        gitlab_client = watchman_processor.initiate_gitlab_connection(
            os.environ.get('GITLAB_WATCHMAN_TOKEN'),
            os.environ.get('GITLAB_WATCHMAN_URL'))

        now = int(time.time())
        today = datetime.date.today().strftime('%Y-%m-%d')
        start_date = time.strftime('%Y-%m-%d', time.localtime(now - timeframe))

        OUTPUT_LOGGER.log('SUCCESS', 'GitLab Watchman started execution')
        OUTPUT_LOGGER.log('INFO', f'Version: {project_metadata.get("version")}')
        OUTPUT_LOGGER.log('INFO', 'Created by: PaperMtn <papermtn@protonmail.com>')
        OUTPUT_LOGGER.log('INFO', f'Searching GitLab instance {os.environ.get("GITLAB_WATCHMAN_URL")}')
        OUTPUT_LOGGER.log('INFO', f'Searching from {start_date} to {today}')
        if verbose:
            OUTPUT_LOGGER.log('INFO', 'Verbose logging enabled')
        else:
            OUTPUT_LOGGER.log('INFO', 'Using non-verbose logging')

        OUTPUT_LOGGER.log('INFO', 'Downloading and importing signatures')
        signature_list = SignatureDownloader(OUTPUT_LOGGER).download_signatures()
        OUTPUT_LOGGER.log('SUCCESS', f'{len(signature_list)} signatures loaded')
        OUTPUT_LOGGER.log('INFO', f'{multiprocessing.cpu_count() - 1} cores being used')

        instance_metadata = gitlab_client.get_metadata()
        OUTPUT_LOGGER.log('INSTANCE', instance_metadata, detect_type='Instance', notify_type='instance')
        authenticated_user = gitlab_client.get_user_info()
        OUTPUT_LOGGER.log('USER', authenticated_user, detect_type='User', notify_type='user')
        if authenticated_user.get('is_admin'):
            OUTPUT_LOGGER.log('SUCCESS', 'This user is an administrator on this GitLab instance!')

        token_info = gitlab_client.get_authed_access_token_value()
        OUTPUT_LOGGER.log('TOKEN', token_info, detect_type='Token', notify_type='token')

        if enum:
            OUTPUT_LOGGER.log('SUCCESS', 'Carrying out enumeration')
            OUTPUT_LOGGER.log('INFO', 'Enumerating users...')
            gitlab_user_output = gitlab_client.get_all_users()
            user_objects = []
            for u in gitlab_user_output:
                user_objects.append(user.create_from_dict(u))
            OUTPUT_LOGGER.log('SUCCESS', f'{len(gitlab_user_output)} users discovered')
            OUTPUT_LOGGER.log('INFO', 'Writing to csv')
            log_to_csv('gitlab_users', user_objects)
            OUTPUT_LOGGER.log(
                'SUCCESS',
                f'Users output to CSV file: {os.path.join(os.getcwd(), "gitlab_users.csv")}')

            OUTPUT_LOGGER.log('INFO', 'Enumerating groups...')
            gitlab_groups_output = gitlab_client.get_all_groups()
            group_objects = []
            for g in gitlab_groups_output:
                group_objects.append(group.create_from_dict(g))
            OUTPUT_LOGGER.log('SUCCESS', f'{len(group_objects)} groups discovered')
            OUTPUT_LOGGER.log('INFO', 'Writing to csv')
            log_to_csv('gitlab_groups', group_objects)
            OUTPUT_LOGGER.log(
                'SUCCESS',
                f'Groups output to CSV file: {os.path.join(os.getcwd(), "gitlab_groups.csv")}')

            OUTPUT_LOGGER.log('INFO', 'Enumerating projects...')
            gitlab_projects_output = gitlab_client.get_all_projects()
            project_objects = []
            for p in gitlab_projects_output:
                project_objects.append(project.create_from_dict(p))
            OUTPUT_LOGGER.log('SUCCESS', f'{len(project_objects)} projects discovered')
            OUTPUT_LOGGER.log('INFO', 'Writing to csv')
            log_to_csv('gitlab_projects', project_objects)
            OUTPUT_LOGGER.log(
                'SUCCESS',
                f'Projects output to CSV file: {os.path.join(os.getcwd(), "gitlab_projects.csv")}')

        search_args = SearchArgs(
            gitlab_client=gitlab_client,
            sig_list=signature_list,
            timeframe=timeframe,
            logging_type=logging_type,
            log_handler=OUTPUT_LOGGER,
            debug=debug,
            verbose=verbose,
            scopes=[])

        if everything:
            OUTPUT_LOGGER.log('INFO', 'Getting everything...')
            search_args.scopes = [
                    'blobs',
                    'commits',
                    'issues',
                    'merge_requests',
                    'wiki_blobs',
                    'milestones',
                    'notes',
                    'snippet_titles'
                ]
            perform_search(search_args)
        else:
            if blobs:
                OUTPUT_LOGGER.log('INFO', 'Searching blobs')
                search_args.scopes = ['blobs']
                perform_search(search_args)
            if commits:
                OUTPUT_LOGGER.log('INFO', 'Searching commits')
                search_args.scopes = ['commits']
                perform_search(search_args)
            if issues:
                OUTPUT_LOGGER.log('INFO', 'Searching issues')
                search_args.scopes = ['issues']
                perform_search(search_args)
            if merge:
                OUTPUT_LOGGER.log('INFO', 'Searching merge requests')
                search_args.scopes = ['merge_requests']
                perform_search(search_args)
            if wiki:
                OUTPUT_LOGGER.log('INFO', 'Searching wiki blobs')
                search_args.scopes = ['wiki_blobs']
                perform_search(search_args)
            if milestones:
                OUTPUT_LOGGER.log('INFO', 'Searching milestones')
                search_args.scopes = ['milestones']
                perform_search(search_args)
            if notes:
                OUTPUT_LOGGER.log('INFO', 'Searching notes')
                search_args.scopes = ['notes']
                perform_search(search_args)
            if snippets:
                OUTPUT_LOGGER.log('INFO', 'Searching snippets')
                search_args.scopes = ['snippet_titles']
                perform_search(search_args)

        OUTPUT_LOGGER.log('SUCCESS', f'GitLab Watchman finished execution - Execution time:'
                                     f' {str(datetime.timedelta(seconds=time.time() - start_time))}')

    except (ElasticsearchMissingError,
            GitLabWatchmanNotAuthorisedError,
            GitLabWatchmanGetObjectError,
            GitLabWatchmanAuthenticationError) as e:
        OUTPUT_LOGGER.log('WARNING', e)
        OUTPUT_LOGGER.log('DEBUG', traceback.format_exc())
    except Exception as e:
        OUTPUT_LOGGER.log('CRITICAL', e)
        OUTPUT_LOGGER.log('DEBUG', traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
