import re
from collections import namedtuple
from datetime import datetime
from math import ceil
from pathlib import Path
from urllib.parse import urlencode

import rows
from scrapy import Request
from selenium.webdriver.common.keys import Keys

from justa.items import CourtOrderReference, CourtOrderTJSP
from justa.spiders import SeleniumSpider


Decision = namedtuple('Decision', ('date', 'text'))


class TJSPNumbersSpider(SeleniumSpider):
    """Spider to list process numbers based on classes"""
    name = 'tjsp_numbers'
    minimum_items_expected = 826
    custom_settings = {'ROBOTSTXT_OBEY': False}
    url = 'https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do'
    page_url = 'https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do'

    @property
    def total_pages(self):
        if hasattr(self, '_total_pages'):
            return self._total_pages

        contents = self.browser.find_by_css('#paginacaoSuperior-D')
        pattern = r'Resultados (?P<start>\d+) a (?P<end>\d+) de (?P<total>\d+)'
        match = re.search(pattern, contents.text)
        start, end, total = (
            int(match.group(field))
            for field in ('start', 'end', 'total')
        )
        per_page = end - (start - 1)
        self._total_pages = ceil(total / per_page)
        self.logger.debug(f'Total pages to crawl: {self._total_pages}')
        return self.total_pages

    def start_requests(self):
        self.logger.debug('Using Selenium to deal with the HTML & JS form')
        self.browser.visit(self.url)

        # open classes modal
        button = '#botaoProcurar_classes'
        assert self.browser.is_element_present_by_css(button, wait_time=60)
        self.browser.find_by_css(button).first.click()

        # query the desired classes
        query = '#classes_treeSelectFilter'
        assert self.browser.is_element_present_by_css(query, wait_time=60)
        # We need to send some keys, something not implemented in Splinter yet,
        # but that will be possible soon:
        # https://github.com/cobrateam/splinter/issues/572
        # While this isn't possible we access the original Selenium element
        query_field = self.browser.find_by_css(query).first._element
        query_field.send_keys('suspensão')
        query_field.send_keys(Keys.ENTER)

        # select the desired classes
        classes = ('#classes_tree_node_144', '#classes_tree_node_145')
        for option in classes:
            assert self.browser.is_element_present_by_css(option)
            self.browser.find_by_css(option).first.click()

        # close the modal
        select = '.spwBotaoDefaultGrid[value=Selecionar]'
        self.browser.find_by_css(select).first.click()
        assert self.browser.is_element_not_present_by_css('#popupModalDiv')

        # select document type (Decisões Monocráticas)
        self.browser.find_by_css('label[for=Dcheckbox]').first.click()

        # deselect default document type (Acórdãos)
        self.browser.find_by_css('label[for=Acheckbox]').first.click()

        # run
        self.browser.find_by_css('#pbSubmit').click()
        assert self.browser.is_element_present_by_css('#divDadosResultado-D')
        cookies = {
            key: value for key, value in self.browser.cookies.all().items()
            if 'JSESSIONID' in key
        }

        # request result pages
        for page in range(1, self.total_pages + 1):
            self.logger.debug(f'Requesting court orders from page {page}')
            params = urlencode({'pagina': page, 'tipoDeDecisao': 'D'})
            yield Request(f'{self.page_url}?{params}', cookies=cookies)

    def parse(self, response):
        for item in response.css('.esajLinkLogin.downloadEmenta::text'):
            number = item.extract().strip()
            self.logger.debug(f'CourtOrderReference: {self.abbr} #{number}')
            yield CourtOrderReference(number=number, source=self.abbr)


class TJSPFullTextSpider(SeleniumSpider):
    """Spider to crawl full text court orders based on a LAI received PDF"""
    name = 'tjsp_full_text'
    minimum_items_expected = 865
    url = 'https://esaj.tjsp.jus.br/cposg/open.do'
    default_pdf = '/mnt/data/SUS-SP-TJE-1301até1812_viaLAI.pdf'
    pattern = r'(\d{7}-\d{2}\.\d{4}).\d\.\d{2}\.(\d{4})'
    start_urls = ('http://justa.org/',)  # fake (real ones happens in Selenium)

    def __init__(self, pdf=None, *args, **kwargs):
        self.pdf = pdf or self.default_pdf
        super(TJSPFullTextSpider, self).__init__(*args, **kwargs)

    @property
    def numbers(self):
        if not Path(self.pdf).exists():
            self.logger.error(
                f'{self.pdf} does not exists. Use -a pdf=/path/to/lai.pdf to '
                'provide an existing path for the PDF with the court orders '
                'numbers received via LAI'
            )
            return

        self.logger.info(f'Reading {self.pdf}')
        for page in rows.plugins.pdf.pdf_to_text(self.pdf):
            yield from re.findall(self.pattern, page)

    def error_handler(self, code, forum):
        number = f'{code}.8.26.{forum}'
        data_dir = Path(self.pdf).parent
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
        labels = ('Decisão Monocrática', 'Despacho')
        decisions = []

        # get the date and the decision; skips two columns: the first columns
        # contains the date, the second columns contains a link useless for us,
        # and the third column the decision text
        for current, previous in zip(cells[2:], cells):
            for label in labels:
                if current.startswith(label):
                    decision = Decision(self.parse_date(previous), current)
                    decisions.append(decision)

        if not decisions:
            return

        *_, decision = sorted(decisions, key=lambda d: len(d.text))
        return decision

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
        try:
            number, *status = output['number_and_status'].split()
        except ValueError:
            number, status = output['number_and_status'], []

        output['number'] = number
        output['status'] = ' '.join(status)
        del output['number_and_status']
        return output

    def court_order(self, code, forum):
        self.browser.visit(self.url)

        # search for the court order
        form = {'numeroDigitoAnoUnificado': code, 'foroNumeroUnificado': forum}
        for name, value in form.items():
            self.browser.is_element_present_by_name(name, wait_time=60)
            self.browser.fill(name, value)
        self.browser.find_by_id('botaoPesquisar').first.click()

        # expand collapsed areas
        self.browser.is_element_present_by_id(
            'tabelaUltimasMovimentacoes',
            wait_time=60
        )
        for link_id in ('linkpartes', 'linkmovimentacoes'):
            if self.browser.is_element_present_by_id(link_id):
                self.browser.find_by_id(link_id).first.click()

        decision = self.parse_decision()
        if not decision.text or not decision.date:
            self.error_handler(code, forum)
            return

        data = {'decision': decision.text, 'decision_date': decision.date}
        data.update(self.parse_metadata())

        if not data.get('number'):
            self.error_handler()
            return

        return CourtOrderTJSP(**data)

    def parse(self, _):
        for code, forum in self.numbers:
            court_order = self.court_order(code, forum)
            if court_order:
                yield court_order
