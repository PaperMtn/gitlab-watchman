import builtins
import argparse
import os
import yaml
import time
from pathlib import Path
from datetime import date
from colorama import init, deinit
from termcolor import colored

import gitlab_watchman.gitlab_wrapper as gitlab
import gitlab_watchman.__about__ as a
import gitlab_watchman.config as cfg
import gitlab_watchman.logger as logger


RULES_PATH = (Path(__file__).parent / 'rules').resolve()
OUTPUT_LOGGER = ''


def validate_conf(path):
    """Check the file watchman.conf exists"""

    if os.environ.get('GITLAB_WATCHMAN_TOKEN') and os.environ.get('GITLAB_WATCHMAN_URL'):
        return True
    if os.path.exists(path):
        with open(path) as yaml_file:
            return yaml.safe_load(yaml_file).get('gitlab_watchman')


def search(gitlab_connection, rule, tf, scope):
    if isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
        print = OUTPUT_LOGGER.log_info
    else:
        print = builtins.print
    try:
        if scope == 'blobs':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'blobs'), 'yellow'))

            blobs = gitlab.search_blobs(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if blobs:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'blobs',
                                            blobs)
                else:
                    for log_data in blobs:
                        OUTPUT_LOGGER.log_notification(log_data, 'blobs', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')

        if scope == 'commits':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'commits'), 'yellow'))

            commits = gitlab.search_commits(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if commits:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'commits',
                                            commits)
                else:
                    for log_data in commits:
                        OUTPUT_LOGGER.log_notification(log_data, 'commits', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')

        if scope == 'issues':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'issues'), 'yellow'))

            issues = gitlab.search_issues(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if issues:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'issues',
                                            issues)
                else:
                    for log_data in issues:
                        OUTPUT_LOGGER.log_notification(log_data, 'issues', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')

        if scope == 'wiki_blobs':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'wiki blobs'), 'yellow'))

            wiki_blobs = gitlab.search_wiki_blobs(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if wiki_blobs:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'wiki_blobs',
                                            wiki_blobs)
                else:
                    for log_data in wiki_blobs:
                        OUTPUT_LOGGER.log_notification(log_data, 'wiki_blobs', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')

        if scope == 'merge_requests':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'merge requests'), 'yellow'))

            merge_requests = gitlab.search_merge_requests(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if merge_requests:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'merge_requests',
                                            merge_requests)
                else:
                    for log_data in merge_requests:
                        OUTPUT_LOGGER.log_notification(log_data, 'merge_requests', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')

        if scope == 'milestones':
            print(colored('Searching for {} in {}'.format(rule.get('meta').get('name'),
                                                          'milestones'), 'yellow'))
            milestones = gitlab.search_milestones(gitlab_connection, OUTPUT_LOGGER, rule, tf)
            if milestones:
                if isinstance(OUTPUT_LOGGER, logger.CSVLogger):
                    OUTPUT_LOGGER.write_csv('exposed_{}'.format(rule.get('filename').split('.')[0]),
                                            'milestones',
                                            milestones)
                else:
                    for log_data in milestones:
                        OUTPUT_LOGGER.log_notification(log_data, 'milestones', rule.get('meta').get('name'),
                                                       rule.get('meta').get('severity'))
                    print('Results output to log')
    except Exception as e:
        if isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
            print = OUTPUT_LOGGER.log_critical
        else:
            print = builtins.print

        print(colored(e, 'red'))


def load_rules():
    rules = []
    try:
        for file in os.scandir(RULES_PATH):
            if file.name.endswith('.yaml'):
                with open(file) as yaml_file:
                    rule = yaml.safe_load(yaml_file)
                    if rule.get('enabled'):
                        rules.append(rule)
        return rules
    except Exception as e:
        if isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
            print = OUTPUT_LOGGER.log_critical
        else:
            print = builtins.print

        print(colored(e, 'red'))


def main():
    global OUTPUT_LOGGER
    try:
        init()

        if isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
            print = OUTPUT_LOGGER.log_critical
        else:
            print = builtins.print

        parser = argparse.ArgumentParser(description=a.__summary__)
        required = parser.add_argument_group('required arguments')
        required.add_argument('--timeframe', choices=['d', 'w', 'm', 'a'], dest='time',
                              help='How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time',
                              required=True)
        required.add_argument('--output', choices=['csv', 'file', 'stdout', 'stream'], dest='logging_type',
                              help='Where to send results', required=True)
        parser.add_argument('--version', action='version',
                            version='gitlab-watchman {}'.format(a.__version__))
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

        args = parser.parse_args()
        tm = args.time
        everything = args.everything
        blobs = args.blobs
        commits = args.commits
        wiki = args.wiki
        issues = args.issues
        merge = args.merge
        milestones = args.milestones
        logging_type = args.logging_type

        if tm == 'd':
            tf = cfg.DAY_TIMEFRAME
        elif tm == 'w':
            tf = cfg.WEEK_TIMEFRAME
        elif tm == 'm':
            tf = cfg.MONTH_TIMEFRAME
        else:
            tf = cfg.ALL_TIME
        conf_path = '{}/watchman.conf'.format(os.path.expanduser('~'))

        if not validate_conf(conf_path):
            raise Exception(
                colored('GITLAB_WATCHMAN_TOKEN environment variable or watchman.conf file not detected. '
                        '\nEnsure environment variable is set or a valid file is located in your home '
                        'directory: {} ', 'red')
                .format(os.path.expanduser('~')))
        else:
            config = validate_conf(conf_path)
            connection = gitlab.initiate_gitlab_connection()

        if logging_type:
            if logging_type == 'file':
                if os.environ.get('GITLAB_WATCHMAN_LOG_PATH'):
                    OUTPUT_LOGGER = logger.FileLogger(os.environ.get('GITLAB_WATCHMAN_LOG_PATH'))
                elif config.get('logging').get('file_logging').get('path') and \
                        os.path.exists(config.get('logging').get('file_logging').get('path')):
                    OUTPUT_LOGGER = logger.FileLogger(log_path=config.get('logging').get('file_logging').get('path'))
                else:
                    print('No config given, outputting gitlab_watchman.log file to home path')
                    OUTPUT_LOGGER = logger.FileLogger(log_path=os.path.expanduser('~'))
            elif logging_type == 'stdout':
                OUTPUT_LOGGER = logger.StdoutLogger()
            elif logging_type == 'stream':
                if os.environ.get('GITLAB_WATCHMAN_HOST') and os.environ.get('GITLAB_WATCHMAN_PORT'):
                    OUTPUT_LOGGER = logger.SocketJSONLogger(os.environ.get('GITLAB_WATCHMAN_HOST'),
                                                            os.environ.get('GITLAB_WATCHMAN_PORT'))
                elif config.get('logging').get('json_tcp').get('host') and \
                        config.get('logging').get('json_tcp').get('port'):
                    OUTPUT_LOGGER = logger.SocketJSONLogger(config.get('logging').get('json_tcp').get('host'),
                                                            config.get('logging').get('json_tcp').get('port'))
                else:
                    raise Exception("JSON TCP stream selected with no config")
            else:
                OUTPUT_LOGGER = logger.CSVLogger()
        else:
            print('No logging option selected, defaulting to CSV')
            OUTPUT_LOGGER = logger.CSVLogger()

        now = int(time.time())
        today = date.today().strftime('%Y-%m-%d')
        start_date = time.strftime('%Y-%m-%d', time.localtime(now - tf))

        if not isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
            print = builtins.print
            print(colored('''
              #####          #                                       
             #     # # ##### #         ##   #####                    
             #       #   #   #        #  #  #    #                   
             #  #### #   #   #       #    # #####                    
             #     # #   #   #       ###### #    #                   
             #     # #   #   #       #    # #    #                   
              #####  #   #   ####### #    # #####                    
                                                                     
             #     #                                                 
             #  #  #   ##   #####  ####  #    # #    #   ##   #    # 
             #  #  #  #  #    #   #    # #    # ##  ##  #  #  ##   # 
             #  #  # #    #   #   #      ###### # ## # #    # # #  # 
             #  #  # ######   #   #      #    # #    # ###### #  # # 
             #  #  # #    #   #   #    # #    # #    # #    # #   ## 
              ## ##  #    #   #    ####  #    # #    # #    # #    # 
                                                                 ''', 'magenta'))
            print('Version: {}\n'.format(a.__version__))
            print('Searching from {} to {}'.format(start_date, today))
            print('Importing rules...')
            rules_list = load_rules()
            print('{} rules loaded'.format(len(rules_list)))
        else:
            OUTPUT_LOGGER.log_info('GitLab Watchman started execution')
            OUTPUT_LOGGER.log_info('Version: {}'.format(a.__version__))
            OUTPUT_LOGGER.log_info('Importing rules...')
            rules_list = load_rules()
            OUTPUT_LOGGER.log_info('{} rules loaded'.format(len(rules_list)))
            print = OUTPUT_LOGGER.log_info

        if everything:
            print(colored('Getting everything...', 'magenta'))
            for rule in rules_list:
                if 'blobs' in rule.get('scope'):
                    search(connection, rule, tf, 'blobs')
                if 'commits' in rule.get('scope'):
                    search(connection, rule, tf, 'commits')
                if 'issues' in rule.get('scope'):
                    search(connection, rule, tf, 'issues')
                if 'merge_requests' in rule.get('scope'):
                    search(connection, rule, tf, 'merge_requests')
                if 'wiki_blobs' in rule.get('scope'):
                    search(connection, rule, tf, 'wiki_blobs')
                if 'milestones' in rule.get('scope'):
                    search(connection, rule, tf, 'milestones')
        else:
            if blobs:
                print(colored('Searching blobs', 'magenta'))
                for rule in rules_list:
                    if 'blobs' in rule.get('scope'):
                        search(connection, rule, tf, 'blobs')
            if commits:
                print(colored('Searching commits', 'magenta'))
                for rule in rules_list:
                    if 'commits' in rule.get('scope'):
                        search(connection, rule, tf, 'commits')
            if issues:
                print(colored('Searching issues', 'magenta'))
                for rule in rules_list:
                    if 'issues' in rule.get('scope'):
                        search(connection, rule, tf, 'issues')
            if merge:
                print(colored('Searching merge requests', 'magenta'))
                for rule in rules_list:
                    if 'merge_requests' in rule.get('scope'):
                        search(connection, rule, tf, 'merge_requests')
            if wiki:
                print(colored('Searching wiki blobs', 'magenta'))
                for rule in rules_list:
                    if 'wiki_blobs' in rule.get('scope'):
                        search(connection, rule, tf, 'wiki_blobs')
            if milestones:
                print(colored('Searching milestones', 'magenta'))
                for rule in rules_list:
                    if 'milestones' in rule.get('scope'):
                        search(connection, rule, tf, 'milestones')
        print(colored('++++++Audit completed++++++', 'green'))

        deinit()

    except Exception as e:
        if isinstance(OUTPUT_LOGGER, logger.StdoutLogger):
            print = OUTPUT_LOGGER.log_critical
        else:
            print = builtins.print

        print(colored(e, 'red'))


if __name__ == '__main__':
    main()
