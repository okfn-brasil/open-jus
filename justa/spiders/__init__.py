from scrapy import Spider
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from justa.settings import SELENIUM_DRIVE_URL


class RemoteSeleniumDriver(webdriver.Remote):

    def wait_for(self, css_selector, timeout=10):
        conditions = (By.CSS_SELECTOR, css_selector)
        expected = expected_conditions.presence_of_element_located(conditions)
        wait = WebDriverWait(self, timeout)
        return wait.until(expected)

    def hover(self, element_or_css):
        element = element_or_css
        if isinstance(element_or_css, str):
            element = self.find_element_by_css_selector(element_or_css)
        ActionChains(self).move_to_element(element).perform()


class SeleniumSpider(Spider):

    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)
        self.browser = RemoteSeleniumDriver(
            command_executor=SELENIUM_DRIVE_URL,
            desired_capabilities=webdriver.DesiredCapabilities.CHROME
        )
