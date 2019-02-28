import re
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from time import sleep

from requests import post
from scrapy import Spider
from splinter.driver.webdriver import WebDriverElement
from splinter.driver.webdriver.remote import WebDriver

from justa.settings import SELENIUM_DRIVE_URL, TWO_CAPTCHA_API_KEY
from justa.items import CourtOrderESAJ


Decision = namedtuple('Decision', ('date', 'text'))
Part = namedtuple('Part', ('name', 'attorneys'))


class RemoteWebDriver(WebDriver):
    """A clone of the default remote web driver class, but using the non-remote
    web driver element class. More details on this specific need:
    https://github.com/cobrateam/splinter/issues/674 """

    def __init__(self, *args, **kwargs):
        super(RemoteWebDriver, self).__init__(*args, **kwargs)
        self.element_class = WebDriverElement  # overrides the element class


class SeleniumSpider(Spider):

    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)
        self.browser = RemoteWebDriver(
            browser='chrome',
            url=SELENIUM_DRIVE_URL
        )


class ESAJSpider(SeleniumSpider):
    """Spider to crawl full text court orders from eSAJ systems, based on court
    orders number usually collected mannualy via LAI"""
    pattern = r'(\d{7}-\d{2}\.\d{4}).\d\.\d{2}\.(\d{4})'
    start_urls = ('http://justa.org/',)  # fake (real ones happens in Selenium)
    recaptcha = False
    js_cache = {}

    def __init__(self, source=None, *args, **kwargs):
        self.source = source or self.default_source
        super(ESAJSpider, self).__init__(*args, **kwargs)

    def error_handler(self, code, forum):
        parts = (code, self.fixed_part_of_the_court_order_number, forum)
        number = ''.join(parts)
        data_dir = Path(self.source).parent
        screenshot = Path(data_dir) / f'debug-{number}.'
        filename = self.browser.screenshot(str(screenshot), full=True)
        self.logger.info(
            f'Unable to crawl court order {number}, '
            f'check {filename} for details'
        )

    def parse_date(self, value, format='%d/%m/%Y'):
        try:
            return datetime.strptime(value, format)
        except ValueError:
            self.logger.error(f'Cannot parse {value} as {format} date')
            return None

    def parse_decision(self):
        cells = tuple(td.text.strip() for td in self.browser.find_by_tag('td'))
        decisions = []

        # get the date and the decision; skips two columns: the first columns
        # contains the date, the second columns contains a link useless for us,
        # and the third column the decision text
        for current, previous in zip(cells[2:], cells):
            for label in self.decision_labels:
                if current.startswith(label):
                    decision = Decision(self.parse_date(previous), current)
                    decisions.append(decision)

        if not decisions:
            return

        *_, decision = sorted(decisions, key=lambda d: len(d.text))
        return decision

    @staticmethod
    def parse_part(value):
        """Separate the name of the part from the name of the attorneys"""
        pattern = r'Advogad[oa]: ?(?P<name>.+)'
        attorneys = (name.strip() for name in re.findall(pattern, value))
        name = re.sub(pattern, '', value).strip()
        return Part(name, ', '.join(attorneys))

    def parse_appeals(self):
        keywords = ('Recurso Extraordinário', 'Recurso Especial')
        has_appeals = any(
            self.browser.is_text_present(keyword)
            for keyword in self.appeal_keywords
        )
        if not has_appeals:
            return ''

        cells = tuple(td.text.strip() for td in self.browser.find_by_tag('td'))
        appeals = []

        # get the date and the decision; skips two columns: the first columns
        # contains the date, the second columns contains a link useless for us,
        # and the third column the decision text
        for current, previous in zip(cells[2:], cells):
            for keyword in keywords:
                if keyword in current and self.parse_date(previous):
                    appeals.append('\n'.join((previous, current)))

        return '\n\n'.join(appeals) if appeals else ''

    def parse_metadata(self):
        cells = tuple(td.text.strip() for td in self.browser.find_by_tag('td'))
        mapping = {
            'Processo:': 'number_and_status',
            'Números de origem:': 'source_numbers',
            'Relator:': 'reporter',
            'Classe:': 'category',
            'Requerente:': 'petitioner',
            'Requerido:': 'requested',
            'Requerida:': 'requested',
            'Assunto:': 'subject'
        }
        data = {key: [] for key in set(mapping.values())}

        # get the contents of a column based on the contents of the previous
        # column, that is the case of a simple two columns table in which
        # the first columns acts as a header and the second one holds the data
        for current_cell, next_cell in zip(cells, cells[1:]):
            key = mapping.get(current_cell)
            if key in data:
                data[key].append(next_cell)

        output = {key: ', '.join(value) for key, value in data.items()}

        # parse number and status
        try:
            number, *status = output['number_and_status'].split()
        except ValueError:
            number, status = output['number_and_status'], []
        output['number'] = number
        output['status'] = ' '.join(status)
        del output['number_and_status']

        # parse parts (split names of the part from attorneys)
        for key in ('petitioner', 'requested'):
            part = self.parse_part(output[key])
            output[key] = part.name
            output[f'{key}_attorneys'] = part.attorneys

        # parse appeals
        output['appeals'] = self.parse_appeals()

        return output

    @staticmethod
    def two_captcha_data(**kwargs):
        data = dict(key=TWO_CAPTCHA_API_KEY, json=1)
        if kwargs:
            data.update(kwargs)
        return data

    def set_recaptcha_response_visibility(self, visible):
        action = 'show' if visible else 'hide'
        cached = self.js_cache.get(action)
        if cached:
            self.browser.execute_script(cached)

        with open(Path() / 'justa' / 'js' / f'{action}_recaptcha.js') as fobj:
            content = fobj.read()

        self.js_cache[action] = content
        self.browser.execute_script(content)

    def request_recaptcha_solution(self, recaptcha_key):
        data = self.two_captcha_data(
            googlekey=recaptcha_key,
            method='userrecaptcha',
            pageurl=self.browser.url
        )
        response = post("http://2captcha.com/in.php", data=data)
        return response.json().get('request')

    def fetch_recaptcha_solution(self):
        if not self.request_id:
            return

        data = self.two_captcha_data(action="get", id=self.request_id)
        response = post("http://2captcha.com/res.php", data=data)
        result = response.json().get('request')
        if not result or result == 'CAPCHA_NOT_READY':
            return

        return result

    def feedback_recaptcha_solution(self, success):
        if not self.request_id:
            return

        action = 'reportgood' if success else 'reportbad'
        data = self.two_captcha_data(action=action, id=self.request_id)
        post("http://2captcha.com/res.php", data=data)

    def solve_recaptcha(self):
        has_recaptcha = self.browser.is_element_present_by_css(
            '.g-recaptcha',
            wait_time=60
        )
        if not has_recaptcha:
            return

        recaptcha = self.browser.find_by_css('.g-recaptcha').first
        recaptcha_id = recaptcha._element.get_attribute('data-sitekey')
        self.request_id = self.request_recaptcha_solution(recaptcha_id)

        sleep(15)
        result = self.fetch_recaptcha_solution()
        while not result:
            sleep(2)
            result = self.fetch_recaptcha_solution()

        self.set_recaptcha_response_visibility(True)
        self.browser.fill('g-recaptcha-response', result)
        self.set_recaptcha_response_visibility(False)

    def search(self, code, forum, recaptcha=False):
        if 'search.do' not in self.browser.url:
            self.browser.visit(self.url)

        form = {'numeroDigitoAnoUnificado': code, 'foroNumeroUnificado': forum}
        for name, value in form.items():
            self.browser.is_element_present_by_name(name, wait_time=60)
            self.browser.fill(name, value)

        if self.recaptcha:
            self.solve_recaptcha()

        self.browser.find_by_id('botaoPesquisar').first.click()

    def court_order(self, code, forum):
        self.search(code, forum)
        has_results = self.browser.is_element_present_by_id(
            'tabelaUltimasMovimentacoes',
            wait_time=60
        )

        if self.recaptcha:
            self.feedback_recaptcha_solution(has_results)

        if not has_results:
            self.error_handler(code, forum)
            return

        for link_id in ('linkpartes', 'linkmovimentacoes'):
            if self.browser.is_element_present_by_id(link_id):
                self.browser.find_by_id(link_id).first.click()

        decision = self.parse_decision()
        if not decision or not decision.text or not decision.date:
            self.error_handler(code, forum)
            return

        data = {'decision': decision.text, 'decision_date': decision.date}
        data.update(self.parse_metadata())

        if not data.get('number'):
            self.error_handler()
            return

        return CourtOrderESAJ(**data)

    def parse(self, _):
        for code, forum in self.numbers:
            court_order = self.court_order(code, forum)
            if court_order:
                yield court_order
