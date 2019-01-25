from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from justa.settings import SELENIUM_DRIVE_URL


class RemoteSeleniumDriver(webdriver.Remote):

    def wait_for(self, selector, **kwargs):
        """Explicitly wait for an element described by a CSS selector, using a
        loop to reload the page if the timeout is reached.

        :param selector: (str) CSS selector to find the element

        Optional `kwargs`:
        :param retries: (int) number of retry attempts (default: 10)
        :param reload_method: (callable or None) method be called between
                              timeout and the retry attempt (default: None)
        :param reload_args: (tuple) reload_method arguments (default: (,))
        :param timeout: (int) timeout in seconds (default: 10)
        :param logger: (Spider.logger or None) logger to be used if needed
                       (default: None)
        :error_message: (str) error to be logged if needed (default: '')
        """
        retries = kwargs.get('retries', 10)
        reload_method = kwargs.get('reload_method', None)
        reload_args = kwargs.get('reload_args', tuple())
        timeout = kwargs.get('timeout', 10)
        logger = kwargs.get('logger', None)
        error_message = kwargs.get('error_message', '')

        conditions = (By.CSS_SELECTOR, selector)
        expected = expected_conditions.presence_of_element_located(conditions)
        wait = WebDriverWait(self, timeout)

        try:
            return wait.until(expected)
        except TimeoutException as error:
            retries -= 1
            if not retries:
                if logger:
                    logger.error(error_message)
                raise error

            if reload_method:
                reload_method(*reload_args)

            kwargs = dict(
                retries=retries,
                reload_method=reload_method,
                reload_args=reload_args,
                timeout=timeout,
                logger=logger,
                error_message=error_message
            )
            return self.wait_for(selector, **kwargs)

    def hover(self, element_or_css):
        element = element_or_css
        if isinstance(element_or_css, str):
            element = self.find_element_by_css_selector(element_or_css)
        ActionChains(self).move_to_element(element).perform()

    def css(self, *args, **kwargs):
        """Shortcurt for find_elements_by_css_selector. Returns a single
        element if only one is found, or a sequence of elements if more than
        one is found."""
        elements = self.find_elements_by_css_selector(*args, **kwargs)
        if len(elements) == 1:
            return elements[0]

        return elements


class SeleniumSpider(Spider):

    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)
        self.browser = RemoteSeleniumDriver(
            command_executor=SELENIUM_DRIVE_URL,
            desired_capabilities=webdriver.DesiredCapabilities.CHROME
        )
