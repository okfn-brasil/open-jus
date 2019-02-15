import glob
import logging
import time
from pathlib import Path

import rows
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from justa.spiders.budget_base import BaseBudgetExecutionSpider, BRDecimalField


def wait_for(condition_function):
    start_time = time.time()
    while not condition_function():
        time.sleep(0.1)

class wait_for_page_load(object):

    def __init__(self, browser, value_to_wait_for):
        self.browser = browser
        self.value_to_wait_for = value_to_wait_for

    def __enter__(self):
        self.old_page = self.browser.find_by_tag('html').first._element

    def page_has_loaded(self):
        new_page = self.browser.find_by_tag('html').first._element
        different_html = new_page.id != self.old_page.id
        element_present = self.browser.is_element_present_by_value(
            self.value_to_wait_for, wait_time=0
        )
        return different_html and element_present

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


class CearaBudgetExecutionSpider(BaseBudgetExecutionSpider):
    browser_name = "firefox"
    download_path = Path("/mnt/data/")  # TODO: get from justa.settings?
    name = "budget_ce"
    preferences = {
        "browser.download.folderList": 2,
        "browser.download.dir": str(download_path.absolute()),
        "browser.download.lastDir": str(download_path.absolute()),
        "browser.download.manager.showWhenStarting": False,
        "browser.helperApps.neverAsk.saveToDisk": "application/vnd.ms-excel",
        "browser.download.panel.shown": False,
        "browser.download.manager.useWindow": False,
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

    def select_value(self, name, value, wait=True, by_text=True):
        value = str(value)
        select_xpath = "//select[contains(@name, '{}')]".format(name)
        if by_text:
            item_index, method_name = 1, "select_by_text"
        else:
            item_index, method_name = 0, "select"

        if wait:
            with wait_for_page_load(self.browser, self.value_to_wait_for):
                select = self.browser.find_by_xpath(select_xpath).first
                getattr(select, method_name)(value)
        else:
            select = self.browser.find_by_xpath(select_xpath).first
            getattr(select, method_name)(value)

    def radio_check(self, name, value, wait=True):
        radios = self.browser.find_by_xpath(
            "//input[@type = 'radio' and contains(@name, '{}')]".format(name)
        )
        desired_radio = [radio for radio in radios if radio.value == value][0]
        if desired_radio.checked:  # Checked already, do nothing
            return

        if wait:
            with wait_for_page_load(self.browser, self.value_to_wait_for):
                desired_radio.check()
        else:
            desired_radio.check()

    def select_options(self, name):
        try:
            options = self.browser.find_by_xpath(
                "//select[contains(@name, '{}')]/option".format(name)
            )
            return [(option.value, option.text, option.selected) for option in options]
        except StaleElementReferenceException:
            # Page probably reloading, so wait and try again later
            time.sleep(0.1)
            return self.select_options(name)

    def select_year(self, year):
        logging.info(f"[Budget-CE]   Selecting year {year}")
        self.select_value("Ano", year)

    def select_action(self, action):
        logging.info(f"[Budget-CE]   Selecting action {action}")
        self.select_value("ProjetoAtividade", action, by_text=False, wait=False)

    def select_month(self, value):
        logging.info(f"[Budget-CE]   Selecting month {value}")
        self.select_value("Mes", value)

    def select_modality_91(self, value):
        logging.info(f"[Budget-CE]   Selecting Modalidade91 {value}")
        self.select_value("Modalidade91", value, wait=False)

    def select_report(self, area, inner_area):
        """
        First, click the radio button with more general report area
        Then, the inner area in the select
        To finish, select the report output format as plain spreadsheet
        """
        logging.info(f"[Budget-CE]   Selecting report ({area}, {inner_area})")

        self.radio_check("Relatorio", area, wait=True)
        self.select_value("Relatorio", inner_area, wait=False)
        self.radio_check("Formato", "Xlss", wait=False)  # Xlss = "Planilha"

    def list_files(self):
        return glob.glob(str(self.download_path / "*.*"))

    def do_search(self, sleep=0.1):
        logging.info(f"[Budget-CE]   Asking to generate the spreadsheet")
        files_before = set(self.list_files())

        with wait_for_page_load(self.browser, self.value_to_wait_for):
            self.browser.find_by_value("Visualizar").first.click()

        # Wait for the file to be downloaded
        diff = set()
        while not diff:
            time.sleep(sleep)
            diff = set(self.list_files()) - files_before
            if any(filename.lower().endswith(".part") for filename in diff):
                # ".part" extension means download didn't finished
                diff = set()
        assert len(diff) == 1, diff
        return diff.pop()

    def parse_budget(self, filename, year, action):
        logging.info(f"[Budget-CE]   Parsing budget {filename}")
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
            assert str(action_code) == str(action)
            row.update({
                "ano": year,
                "codigo_acao": action,
                "estado": "CE",
            })
            result.append(row)

        return result

    def execute(self, year, action):
        logging.info(f"[Budget-CE] Starting for {year} and action {action}")
        self.select_year(year)
        self.select_month("Dezembro")  # December has the cumulative for the year
        self.select_action(action)
        self.select_modality_91("TUDO")
        self.select_report("Outros", "PA")
        filename = self.do_search()
        result = self.parse_budget(filename, year, action)

        for row in rows.import_from_dicts(result):
            yield row._asdict()
