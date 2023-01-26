import json
import string
import traceback
from dataclasses import asdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from common.logging import get_logger
from config.logging import get_logging_config

logger = get_logger(get_logging_config())


def clean_text(text):
    return ' '.join(text.split())


def get_xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '{0}[{1}]'.format(
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child),
            ),
        )
        child = parent
    components.reverse()
    return '/{0}'.format('/'.join(components))


def get_driver(browser, headless):
    if browser == 'chrome':
        options = ChromeOptions()
    elif browser == 'firefox':
        options = FirefoxOptions()
    else:
        raise ValueError('Unsupported browser: {0}'.format(browser))
    if headless:
        options.add_argument('--headless')
    if browser == 'chrome':
        driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager().install(),
            ),
            options=options,
        )
    else:
        driver = webdriver.Firefox(
            service=FirefoxService(
                GeckoDriverManager().install(),
            ),
            options=options,
        )
    driver.maximize_window()
    return driver


def reactions_to_json(reactions, filepath):
    reactions_data = [asdict(reaction) for reaction in reactions]
    with open(filepath, 'w') as output_file:
        json.dump(
            reactions_data,
            output_file,
            ensure_ascii=False,
            indent=4,
        )


def save_run_info(
        filepath, pages, parsed_pages, failed_pages,
):
    run_info = [
        'Pages: {0}'.format(pages),
        'Parsed pages: {0}'.format(parsed_pages),
        'Failed pages: {0}'.format(failed_pages),
    ]
    with open(filepath, 'w') as output_file:
        output_file.writelines('\n'.join(run_info))


def reactions_to_csv(reactions, delimiter):
    reactions.sort(key=lambda row: -row.stages_number)
    max_stages_number = reactions[0].stages_number
    stages_header = []
    for stage in range(1, max_stages_number + 1):
        stages_header.append(
            delimiter.join(
                [
                    'reagents_{stage}'.format(stage=stage),
                    'catalysts_{stage}'.format(stage=stage),
                    'solvents_{stage}'.format(stage=stage),
                    'other_conditions_{stage}'.format(stage=stage),
                ],
            ),
        )
    header = delimiter.join(
        [
            'reaction_id',
            'reactants',
            'products',
            'stages_number',
            'yield_value',
            'reference_title',
            'authors',
            'bibliography',
            delimiter.join(stages_header),
        ],
    )
    lines = [reaction.to_csv(delimiter) for reaction in reactions]
    lines.insert(0, header)
    return lines


def notification_hook(exc_type, value, tb):
    error_message = ''.join(
        traceback.format_exception(
            exc_type, value, tb,
        ),
    )
    error_info = [
        '<b>ERROR</b>',
        exc_type.__name__,
    ]
    logger.critical('\n'.join(error_info))
    logger.error(error_message)


def parse_pages_string(pages_string):
    allowed_chars = {',', '-', *string.digits}
    cleaned_string = []
    for char in pages_string:
        if char in allowed_chars:
            cleaned_string.append(char)
    page_groups = ''.join(cleaned_string).split(',')
    pages = set()
    for page_group in page_groups:
        pages_range = page_group.split('-')
        if len(pages_range) == 1:
            pages.add(int(pages_range[0]))
        elif len(pages_range) == 2:
            for page in range(int(pages_range[0]), int(pages_range[1]) + 1):
                pages.add(page)
    return sorted(pages)


def write_line(output_filepath, query, result, comment, delimiter='\t'):
    with open(output_filepath, 'a') as output_file:
        output_file.write(
            '{0}{1}'.format(
                delimiter.join([query, result, comment]), '\n',
            ),
        )
