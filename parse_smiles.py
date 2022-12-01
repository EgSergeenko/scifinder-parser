import sys

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
def parse_smiles(input_filepath, output_filepath, headless):
    parser_config = get_parser_config()

    start_url = 'https://scifinder-n.cas.org'

    logger.info('Input filepath: {0}'.format(input_filepath))
    logger.info('Output filepath: {0}'.format(output_filepath))
    logger.info('Headless mode: {0}'.format(headless))
    logger.info('Url template: {0}'.format(start_url))

    driver = get_driver(headless)

    login_page = LoginPage(
        driver, parser_config.timeout, parser_config.poll_frequency,
    )
    search_page = SearchPage(
        driver, parser_config.timeout, parser_config.poll_frequency,
    )
    substance_page = SubstancePage(
        driver, parser_config.timeout, parser_config.poll_frequency,
    )

    logger.info('Navigating to the start url...')
    driver.get(start_url)

    logger.info('Filling out the login form...')
    login_page.login(parser_config.username, parser_config.password)

    df = pd.read_csv(input_filepath)
    results = []

    for idx, cas_number in enumerate(df['query']):
        logger.info(
            '{0}/{1}... Parsing smiles for {2}'.format(
                idx + 1, len(df['query']), cas_number,
            ),
        )
        single_result = search_page.search_substance(
            cas_number, first_page=idx == 0,
        )
        result = 'Multiple results'
        if single_result:
            result = substance_page.parse_smiles()
        results.append(result)

    df['result'] = results
    df.to_csv(output_filepath, index=False)

    logger.info('Saved data locally...')
    logger.info('Local filepath: {0}'.format(output_filepath))

    run_info = [
        '<b>RUN INFO</b>',
        'parse_smiles.py execution has finished',
    ]

    logger.critical('\n'.join(run_info))

    driver.quit()


if __name__ == '__main__':
    sys.excepthook = notification_hook
    parse_smiles()
