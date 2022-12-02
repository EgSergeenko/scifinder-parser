from datetime import datetime

from config.base import BaseConfig


class ParserConfig(BaseConfig):
    page_size: int = 20
    subpage_size: int = 50
    username: str
    password: str
    timeout: float = 30.0
    poll_frequency: float = 0.1
    dirname: str = 'runs'
    filename: str = '{0}.txt'.format(
        datetime.now().strftime('%m_%d_%Y__%H_%M_%S'),
    )
    n_retries: int = 5


def get_parser_config():
    return ParserConfig()
