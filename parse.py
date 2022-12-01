import os
import sys
import traceback
from datetime import datetime

import click

from common.logging import get_logger
from common.utils import (get_driver, notification_hook, parse_pages_string,
                          reactions_to_csv, save_run_info)
from config.logging import get_logging_config
from config.parser import get_parser_config
from config.storage import get_storage_config
from pages.login_page import LoginPage
from pages.results_page import ResultsPage
from storage.cloud_storage import CloudStorage
from storage.local_storage import LocalStorage

logger = get_logger(get_logging_config())


@click.command()
@click.option('--pages', 'pages_string', required=True)
@click.option('--url-template', required=True)
@click.option('--headless', default=False, is_flag=True)
def parse(pages_string, url_template, headless):
    parser_config = get_parser_config()
    storage_config = get_storage_config()

    if not os.path.isdir(parser_config.dirname):
        os.mkdir(parser_config.dirname)

    local_storage = LocalStorage(storage_config.local_storage_config)
    cloud_storage = CloudStorage(storage_config.cloud_storage_config)

    pages = parse_pages_string(pages_string)

    logger.info('Url template: {0}'.format(url_template))
    logger.info('Pages string: {0}'.format(pages_string))
    logger.info('Pages: {0}'.format(pages))
    logger.info('Headless mode: {0}'.format(headless))

    driver = get_driver(headless)

    login_page = LoginPage(
        driver, parser_config.timeout, parser_config.poll_frequency,
    )
    results_page = ResultsPage(
        driver, parser_config.timeout, parser_config.poll_frequency,
    )

    start_datetime = datetime.now()

    logger.info('Navigating to the start url...')
    driver.get(url_template.format(page=pages[0]))

    logger.info('Filling out the login form...')
    login_page.login(parser_config.username, parser_config.password)

    parsed_pages, failed_pages = [], []
    for page in pages:
        if page != pages[0]:
            driver.get(url_template.format(page=page))
        logger.info('Parsing page {page}...'.format(page=page))
        try:
            reactions = results_page.parse(
                parser_config.page_size, parser_config.subpage_size,
            )
        except Exception:
            failed_pages.append(page)
            error_message = traceback.format_exc()
            logger.error(
                'An error occurred while parsing page {page}'.format(
                    page=page,
                ),
            )
            logger.error(error_message)
        else:
            logger.info('Saving data from page {page}...'.format(page=page))

            filename = '{page}.tsv'.format(page=page)

            local_filepath = local_storage.save(
                filename, reactions_to_csv(reactions, '\t'),
            )
            logger.info('Saved data locally...')
            logger.info('Local filepath: {0}'.format(local_filepath))

            cloud_filepath = cloud_storage.upload(
                local_storage.get_filepath(filename),
            )
            logger.info('Uploaded data to the cloud...')
            logger.info('Cloud filepath: {0}'.format(cloud_filepath))

            parsed_pages.append(page)

        save_run_info(
            os.path.join(
                parser_config.dirname,
                parser_config.filename,
            ),
            pages,
            parsed_pages,
            failed_pages,
        )

    finish_datetime = datetime.now()

    run_info = [
        '<b>RUN INFO</b>',
        'Parsed pages number: {0}'.format(len(parsed_pages)),
        'Failed pages number: {0}'.format(len(failed_pages)),
        'Start date: {0}'.format(
            start_datetime.strftime('%m.%d.%Y %H:%M:%S'),
        ),
        'Finish date: {0}'.format(
            finish_datetime.strftime('%m.%d.%Y %H:%M:%S'),
        ),
        'Elapsed time: {0}'.format(finish_datetime - start_datetime),
    ]

    logger.critical('\n'.join(run_info))
    logger.info('Parsed pages: {0}'.format(parsed_pages))
    logger.info('Failed pages: {0}'.format(failed_pages))

    driver.quit()


if __name__ == '__main__':
    sys.excepthook = notification_hook
    parse()
