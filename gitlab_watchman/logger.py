import json
import os
import csv
import logging
import socket
import sys
import logging.handlers
from datetime import datetime
from logging import Logger


class CSVLogger(object):
    def __init__(self):
        self.base_out_path = os.getcwd()
        self.headers = {
            'commits': [
                'commit_id',
                'title',
                'data',
                'committed_date',
                'committer_name',
                'committer_email',
                'project_url',
                'project_id',
                'project_name'
            ],
            'milestones': [
                'milestone_id',
                'title',
                'description',
                'created_at',
                'updated_at',
                'due_date',
                'start_date',
                'project_url',
                'project_id',
                'project_name'
            ],
            'issues': [
                'issue_id',
                'title',
                'description',
                'web_url',
                'state',
                'created_at',
                'updated_at',
                'closed_at',
                'author_id',
                'author_username',
                'due_date',
                'confidential',
                'project_url',
                'project_id',
                'project_name',
                'assignee_id',
                'assignee_username'
            ],
            'wiki_blobs': [
                'wiki_blob_id',
                'basename',
                'data',
                'path',
                'project_url',
                'project_id',
                'project_name'
            ],
            'merge_requests': [
                'merge_request_id',
                'title',
                'description',
                'state',
                'created_at',
                'updated_at',
                'author_id',
                'author_username',
                'merge_status',
                'url',
                'project_url',
                'project_id',
                'project_name',
                'assignee_id',
                'assignee_username'
            ],
            'blobs': [
                'blob_id',
                'basename',
                'data',
                'path',
                'project_url',
                'project_id',
                'project_name'
            ],
            'variables': [
                'project_id',
                'project_name'
                'repository_url',
                'last_activity'
            ]
        }

    def write_csv(self, filename, scope, input_list):
        """Writes input list to .csv. The headers and output path are passed as variables"""

        path = '{}/{}_{}.csv'.format(self.base_out_path, filename, scope)

        with open(path, mode='w+', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers.get(scope))
            writer.writeheader()
            for data in input_list:
                writer.writerow(data)

        csv_file.close()
        print('CSV written: {}'.format(path))


class LoggingBase(Logger):
    def __init__(self, name='GitLab Watchman'):
        super().__init__(name)
        self.notify_format = logging.Formatter(
            '{"localtime": "%(asctime)s", "level": "NOTIFY", "source": "%(name)s", "scope": "%(scope)s",'
            ' "severity": "%(severity)s", "detection_type": "%(type)s", "detection_data": %(message)s}')
        self.info_format = logging.Formatter(
            '{"localtime": "%(asctime)s", "level": "%(levelname)s", "source": "%(name)s", "message":'
            ' "%(message)s"}')
        self.log_path = ''
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)


class FileLogger(LoggingBase):
    def __init__(self, log_path):
        LoggingBase.__init__(self)
        self.handler = logging.handlers.WatchedFileHandler(os.path.join(log_path, 'gitlab_watchman.log'))
        self.logger.addHandler(self.handler)

    def log_notification(self, log_data, scope, detect_type, severity):
        self.handler.setFormatter(self.notify_format)
        self.logger.warning(json.dumps(log_data), extra={
            'scope': scope,
            'type': detect_type,
            'severity': severity
        })

    def log_info(self, log_data):
        self.handler.setFormatter(self.info_format)
        self.logger.info(log_data)

    def log_critical(self, log_data):
        self.handler.setFormatter(self.info_format)
        self.logger.critical(log_data)


class StdoutLogger(LoggingBase):
    def __init__(self):
        LoggingBase.__init__(self)
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.handler)

    def log_notification(self, log_data, scope, detect_type, severity):
        self.handler.setFormatter(self.notify_format)
        self.logger.warning(json.dumps(log_data), extra={
            'scope': scope,
            'type': detect_type,
            'severity': severity
        })

    def log_info(self, log_data):
        self.handler.setFormatter(self.info_format)
        self.logger.info(log_data)

    def log_critical(self, log_data):
        self.handler.setFormatter(self.info_format)
        self.logger.critical(log_data)


class SocketJSONLogger(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except socket.error as error:
            print(error)

    def send(self, data):
        try:
            self.sock.sendall(bytes(data, encoding="utf-8"))
        except Exception as e:
            print(e)

    def log_notification(self, log_data, scope, detect_type, severity):
        message = json.dumps({
            'localtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
            'level': 'NOTIFY',
            'source': 'GitLab Watchman',
            'scope': scope,
            'severity': severity,
            'detection_type': detect_type,
            'detection_data': log_data
        }) + '\n'
        self.send(message)

    def log_info(self, log_data):
        message = json.dumps({
            'localtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
            'level': 'INFO',
            'source': 'GitLab Watchman',
            'message': log_data
        }) + '\n'
        self.send(message)

    def log_critical(self, log_data):
        message = json.dumps({
            'localtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
            'level': 'CRITICAL',
            'source': 'GitLab Watchman',
            'message': log_data
        }) + '\n'
        self.send(message)
