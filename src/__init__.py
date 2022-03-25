import argparse
import calendar
import os
import yaml
import time
from pathlib import Path
from datetime import date

from gitlab_watchman import gitlab_wrapper
from gitlab_watchman import __version__
from gitlab_watchman import logger as logger
from gitlab_watchman import signature

SIGNATURE_PATH = (Path(__file__).parent / 'gitlab_watchman/signatures').resolve()
OUTPUT_LOGGER = logger.StdoutLogger


def validate_conf(path: Path) -> bool:
    """ Check the file watchman.conf exists

    Args:
        path: Path .conf file is located in
    Returns:
        True if file exists
    """

    if os.environ.get('GITLAB_WATCHMAN_TOKEN') and os.environ.get('GITLAB_WATCHMAN_URL'):
        return True
    if os.path.exists(path):
        with open(path) as yaml_file:
            return yaml.safe_load(yaml_file).get('gitlab_watchman')


def search(gitlab_connection: gitlab_wrapper.GitLabAPIClient,
           sig: signature.Signature,
           tf: int,
           scope: str):
    """ Use the appropriate search function to search GitLab based on the contents
    of the signature file. Outputs results to stdout

    Args:
        gitlab_connection: GitLab API object
        sig: Signature object
        tf: Timeframe to search for
        scope: What sort of GitLab objects to search
    """

    try:
        OUTPUT_LOGGER.log_info(f'Searching for {sig.meta.name} in {scope}')

        results = gitlab_wrapper.search(gitlab_connection, OUTPUT_LOGGER, sig, scope, tf)
        if results:
            for log_data in results:
                OUTPUT_LOGGER.log_notification(log_data, scope, sig.meta.name, sig.meta.severity)
    except Exception as e:

        OUTPUT_LOGGER.log_critical(e)


def init_logger() -> logger.StdoutLogger:
    """ Create a logger object

    Returns:
        Logging object for outputting results
    """

    return logger.StdoutLogger()


def load_signatures() -> list[signature.Signature]:
    """ Load signatures from YAML files

    Returns:
        List containing loaded definitions as signatures objects
    """

    loaded_signatures = []
    try:
        for root, dirs, files in os.walk(SIGNATURE_PATH):
            for sig_file in files:
                sig_path = (Path(root) / sig_file).resolve()
                if sig_path.name.endswith('.yaml'):
                    loaded_def = signature.load_from_yaml(sig_path)
                    if loaded_def.enabled:
                        loaded_signatures.append(loaded_def)
        return loaded_signatures
    except Exception as e:
        raise e


