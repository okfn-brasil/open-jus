import re
from math import ceil
from pathlib import Path
from urllib.parse import urlencode

import rows
from scrapy import Request
from selenium.webdriver.common.keys import Keys

from justa.items import CourtOrderReference
from justa.spiders import SeleniumSpider, ESAJSpider


class TJSPFullTextSpider(ESAJSpider):
    """Spider to crawl full text court orders based on a LAI received PDF"""
    name = 'tjsp_full_text'
    minimum_items_expected = 865
    url = 'https://esaj.tjsp.jus.br/cposg/open.do'

    default_source = '/mnt/data/SUS-SP-TJE-1301até1812_viaLAI.pdf'
    fixed_part_of_the_court_order_number = '.8.26.'
    decision_labels = ('Decisão Monocrática', 'Despacho')
    appeal_keywords = ('Recurso Extraordinário', 'Recurso Especial')

    @property
    def numbers(self):
        if not Path(self.source).exists():
            self.logger.error(
                f'{self.source} does not exists. Use -a '
                'source=/path/to/lai.pdf to provide an existing path for the '
                'PDF with the court orders numbers received via LAI'
            )
            return

        self.logger.info(f'Reading {self.source}')
        for page in rows.plugins.pdf.pdf_to_text(self.source):
            yield from re.findall(self.pattern, page)


class TJSPNumbersSpider(SeleniumSpider):
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
