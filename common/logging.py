import logging
import os

import requests

LOG_FORMAT = '[{asctime}] - [{levelname}] - {message}'


class RequestsHandler(logging.Handler):
    def __init__(self, config):
        super().__init__()
        self.url_template = config.url_template
        self.token = config.log_token
        self.chat_id = config.chat_id

    def emit(self, record):
        message = self.format(record)
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML',
        }
        requests.post(
            self.url_template.format(token=self.token),
            data=payload,
        )


def get_stream_handler(config):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(config.level)
    stream_handler.setFormatter(
        logging.Formatter(config.format, style='{'),
    )
    return stream_handler


def get_file_handler(config):
    if not os.path.isdir(config.dirname):
        os.mkdir(config.dirname)
    filepath = os.path.join(
        config.dirname, config.filename,
    )
    file_handler = logging.FileHandler(filepath)
    file_handler.setLevel(config.level)
    file_handler.setFormatter(
        logging.Formatter(config.format, style='{'),
    )
    return file_handler


def get_requests_handler(config):
    requests_handler = RequestsHandler(config)
    requests_handler.setLevel(config.level)
    requests_handler.setFormatter(
        logging.Formatter(config.format, style='{'),
    )
    return requests_handler


def get_logger(logging_config):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        logger.addHandler(
            get_file_handler(logging_config.file_handler_config),
        )
        logger.addHandler(
            get_stream_handler(logging_config.stream_handler_config),
        )
        logger.addHandler(
            get_requests_handler(logging_config.requests_handler_config),
        )
    return logger
