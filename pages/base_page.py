import time

from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common.expected_conditions import visibility_of_elements_located


class BasePage(object):
    def __init__(
        self,
        driver,
        timeout,
        poll_frequency,
        page_source_delay=3.0,
    ):
        self._driver = driver
        self._wait = WebDriverWait(
            self._driver,
            timeout,
            poll_frequency,
        )
        self.page_source_delay = page_source_delay

    def click(self, locator):
        element = self._wait.until(
            expected_conditions.element_to_be_clickable(locator),
        )
        element.click()

    def clear(self, locator):
        element = self._wait.until(
            expected_conditions.element_to_be_clickable(locator),
        )
        element.clear()

    def fill_text_input(self, locator, input_value):
        element = self._wait.until(
            expected_conditions.element_to_be_clickable(locator),
        )
        element.send_keys(input_value)

    def escape(self):
        ActionChains(self._driver).send_keys(Keys.ESCAPE).perform()

    def wait_element(self, locator):
        self._wait.until(
            expected_conditions.visibility_of_element_located(locator),
        )

    def wait_elements(self, locator, number=0):
        self._wait.until(
            visibility_of_elements_located(locator, number),
        )

    def wait_element_invisibility(self, locator):
        self._wait.until(
            expected_conditions.invisibility_of_element_located(locator),
        )

    def find_element(self, locator):
        return self._wait.until(
            expected_conditions.visibility_of_element_located(locator),
        )

    def find_elements(self, locator, number=0):
        return self._wait.until(
            visibility_of_elements_located(locator, number),
        )

    def get_page_source(self, no_delay=False):
        if not no_delay:
            time.sleep(self.page_source_delay)
        return BeautifulSoup(
            self._driver.page_source, 'html.parser',
        )

    def forward(self):
        self._driver.forward()

    def back(self):
        self._driver.back()

    def go_to(self, url):
        self._driver.get(url)

    def get_current_url(self):
        return self._driver.current_url
