from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SubstancePage(BasePage):
    EXPAND_BUTTON = (By.CLASS_NAME, 'panel-heading')

    def parse_smiles(self):
        self.click(self.EXPAND_BUTTON)
        page_source = self.get_page_source()
        smiles_component = page_source.find(
            'div', {'class': 'smiles-text'},
        )
        if smiles_component is None:
            return 'Not found'
        return smiles_component.get_text()
