import re
from datetime import datetime
from time import sleep
from urllib.parse import urlencode

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

from justa.items import CourtOrder
from justa.settings import SELENIUM_DRIVE_URL
from justa.spiders import SeleniumSpider


class DistritoFederalSpider(SeleniumSpider):
    name = 'distrito_federal'
    minimum_items_expected = 433
    params = urlencode({
        'visaoId': 'tjdf.sistj.acordaoeletronico.buscaindexada.apresentacao.VisaoBuscaAcordao',
        'nomeDaPagina': 'buscaLivre2',
        'buscaPorQuery': '1',
        'baseSelecionada': 'BASE_DESPACHO',
        'filtroAcordaosPublicos': 'falsei',
        'camposSelecionados': '[ESPELHO, INTEIROTEOR]',
        'argumentoDePesquisa': '"suspensao de seguranca"',
        'numero': '',
        'tipoDeRelator': 'TODOS',
        'dataFim': '31/12/2018',
        'indexacao': '',
        'ramoJuridico': '',
        'baseDados': '[BASE_DESPACHO]',
        'tipoDeNumero': 'Processo',
        'tipoDeData': 'DataPublicacao',
        'ementa': '',
        'filtroSegredoDeJustica': 'false',
        'desembargador': '',
        'dataInicio': '01/01/2013',
        'legislacao': '',
        'orgaoJulgador': '',
        'numeroDaPaginaAtual': '1',
        'quantidadeDeRegistros': '20',
        'totalHits': '433',
    })
    url = (
        'https://pesquisajuris.tjdft.jus.br/'
        f'IndexadorAcordaos-web/sistj?{params}'
    )
    start_urls = (SELENIUM_DRIVE_URL,)  # fake (real ones happens in Selenium)

    def parse(self, _):
        self.start_page()
        for page in range(1, self.total_pages + 1):
            yield from self.parse_page(page)

    def start_page(self, page=1):
        button = '#botao_pesquisar'
        self.browser.visit(self.url)
        assert self.browser.is_element_present_by_css(button, wait_time=60)
        self.browser.find_by_css(button).click()

        if page > 1:
            field = '#numeroDaPaginaAtual'
            assert self.browser.is_element_present_by_css(field, wait_time=60)

            # We need to send some keys, something not implemented in Splinter
            # yet, but that will be possible soon:
            # https://github.com/cobrateam/splinter/issues/572
            # While this isn't possible we access the original Selenium element
            paginator = self.browser.find_by_css(field).first._element
            paginator.send_keys(Keys.CONTROL + "a");
            paginator.send_keys(Keys.DELETE);
            paginator.send_keys(page)
            paginator.send_keys(Keys.ENTER)

    @property
    def total_pages(self):
        if getattr(self, '_total_pages', None):
            return self._total_pages

        selector = '#div_conteudoGeral'
        assert self.browser.is_element_present_by_css(selector, wait_time=60)

        contents = self.browser.find_by_css(selector)
        pattern = r'Total de páginas: (?P<total>\d+)\.'
        match = re.search(pattern, contents.text)
        self._total_pages = int(match.group('total'))
        self.logger.debug(f'Total pages to crawl: {self._total_pages}')
        return self.total_pages

    def parse_page(self, page):
        self.start_page(page)
        self.logger.debug(f'Crawling page {page} of {self.total_pages}')
        selector = '#tabelaResultado'
        assert self.browser.is_element_present_by_css(selector, wait_time=60)

        rows = self.browser.find_by_css(selector).find_by_css('tbody tr')
        yield from (self.parse_row(row) for row in rows)

    def parse_row(self, row):
        columns = (td.text for td in row.find_by_css('td'))
        _, number, name, date, body, _, alt_text = columns
        text = self.read_tooltip(row)
        date = datetime.strptime(date, '%d/%m/%Y').date()
        return CourtOrder(
            number=number,
            name=name,
            date=date,
            body=body,
            text=text or alt_text
        )

    def read_tooltip(self, row, mouse_over=True):
        if mouse_over:
            row.find_by_css('.botaoAjuda').mouse_over()

        selector = '.jquerybubblepopup-innerHtml'
        assert self.browser.is_element_present_by_css(selector, wait_time=60)

        try:
            return self.browser.find_by_css(selector).first.text
        except StaleElementReferenceException:
            # not sure why Chrome complains here from time to time, so retry
            sleep(0.5)
            return self.read_tooltip(row, mouse_over=False)
