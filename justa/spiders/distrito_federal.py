import re
from datetime import datetime
from urllib.parse import urlencode

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from justa.items import JustaItem
from justa.settings import SELENIUM_DRIVE_URL
from justa.spiders import SeleniumSpider


class DistritoFederalSpider(SeleniumSpider):
    name = 'distrito_federal'
    allowed_domains = ['tjdft.jus.br']
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

    def start_page(self):
        self.browser.get(self.url)
        self.browser.wait_for('#botao_pesquisar').click()  # (re)post form

    @property
    def total_pages(self):
        if getattr(self, '_total_pages', None):
            return self._total_pages

        pattern = r'Total de páginas: (?P<total>\d+)\.'
        contents = self.browser.wait_for('#div_conteudoGeral')
        match = re.search(pattern, contents.text)

        self._total_pages = int(match.group('total'))
        return self.total_pages

    def parse_page(self, page, retries=10):
        paginator = self.browser.wait_for('#numeroDaPaginaAtual')
        paginator.send_keys(Keys.CONTROL + "a");
        paginator.send_keys(Keys.DELETE);
        paginator.send_keys(page)
        paginator.send_keys(Keys.ENTER)

        # sometimes the server struggles here, so let's restart and retry
        try:
            results = self.browser.wait_for('#tabelaResultado')
        except TimeoutException as error:
            self.start_page()
            retries -= 1
            if retries:
                return self.parse_page(page, retries)
            self.logger.error(f'Cannot find any rows for page {page}')
            return

        yield from (
            self.parse_row(row)
            for row in results.find_elements_by_css_selector('tbody tr')
        )

    def parse_row(self, row):
        columns = (td.text for td in row.find_elements_by_tag_name('td'))
        _, number, name, date, body, _, alt_text = columns
        text = self.read_tooltip(row)
        date = datetime.strptime(date, '%d/%m/%Y').date()
        return JustaItem(
            number=number,
            name=name,
            date=date,
            body=body,
            text=text or alt_text
        )

    def read_tooltip(self, row):
        self.browser.hover(row.find_element_by_class_name('botaoAjuda'))
        tooltip = self.browser.wait_for('.jquerybubblepopup-innerHtml')
        return tooltip.text
