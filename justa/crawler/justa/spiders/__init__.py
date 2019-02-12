from scrapy import Spider
from selenium import webdriver
from splinter.driver.webdriver import WebDriverElement
from splinter.driver.webdriver.remote import WebDriver

from justa.settings import SELENIUM_DRIVE_URL


class RemoteWebDriver(WebDriver):
    """A clone of the default remote web driver class, but using the non-remote
    web driver element class. More details on this specific need:
    https://github.com/cobrateam/splinter/issues/674 """

    def __init__(self, *args, **kwargs):
        super(RemoteWebDriver, self).__init__(*args, **kwargs)
        self.element_class = WebDriverElement  # overrides the element class


class SeleniumSpider(Spider):

    preferences = None

    def __init__(self, headless=True, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)
        # If using "scrapy craw -a headless=true" we must parse the string
        self.headless = str(headless).lower() == "true"
        self.browser = RemoteWebDriver(
            browser="chrome",
            url=SELENIUM_DRIVE_URL,
            options=self.get_browser_options(),
            headless=self.headless,
        )

    def get_browser_options(self):
        if self.preferences is None:
            return None
        else:
            options = webdriver.ChromeOptions()
            options.add_experimental_option("prefs", self.preferences)
            return options
