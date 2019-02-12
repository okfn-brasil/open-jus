import glob
import time
from pathlib import Path

import rows
from selenium import webdriver

from justa.spiders.budget_base import BaseBudgetExecutionSpider, BRDecimalField


class CearaBudgetExecutionSpider(BaseBudgetExecutionSpider):
    download_path = Path("/mnt/data/download")  # TODO: get from justa.settings?
    name = "budget_ce"
    preferences = {
        "disable-popup-blocking": "true",
        "download.default_directory": str(download_path.absolute()),
        "download.directory_upgrade": "true",
        "download.prompt_for_download": "false",
    }
    state = "CE"
    url = "http://web3.seplag.ce.gov.br/siofconsulta/Paginas/frm_consulta_execucao.aspx"
    value_to_wait_for = "Visualizar"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.headless:
            raise RuntimeError(
                "This spider cannot be run in headless mode. Check the bug: <https://bugs.chromium.org/p/chromium/issues/detail?id=696481>"
            )
        if not self.download_path.exists():
            self.download_path.mkdir(parents=True)

    def select_value(self, name, value, wait=True):
        select = self.browser.find_by_xpath(
            "//select[contains(@name, '{}')]".format(name)
        ).first
        select.select_by_text(value)
        if wait:
            self.wait()

    def radio_check(self, name, value, wait=True):
        radios = self.browser.find_by_xpath(
            "//input[@type = 'radio' and contains(@name, '{}')]".format(name)
        )
        for radio in radios:
            if radio.value == value:
                radio.check()
                break
        if wait:
            self.wait()

    def select_year(self, year):
        self.select_value("Ano", str(year))

    def select_action(self, action):
        actions = self.browser.find_by_xpath(
            "//select[contains(@name, 'ProjetoAtividade')]/option[starts-with(@value, '{}')]".format(
                action
            )
        )
        assert len(actions) == 1

        self.select_value("ProjetoAtividade", actions.first.text)

    def select_month(self, value):
        self.select_value("Mes", str(value))

    def select_modality_91(self, value):
        self.select_value("Modalidade91", value, wait=False)

    def select_report(self, area, inner_area):
        """
        First, click the radio button with more general report area
        Then, the inner area in the select
        To finish, select the report output format as plain spreadsheet
        """

        self.radio_check("Relatorio", area)
        self.select_value("Relatorio", inner_area)
        self.radio_check("Formato", "Xlss", wait=False)  # Xlss = "Planilha"

    def list_files(self):
        return glob.glob(str(self.download_path / "*.*"))

    def do_search(self, sleep=0.1):
        files_before = set(self.list_files())
        self.browser.find_by_value("Visualizar").first.click()
        self.wait()  # Wait for the form to be POSTed

        # Wait for the file to be downloaded
        diff = set()
        while not diff:
            time.sleep(sleep)
            diff = set(self.list_files()) - files_before
            if len(diff) == 1 and list(diff)[0].endswith(".crdownload"):
                # ".crdownload" extension means download didn't finished
                diff = set()
        assert len(diff) == 1
        return diff.pop()

    def parse_budget(self, filename, year, action):
        # First, import the table and clean up not desired lines
        table = rows.import_from_xls(filename)
        result = []
        for row in table:
            if row.codigo.lower().strip() == "total geral":
                break
            result.append(row._asdict())

        # Then, import desired lines parsing some columns as Decimals
        table = rows.import_from_dicts(
            result,
            force_types={
                "lei": BRDecimalField,
                "lei_cred": BRDecimalField,
                "empenhado": BRDecimalField,
                "pago": BRDecimalField,
                "emp": BRDecimalField,
                "pago_2": BRDecimalField,
            },
        )
        result = []
        for row in table:
            row = row._asdict()
            action_code = row.pop("codigo")
            assert action_code == action
            row.update({
                "ano": year,
                "codigo_acao": action,
                "estado": "CE",
            })
            result.append(row)

        return result

    def execute(self, year, action):
        self.select_year(year)
        self.select_month("Dezembro")  # December has the cumulative for the year
        self.select_action(action)
        self.select_modality_91("TUDO")
        self.select_report("Outros", "PA")
        filename = self.do_search()
        result = self.parse_budget(filename, year, action)

        for row in rows.import_from_dicts(result):
            yield row._asdict()
