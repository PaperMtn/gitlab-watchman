import json
import dataclasses
import logging
import sys
import logging.handlers
from logging import Logger


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class LoggingBase(Logger):
    def __init__(self, name='Slack Watchman Enterprise'):
        super().__init__(name)
        self.notify_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "NOTIFY", "scope": "%(scope)s", "severity": '
            '"%(severity)s", "detection_type": "%(type)s", "detection_data": %(message)s}')
        self.info_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
        self.critical_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)


class StdoutLogger(LoggingBase):
    def __init__(self):
        LoggingBase.__init__(self)
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.handler)

    def log_notification(self,
                         log_data: str or dict,
                         scope: str = None,
                         detect_type: str = None,
                         severity: int = None):
        self.handler.setFormatter(self.notify_format)
        self.logger.warning(json.dumps(log_data, cls=EnhancedJSONEncoder),
                            extra={
                                'scope': scope,
                                'type': detect_type,
                                'severity': severity
                            })

    def log_info(self, log_data: str or dict):
        self.handler.setFormatter(self.info_format)
        self.logger.info(log_data)

    def log_critical(self, log_data: str or dict):
        self.handler.setFormatter(self.critical_format)
        self.logger.critical(log_data)
