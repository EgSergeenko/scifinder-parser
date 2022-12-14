import sys
import traceback

import click
import pandas as pd

from common.logging import get_logger
from common.utils import get_driver, notification_hook
from config.logging import get_logging_config
from config.parser import get_parser_config
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.substance_page import SubstancePage

logger = get_logger(get_logging_config())


@click.command()
@click.argument('input-filepath', type=click.Path(exists=True))
@click.argument('output-filepath', type=click.Path())
@click.option('--headless', default=False, is_flag=True)
@click.option('--browser', default='chrome')
def parse_smiles(input_filepath, output_filepath, headless, browser):
    parser_config = get_parser_config()

    start_url = 'https://scifinder-n.cas.org'

    logger.info('Input filepath: {0}'.format(input_filepath))
    logger.info('Output filepath: {0}'.format(output_filepath))
    logger.info('Browser: {0}'.format(browser))
    logger.info('Headless mode: {0}'.format(headless))
    logger.info('Url template: {0}'.format(start_url))

    driver = get_driver(browser, headless)

    login_page = LoginPage(
        driver,
        parser_config.timeout,
        parser_config.poll_frequency,
        parser_config.n_retries,
    )
    search_page = SearchPage(
        driver,
        parser_config.timeout,
        parser_config.poll_frequency,
        parser_config.n_retries,
    )
    substance_page = SubstancePage(
        driver,
        parser_config.timeout,
        parser_config.poll_frequency,
        parser_config.n_retries,
    )

    logger.info('Navigating to the start url...')
    driver.get(start_url)

    logger.info('Filling out the login form...')
    login_page.login(parser_config.username, parser_config.password)

    df = pd.read_csv(input_filepath)

    write_line(output_filepath, 'query', 'result', 'comment')

    for idx, query in enumerate(df['query']):
        logger.info(
            '{0}/{1}... Parsing smiles for {2}'.format(
                idx + 1, len(df['query']), query,
            ),
        )
        try:
            single_result = search_page.search_substance(
                query, first_page=idx == 0,
            )
        except Exception:
            result = ''
            error_message = traceback.format_exc()
            logger.error('An error occurred while searching a substance')
            logger.error(error_message)
            logger.info('Navigating to the start url...')
            driver.get(start_url)
            write_line(output_filepath, query, result, 'Error')
            continue

        comment, result = '', ''
        if not single_result:
            comment = 'Multiple results'

        try:
            result = substance_page.parse_smiles()
        except Exception:
            comment = 'Error'
            error_message = traceback.format_exc()
            logger.error('An error occurred while parsing SMILES')
            logger.error(error_message)
            logger.info('Navigating to the start url...')
            driver.get(start_url)

        if result == 'Not found':
            comment, result = result, ''

        write_line(output_filepath, query, result, comment)

    run_info = [
        '<b>RUN INFO</b>',
        'parse_smiles.py execution has finished',
    ]

    logger.critical('\n'.join(run_info))

    driver.quit()


def write_line(output_filepath, query, result, comment):
    with open(output_filepath, 'a') as output_file:
        output_file.write(
            '{0}{1}'.format(
                ','.join([query, result, comment]), '\n',
            ),
        )


if __name__ == '__main__':
    sys.excepthook = notification_hook
    parse_smiles()
