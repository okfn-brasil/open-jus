import io
from collections import namedtuple

import requests
import rows
import splinter

from justa.spiders import SeleniumSpider


Action = namedtuple("Action", ["year", "state", "name", "code"])


def get_actions_for_state(state):
    url = "https://docs.google.com/spreadsheets/d/1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY/export?format=csv&id=1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY&gid=1565988556"
    response = requests.get(url)
    table = rows.import_from_csv(io.BytesIO(response.content), encoding="utf-8")
    return [
        Action(year=row.ano, state=row.estado, name=row.nome_acao, code=row.codigo_acao)
        for row in table
        if row.estado == state and all((row.ano, row.estado, row.codigo_acao, row.nome_acao))
    ]


class BaseBudgetExecutionSpider(SeleniumSpider):
    start_urls = ("http://justa.org.br/",)  # fake (real ones happens in Selenium)
    state = None  # TODO: set state code
    url = None  # Base URL used on `start_page` method
    value_to_wait_for = ""  # Value of an element to wait during operations
    value_wait_timeout = 30  # Seconds to wait for this value to be shown in the page

    @property
    def actions(self):
        return get_actions_for_state(self.state)

    def parse(self, _):
        self.start_page()
        for action in self.actions:
            yield from self.execute(action.year, action.code)

    def wait(self):
        if self.value_to_wait_for:
            self.browser.is_element_present_by_value(
                self.value_to_wait_for, wait_time=self.value_wait_timeout
            )

    def start_page(self):
        self.browser.visit(self.url)
        self.wait()

    def close(self):
        self.browser.quit()

    def execute(self, year, action):
        raise NotImplementedError()


class BRDecimalField(rows.fields.DecimalField):
    @classmethod
    def deserialize(self, value):
        value = str(value or "").replace(".", "").replace(",", ".")
        return super().deserialize(value)
