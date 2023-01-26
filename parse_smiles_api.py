import re
import sys
import traceback
from http import HTTPStatus

import click
import pandas as pd
import requests

from common.logging import get_logger
from common.utils import write_line, notification_hook
from config.logging import get_logging_config

logger = get_logger(get_logging_config())


@click.command()
@click.argument('input-filepath', type=click.Path(exists=True))
@click.argument('output-filepath', type=click.Path())
def parse_smiles_api(input_filepath, output_filepath):

    base_url = 'https://commonchemistry.cas.org/api'

    logger.info('Input filepath: {0}'.format(input_filepath))
    logger.info('Output filepath: {0}'.format(output_filepath))

    df = pd.read_csv(input_filepath, delimiter='\t')

    write_line(output_filepath, 'query', 'result', 'comment')

    cas_number_pattern = re.compile('([0-9]+-)+[0-9]+')

    for idx, query in enumerate(df['query']):

        if idx % 100 == 0:
            logger.info(
                '{0}/{1}... Parsing smiles for {2}'.format(
                    idx + 1, len(df['query']), query,
                ),
            )

        search_comment = ''
        if cas_number_pattern.match(query):
            cas_number = query
        else:
            url = '{0}/search?q={1}'.format(
                base_url, query,
            )
            cas_number, search_comment = search_substance(url)

        if search_comment not in {'Not found', 'Error'}:
            url = '{0}/detail?cas_rn={1}'.format(
                base_url, cas_number,
            )
            result, comment = get_substance(url)
        else:
            result, comment = '', search_comment

        if not comment and search_comment:
            comment = search_comment

        write_line(output_filepath, query, result, comment)


def search_substance(url):
    cas_number, comment = '', 'Error'
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        error_message = traceback.format_exc()
        logger.error('An error occurred while getting searching substance')
        logger.error(error_message)
        return cas_number, comment

    if response.ok:
        data = response.json()
        if data['count'] == 0:
            comment = 'Not found'
        else:
            cas_number, comment = data['results'][0]['rn'], ''
            if data['count'] > 1:
                comment = 'Multiple results'
    elif response.status_code == HTTPStatus.NOT_FOUND:
        comment = 'Not found'
    return cas_number, comment


def get_substance(url):
    result, comment = '', 'Error'
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        error_message = traceback.format_exc()
        logger.error('An error occurred while getting substance details')
        logger.error(error_message)
        return result, comment

    if response.ok:
        data = response.json()
        if 'smile' in data:
            result, comment = data['smile'], ''
        else:
            comment = 'Not found'
    elif response.status_code == HTTPStatus.NOT_FOUND:
        comment = 'Not found'
    return result, comment


if __name__ == '__main__':
    sys.excepthook = notification_hook
    parse_smiles_api()
