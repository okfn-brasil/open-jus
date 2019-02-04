import io
import time
from collections import namedtuple

import rows
import rows.utils
import splinter


Action = namedtuple("Action", ["year", "state", "name", "code"])


class BRMoney(rows.fields.DecimalField):
    @classmethod
    def deserialize(self, value):
        value = value.replace(".", "").replace(",", ".")
        return super().deserialize(value)


def get_actions_for_state(state):
    url = "https://docs.google.com/spreadsheets/d/1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY/export?format=csv&id=1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY&gid=1565988556"
    return [
        Action(year=row.ano, state=row.estado, name=row.acao, code=row.cod_acao)
        for row in rows.utils.import_from_uri(url)
        if row.estado == state and all(row._asdict().values())
    ]


class SaoPauloBudgetExecutionScraper:
    url = "https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/FlexConsDespesa.aspx"

    def __init__(self):
        self.__browser = None

    @property
    def browser(self):
        if self.__browser is None:
            self.__browser = splinter.Browser("chrome")
        return self.__browser

    def wait(self, sleep=0.1):
        """Wait for the whole page to load - it takes time"""

        finished = False
        while not finished:
            if len(self.browser.find_by_value("Pesquisar")) > 0:
                finished = True
            else:
                time.sleep(sleep)

    def start(self):
        self.browser.visit(self.url)
        self.wait()

    def select_year(self, year):
        select = self.browser.find_by_xpath("//select[contains(@name, 'Ano')]")[0]
        select.select_by_text(str(year))
        self.wait()

    def check_all_phases(self):
        finished = False
        while not finished:
            finished = True
            for checkbox in self.browser.find_by_xpath(
                "//input[@type='checkbox' and contains(@name, 'Fase')]"
            ):
                if not checkbox.checked:
                    checkbox.check()
                    self.wait()
                    finished = False
                    break

    def select_action(self, action):
        actions = self.browser.find_by_xpath(
            "//select[contains(@name, 'Acao')]/option[starts-with(@value, '{}')]".format(
                action
            )
        )
        assert len(actions) == 1
        select_action = self.browser.find_by_xpath("//select[contains(@name, 'Acao')]")[
            0
        ]
        action_text = actions[0].text
        select_action.select_by_text(action_text)
        self.wait()

    def do_search(self):
        self.browser.find_by_value("Pesquisar")[0].click()
        self.wait()

    def close(self):
        self.browser.quit()

    def parse_budget(self):
        table = rows.import_from_html(
            io.BytesIO(self.browser.html.encode("utf-8")),
            index=10,
            force_types={
                "dotacao_inicial": BRMoney,
                "dotacao_atual": BRMoney,
                "empenhado": BRMoney,
                "liquidado": BRMoney,
                "pago": BRMoney,
                "pago_restos": BRMoney,
            },
        )

        result = [row._asdict() for row in table if row.elemento != "TOTAL"]
        return rows.import_from_dicts(result)

    def execute(self, year, action):
        self.start()
        self.select_year(year)
        self.check_all_phases()
        self.select_action(action)
        self.do_search()
        return self.parse_budget()


if __name__ == "__main__":
    scraper = SaoPauloBudgetExecutionScraper()
    for action in get_actions_for_state("SP"):
        print(
            "Downloading SP budget execution for {}/{}".format(action.year, action.code)
        )
        table = scraper.execute(action.year, action.code)
        output_filename = "SP-{}-{}.csv".format(action.year, action.code)
        rows.export_to_csv(table, output_filename)
    scraper.close()
