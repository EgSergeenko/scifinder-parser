from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SearchPage(BasePage):
    SEARCH_INPUT = (By.CLASS_NAME, 'search-input')
    SEARCH_BUTTON = (By.ID, 'submit-search-button')
    SUBSTANCE_LINK = (By.CLASS_NAME, 'substance-rn-partial')
    LOADING_OVERLAY = (By.CLASS_NAME, 'loading-overlay')
    SEARCH_TYPE_BUTTON = (By.ID, 'result-type-substance')

    def search_substance(self, query, first_page=False):
        if first_page:
            try:
                self.wait_element(self.LOADING_OVERLAY)
            except TimeoutException:
                pass
            self.wait_element_invisibility(self.LOADING_OVERLAY)
            self.click(self.SEARCH_TYPE_BUTTON)
        self.clear(self.SEARCH_INPUT)
        self.fill_text_input(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        self.wait_element(self.SUBSTANCE_LINK)
        single_result = len(self.find_elements(self.SUBSTANCE_LINK)) == 1
        self.click(self.SUBSTANCE_LINK)
        return single_result
