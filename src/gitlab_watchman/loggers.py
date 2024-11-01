import json
import dataclasses
import logging
import os
import sys
import logging.handlers
import re
import traceback
import csv
from logging import Logger
from typing import Any, Dict, List, ClassVar, Protocol
from colorama import Fore, Back, Style, init


class StdoutLogger:
    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug')
        self.print_header()
        init()

    def log(self,
            mes_type: str,
            message: Any,
            **kwargs) -> None:

        notify_type = kwargs.get('notify_type')
        scope = kwargs.get('scope')

        if not self.debug and mes_type == 'DEBUG':
            return

        if dataclasses.is_dataclass(message):
            message = dataclasses.asdict(message)

        if notify_type == "instance":
            message = f'GITLAB_INSTANCE: \n' \
                      f'    VERSION: {message.get("version")}  \n' \
                      f'    REVISION: {message.get("revision")}  \n' \
                      f'    KUBERNETES_SERVER: \n' \
                      f'        ENABLED: {message.get("kas").get("enabled")}  \n' \
                      f'        URL: {message.get("kas").get("externalUrl")}  \n'\
                      f'        VERSION: {message.get("kas").get("version")}  \n' \
                      f'    ENTERPRISE: {message.get("enterprise")}'
            mes_type = 'INSTANCE'
        if notify_type == "user":
            message = f'USER: \n' \
                      f'    ID: {message.get("id")}  \n' \
                      f'    NAME: {message.get("name")}  \n' \
                      f'    USERNAME: {message.get("username")}  \n' \
                      f'    COMMIT_EMAIL: {message.get("email")}  \n' \
                      f'    CREATED_AT: {message.get("created_at")} \n' \
                      f'    ADMIN: {message.get("is_admin", False)} \n' \
                      f'    BOT_USER: {message.get("bot")} \n' \
                      f'    CAN_CREATE_GROUP: {message.get("can_create_group")} \n'\
                      f'    CAN_CREATE_PROJECT: {message.get("can_create_project")} \n' \
                      f'    2FA_ENABLED: {message.get("two_factor_enabled")}'
            mes_type = 'USER'
        if notify_type == "token":
            message = f'PERSONAL_ACCESS_TOKEN: \n' \
                      f'    ID: {message.get("id")}  \n' \
                      f'    NAME: {message.get("name")}  \n' \
                      f'    REVOKED: {message.get("revoked")}  \n' \
                      f'    CREATED_AT: {message.get("created_at")} \n' \
                      f'    SCOPES: {message.get("scopes", False)} \n' \
                      f'    LAST_USED_AT: {message.get("last_used_at")} \n' \
                      f'    ACTIVE: {message.get("active")} \n'\
                      f'    EXPIRY: {message.get("expires_at", "Never")}'
            mes_type = 'WARNING'
        if notify_type == "result":
            if scope == 'blobs':
                message = 'SCOPE: Blob' \
                          f'    AUTHOR: {message.get("commit").get("author_name")} - ' \
                          f'{message.get("commit").get("author_email")}' \
                          f'    COMMITTED: {message.get("commit").get("committed_date")} \n' \
                          f'    FILENAME: {message.get("blob").get("basename")} \n' \
                          f'    URL: {message.get("project").get("web_url")}/-/blob/{message.get("blob").get("ref")}/' \
                          f'{message.get("blob").get("filename")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'merge_requests':
                message = 'SCOPE: Merge Request' \
                          f'    AUTHOR: {message.get("merge_request").get("author").get("name")} ' \
                          f'    CREATED: {message.get("merge_request").get("created_at")} \n' \
                          f'    URL: {message.get("merge_request").get("web_url")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'commits':
                message = 'SCOPE: Commit' \
                          f'    AUTHOR: {message.get("commit").get("author_name")} - ' \
                                f'{message.get("commit").get("author_email")}' \
                          f'    CREATED: {message.get("commit").get("created_at")} \n' \
                          f'    URL: {message.get("commit").get("web_url")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'milestones':
                message = 'SCOPE: Milestones' \
                          f'    TITLE: {message.get("milestone").get("title")} ' \
                          f'    CREATED: {message.get("milestone").get("created_at")} \n' \
                          f'    URL: {message.get("milestone").get("web_url")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'wiki_blobs':
                message = 'SCOPE: Wiki Blob' \
                          f'    FILENAME: {message.get("wiki_blob").get("filename")} \n' \
                          f'    URL: {message.get("project").get("web_url")}/-/wikis/' \
                          f'{message.get("wiki_blob").get("basename")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'issues':
                message = 'SCOPE: Issue' \
                          f'    AUTHOR: {message.get("issue").get("author").get("username")} '\
                          f'    CREATED: {message.get("issue").get("created_at")} \n' \
                          f'    URL: {message.get("issue").get("web_url")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'notes':
                message = 'SCOPE: Note' \
                          f'    AUTHOR: {message.get("note").get("author").get("username")}'\
                          f'    CREATED: {message.get("note").get("created_at")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'snippet_titles':
                message = 'SCOPE: Snippet' \
                          f'    AUTHOR: {message.get("snippet").get("author").get("username")} '\
                          f'    CREATED: {message.get("snippet").get("created_at")} \n' \
                          f'    URL: {message.get("snippet").get("web_url")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            mes_type = 'RESULT'
        try:
            self.log_to_stdout(message, mes_type)
        except Exception as e:
            print(e)
            self.log_to_stdout(message, mes_type)

    def log_to_stdout(self,
                      message: Any,
                      mes_type: str) -> None:

        try:

            reset_all = Style.NORMAL + Fore.RESET + Back.RESET
            key_color = Fore.WHITE
            base_color = Fore.WHITE
            high_color = Fore.WHITE
            style = Style.NORMAL

            if mes_type == "NOTIFY":
                base_color = Fore.CYAN
                high_color = Fore.CYAN
                key_color = Fore.CYAN
                style = Style.NORMAL
            elif mes_type == 'INFO':
                base_color = Fore.WHITE
                high_color = Fore.WHITE
                key_color = Fore.WHITE
                style = Style.DIM
                mes_type = '-'
            elif mes_type == 'INSTANCE':
                base_color = Fore.LIGHTBLUE_EX
                high_color = Fore.LIGHTBLUE_EX
                key_color = Fore.LIGHTBLUE_EX
                style = Style.NORMAL
                mes_type = '+'
            elif mes_type == 'USER':
                base_color = Fore.RED
                high_color = Fore.RED
                key_color = Fore.RED
                style = Style.NORMAL
                mes_type = '+'
            elif mes_type == 'WARNING':
                base_color = Fore.YELLOW
                high_color = Fore.YELLOW
                key_color = Fore.YELLOW
                style = Style.NORMAL
                mes_type = '!'
            elif mes_type == "SUCCESS":
                base_color = Fore.LIGHTGREEN_EX
                high_color = Fore.LIGHTGREEN_EX
                key_color = Fore.LIGHTGREEN_EX
                style = Style.NORMAL
                mes_type = '>>'
            elif mes_type == "DEBUG":
                base_color = Fore.WHITE
                high_color = Fore.WHITE
                key_color = Fore.WHITE
                style = Style.DIM
                mes_type = '#'
            elif mes_type == "ERROR":
                base_color = Fore.MAGENTA
                high_color = Fore.MAGENTA
                key_color = Fore.MAGENTA
                style = Style.NORMAL
            elif mes_type == "CRITICAL":
                base_color = Fore.RED
                high_color = Fore.RED
                key_color = Fore.RED
                style = Style.NORMAL
            elif mes_type == "RESULT":
                base_color = Fore.LIGHTGREEN_EX
                high_color = Fore.LIGHTGREEN_EX
                key_color = Fore.LIGHTGREEN_EX
                style = Style.NORMAL
                mes_type = '!'

            # Make log level word/symbol coloured
            type_colorer = re.compile(r'([A-Z]{3,})', re.VERBOSE)
            mes_type = type_colorer.sub(high_color + r'\1' + base_color, mes_type.lower())
            # Make header words coloured
            header_words = re.compile('([A-Z_0-9]{2,}:)\s', re.VERBOSE)
            message = header_words.sub(key_color + Style.BRIGHT + r'\1 ' + Fore.WHITE + Style.NORMAL, str(message))
            sys.stdout.write(
                f"{reset_all}{style}[{base_color}{mes_type}{Fore.WHITE}]{style} {message}{Fore.WHITE}{Style.NORMAL}\n")
        except Exception:
            if self.debug:
                traceback.print_exc()
                sys.exit(1)
            print('Formatting error')

    def print_header(self) -> None:
        print(" ".ljust(79) + Style.BRIGHT)

        print(Fore.LIGHTRED_EX + Style.BRIGHT +
              """
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠾⠛⢉⣉⣉⣉⡉⠛⠷⣦⣄⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⣠⣴⣿⣿⣿⣿⣿⡿⣿⣶⣌⠹⣷⡀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣆⠉⠻⣧⠘⣷⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠈⠀⢹⡇⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⠛⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⢸⡇⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⢿⡆⠈⠛⠻⠟⠛⠉⠀⠀⠀⠀⠀⠀⣾⠃⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⡀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠃⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⠿⣦⣄⠀⠀⠀⠀⠀⠀⠀⣀⣴⠟⠁⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣦⠀⠀⠈⠉⠛⠓⠲⠶⠖⠚⠋⠉⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀ ⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """ + Style.RESET_ALL
              )
        print('   GitLab Watchman     ')
        print(Style.DIM + '   Finding exposed secrets and personal data in GitLab      ' + Style.RESET_ALL)
        print('  ')
        print(Style.BRIGHT + '   by PaperMtn - GNU General Public License')
        print(' '.ljust(79) + Fore.GREEN)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class JSONLogger(Logger):
    def __init__(self, name: str = 'gitlab_watchman', **kwargs):
        super().__init__(name)
        self.notify_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "NOTIFY", "scope": "%(scope)s", "severity": '
            '"%(severity)s", "detection_type": "%(type)s", "detection_data": %(message)s}')
        self.info_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')
        self.success_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "SUCCESS", "message": %(message)s}')
        self.instance_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "INSTANCE", "message": %(message)s}')
        self.user_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "USER", "message": %(message)s}')
        self.token_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "TOKEN", "message": %(message)s}')
        self.logger = logging.getLogger(self.name)
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.handler)
        if kwargs.get('debug'):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def log(self,
            level: str,
            log_data: str or Dict,
            **kwargs):
        if level.upper() == 'NOTIFY':
            self.handler.setFormatter(self.notify_format)
            self.logger.info(
                json.dumps(
                    log_data,
                    cls=EnhancedJSONEncoder),
                extra={
                    'scope': kwargs.get('scope', ''),
                    'type': kwargs.get('detect_type', ''),
                    'severity': kwargs.get('severity', '')})
        elif level.upper() == 'INFO':
            self.handler.setFormatter(self.info_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'DEBUG':
            self.handler.setFormatter(self.info_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'SUCCESS':
            self.handler.setFormatter(self.success_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'INSTANCE':
            self.handler.setFormatter(self.instance_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'USER':
            self.handler.setFormatter(self.user_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'TOKEN':
            self.handler.setFormatter(self.token_format)
            self.logger.info(json.dumps(log_data))
        else:
            self.handler.setFormatter(self.info_format)
            self.logger.critical(log_data)


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict]


def log_to_csv(csv_name: str, export_data: List[IsDataclass]) -> None:
    """ Export the data passed in a dataclass to CSV file

    Args:
        csv_name: Name of the CSV file to create
        export_data: Dataclass object to create CSV from
    """
    try:
        headers = dataclasses.asdict(export_data[0]).keys()
        with open(f'{os.path.join(os.getcwd(), csv_name)}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in export_data:
                writer.writerow(dataclasses.asdict(item))
        f.close()
    except Exception as e:
        print(e)
