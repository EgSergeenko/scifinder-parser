import logging
from datetime import datetime
from functools import cache

from config.base import BaseConfig


class BaseLoggingConfig(BaseConfig):
    level: int = logging.INFO
    format: str = '[{asctime}] - [{levelname}] - {message}'


class StreamHandlerConfig(BaseLoggingConfig):
    pass


class FileHandlerConfig(BaseLoggingConfig):
    dirname: str = 'log'
    filename: str = '{0}.txt'.format(
        datetime.now().strftime('%m_%d_%Y__%H_%M_%S'),
    )


class RequestsHandlerConfig(BaseLoggingConfig):
    level: int = logging.CRITICAL
    format: str = '{message}'
    url_template: str = 'https://api.telegram.org/bot{token}/sendMessage'
    log_token: str
    chat_id: str


class LoggingConfig(BaseLoggingConfig):
    stream_handler_config: StreamHandlerConfig
    file_handler_config: FileHandlerConfig
    requests_handler_config: RequestsHandlerConfig


@cache
def get_logging_config():
    return LoggingConfig(
        stream_handler_config=StreamHandlerConfig(),
        file_handler_config=FileHandlerConfig(),
        requests_handler_config=RequestsHandlerConfig(),
    )
