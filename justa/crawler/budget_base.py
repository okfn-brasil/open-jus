from collections import namedtuple

import rows
import rows.utils
import splinter


Action = namedtuple("Action", ["year", "state", "name", "code"])


def get_actions_for_state(state):
    url = "https://docs.google.com/spreadsheets/d/1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY/export?format=csv&id=1epxFffymqv1t2s37rQ-p5eKpvecOIBzCfJPLI53wYTY&gid=1565988556"
    return [
        Action(year=row.ano, state=row.estado, name=row.acao, code=row.cod_acao)
        for row in rows.utils.import_from_uri(url)
        if row.estado == state and all(row._asdict().values())
    ]


class BaseBudgetExecutionSpider:
    url = None  # Base URL used on `start` method
    value_to_wait_for = ""  # Value of an element to wait during operations
    value_wait_timeout = 30  # Seconds to wait for this value to be shown in the page

    def __init__(self, headless=True):
        self.browser_args = []
        self.browser_kwargs = {"headless": headless}
        self.headless = headless
        self._browser = None

    def get_browser_options(self):
        return None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = splinter.Browser(
                "chrome",
                options=self.get_browser_options(),
                *self.browser_args,
                **self.browser_kwargs,
            )
        return self._browser

    def wait(self):
        if self.value_to_wait_for:
            self.browser.is_element_present_by_value(
                self.value_to_wait_for,
                wait_time=self.value_wait_timeout,
            )

    def start(self):
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
