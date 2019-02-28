import re
from collections import namedtuple
from datetime import datetime
from pathlib import Path

from scrapy import Spider
from splinter.driver.webdriver import WebDriverElement
from splinter.driver.webdriver.remote import WebDriver

from justa.settings import SELENIUM_DRIVE_URL
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

    def search(self, code, forum):
        self.browser.visit(self.url)
        form = {'numeroDigitoAnoUnificado': code, 'foroNumeroUnificado': forum}
        for name, value in form.items():
            self.browser.is_element_present_by_name(name, wait_time=60)
            self.browser.fill(name, value)
        self.browser.find_by_id('botaoPesquisar').first.click()

    def court_order(self, code, forum):
        self.search(code, forum)
        self.browser.is_element_present_by_id(
            'tabelaUltimasMovimentacoes',
            wait_time=60
        )
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