def main():
    global OUTPUT_LOGGER
    try:
        OUTPUT_LOGGER = init_logger()
        parser = argparse.ArgumentParser(description=__version__.__summary__)
        required = parser.add_argument_group('required arguments')
        required.add_argument('--timeframe', choices=['d', 'w', 'm', 'a'], dest='time',
                              help='How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time',
                              required=True)
        parser.add_argument('--version', action='version',
                            version=f'gitlab-watchman {__version__.__version__}')
        parser.add_argument('--all', dest='everything', action='store_true',
                            help='Find everything')
        parser.add_argument('--blobs', dest='blobs', action='store_true',
                            help='Search code blobs')
        parser.add_argument('--commits', dest='commits', action='store_true',
                            help='Search commits')
        parser.add_argument('--wiki-blobs', dest='wiki', action='store_true',
                            help='Search wiki blobs')
        parser.add_argument('--issues', dest='issues', action='store_true',
                            help='Search issues')
        parser.add_argument('--merge-requests', dest='merge', action='store_true',
                            help='Search merge requests')
        parser.add_argument('--milestones', dest='milestones', action='store_true',
                            help='Search milestones')
        parser.add_argument('--notes', dest='notes', action='store_true',
                            help='Search notes')
        parser.add_argument('--snippets', dest='snippets', action='store_true',
                            help='Search snippets')

        args = parser.parse_args()
        tm = args.time
        everything = args.everything
        blobs = args.blobs
        commits = args.commits
        wiki = args.wiki
        issues = args.issues
        merge = args.merge
        milestones = args.milestones
        notes = args.notes
        snippets = args.snippets

        if tm == 'd':
            tf = 86400
        elif tm == 'w':
            tf = 604800
        elif tm == 'm':
            tf = 2592000
        else:
            tf = calendar.timegm(time.gmtime()) + 1576800000
        conf_path = f'{os.path.expanduser("~")}/watchman.conf'

        if not validate_conf(conf_path):
            raise Exception('GITLAB_WATCHMAN_TOKEN environment variable or watchman.conf file not detected. '
                            '\nEnsure environment variable is set or a valid file is located in your home '
                            'directory')
        else:
            config = validate_conf(conf_path)
            connection = gitlab_wrapper.initiate_gitlab_connection()

        now = int(time.time())
        today = date.today().strftime('%Y-%m-%d')
        start_date = time.strftime('%Y-%m-%d', time.localtime(now - tf))

        OUTPUT_LOGGER.log_info(f'Version: {__version__.__version__}')
        OUTPUT_LOGGER.log_info(f'Searching from {start_date} to {today}')
        OUTPUT_LOGGER.log_info('Importing signatures...')
        sig_list = load_signatures()
        OUTPUT_LOGGER.log_info(f'{len(sig_list)} signatures loaded')

        if everything:
            OUTPUT_LOGGER.log_info('Getting everything...')
            for sig in sig_list:
                if 'blobs' in sig.scope:
                    search(connection, sig, tf, 'blobs')
                if 'commits' in sig.scope:
                    search(connection, sig, tf, 'commits')
                if 'issues' in sig.scope:
                    search(connection, sig, tf, 'issues')
                if 'merge_requests' in sig.scope:
                    search(connection, sig, tf, 'merge_requests')
                if 'wiki_blobs' in sig.scope:
                    search(connection, sig, tf, 'wiki_blobs')
                if 'milestones' in sig.scope:
                    search(connection, sig, tf, 'milestones')
                if 'notes' in sig.scope:
                    search(connection, sig, tf, 'notes')
                if 'snippet_titles' in sig.scope:
                    search(connection, sig, tf, 'snippet_titles')
        else:
            if blobs:
                OUTPUT_LOGGER.log_info('Searching blobs')
                for sig in sig_list:
                    if 'blobs' in sig.scope:
                        search(connection, sig, tf, 'blobs')
            if commits:
                OUTPUT_LOGGER.log_info('Searching commits')
                for sig in sig_list:
                    if 'commits' in sig.scope:
                        search(connection, sig, tf, 'commits')
            if issues:
                OUTPUT_LOGGER.log_info('Searching issues')
                for sig in sig_list:
                    if 'issues' in sig.scope:
                        search(connection, sig, tf, 'issues')
            if merge:
                OUTPUT_LOGGER.log_info('Searching merge requests')
                for sig in sig_list:
                    if 'merge_requests' in sig.scope:
                        search(connection, sig, tf, 'merge_requests')
            if wiki:
                OUTPUT_LOGGER.log_info('Searching wiki blobs')
                for sig in sig_list:
                    if 'wiki_blobs' in sig.scope:
                        search(connection, sig, tf, 'wiki_blobs')
            if milestones:
                OUTPUT_LOGGER.log_info('Searching milestones')
                for sig in sig_list:
                    if 'milestones' in sig.scope:
                        search(connection, sig, tf, 'milestones')
            if notes:
                OUTPUT_LOGGER.log_info('Searching notes')
                for sig in sig_list:
                    if 'notes' in sig.scope:
                        search(connection, sig, tf, 'notes')
            if snippets:
                OUTPUT_LOGGER.log_info('Searching snippets')
                for sig in sig_list:
                    if 'snippet_titles' in sig.scope:
                        search(connection, sig, tf, 'snippet_titles')

        OUTPUT_LOGGER.log_info('++++++Audit completed++++++')

    except Exception as e:
        OUTPUT_LOGGER.log_critical(e)


if __name__ == '__main__':
    main()
