from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'password')
    CONTINUE_BUTTON = (By.ID, 'continueButton')
    LOGIN_BUTTON = (By.ID, 'loginButton')

    def login(self, username, password):
        self.fill_text_input(self.USERNAME_INPUT, username)
        self.click(self.CONTINUE_BUTTON)
        self.fill_text_input(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
