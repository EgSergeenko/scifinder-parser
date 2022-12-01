from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SubstancePage(BasePage):
    EXPAND_BUTTON = (By.CLASS_NAME, 'panel-heading')

    def parse_smiles(self):
        self.click(self.EXPAND_BUTTON)
        page_source = self.get_page_source(no_delay=True)
        return page_source.find(
            'div', {'class': 'smiles-text'},
        ).get_text()
