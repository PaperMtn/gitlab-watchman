import argparse
import calendar
import multiprocessing
import os
import sys
import time
import datetime
import traceback
from importlib import metadata
from typing import List

from gitlab_watchman import watchman_processor
from gitlab_watchman.signature_downloader import SignatureDownloader
from gitlab_watchman.loggers import JSONLogger, StdoutLogger, log_to_csv
from gitlab_watchman.models import (
    signature,
    user,
    project,
    group
)
from gitlab_watchman.exceptions import (
    GitLabWatchmanError,
    GitLabWatchmanGetObjectError,
    GitLabWatchmanNotAuthorisedError,
    GitLabWatchmanAuthenticationError,
    ElasticsearchMissingError,
    MissingEnvVarError
)
from gitlab_watchman.clients.gitlab_client import GitLabAPIClient


def search(gitlab_connection: GitLabAPIClient,
           sig: signature.Signature,
           timeframe: int,
           scope: str,
           verbose: bool):
    """ Use the appropriate search function to search GitLab based on the contents
    of the signature file. Output results to stdout

    Args:
        gitlab_connection: GitLab API object
        sig: Signature object
        timeframe: Timeframe to search for
        scope: What sort of GitLab objects to search
        verbose: Whether to use verbose logging or not
    """

    try:
        OUTPUT_LOGGER.log('INFO', f'Searching for {sig.name} in {scope}')

        results = watchman_processor.search(
            gitlab=gitlab_connection,
            log_handler=OUTPUT_LOGGER,
            sig=sig,
            scope=scope,
            verbose=verbose,
            timeframe=timeframe)
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


def perform_search(gitlab_connection: GitLabAPIClient,
                   sig_list: List[signature.Signature],
                   timeframe: int,
                   verbose_logging: bool,
                   scopes: List[str]):
    """ Helper function to perform the search for each signature and each scope

    Args:
        gitlab_connection: GitLab API object
        sig_list: List of Signature objects
        timeframe: Timeframe to search for
        verbose_logging: Whether to use verbose logging or not
        scopes: List of scopes to search
    """

    for sig in sig_list:
        if sig.scope:
            for scope in scopes:
                if scope in sig.scope:
                    search(gitlab_connection, sig, timeframe, scope, verbose_logging)


def init_logger(logging_type: str, debug: bool) -> JSONLogger | StdoutLogger:
    """ Create a logger object. Defaults to stdout if no option is given

    Args:
        logging_type: Type of logging to use
        debug: Whether to use debug level logging or not
    Returns:
        Logger object
    """

    if not logging_type or logging_type == 'stdout':
        return StdoutLogger(debug=debug)
    return JSONLogger(debug=debug)


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

        if everything:
            OUTPUT_LOGGER.log('INFO', 'Getting everything...')
            perform_search(gitlab_client, signature_list, timeframe, verbose,
                           [
                               'blobs',
                               'commits',
                               'issues',
                               'merge_requests',
                               'wiki_blobs',
                               'milestones',
                               'notes',
                               'snippet_titles'
                           ])
        else:
            if blobs:
                OUTPUT_LOGGER.log('INFO', 'Searching blobs')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['blobs'])
            if commits:
                OUTPUT_LOGGER.log('INFO', 'Searching commits')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['commits'])
            if issues:
                OUTPUT_LOGGER.log('INFO', 'Searching issues')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['issues'])
            if merge:
                OUTPUT_LOGGER.log('INFO', 'Searching merge requests')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['merge_requests'])
            if wiki:
                OUTPUT_LOGGER.log('INFO', 'Searching wiki blobs')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['wiki_blobs'])
            if milestones:
                OUTPUT_LOGGER.log('INFO', 'Searching milestones')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['milestones'])
            if notes:
                OUTPUT_LOGGER.log('INFO', 'Searching notes')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['notes'])
            if snippets:
                OUTPUT_LOGGER.log('INFO', 'Searching snippets')
                perform_search(gitlab_client, signature_list, timeframe, verbose, ['snippet_titles'])

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
