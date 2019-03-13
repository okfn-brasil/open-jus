import re
from pathlib import Path

from rows.plugins.xls import import_from_xls

from justa.spiders import ESAJSpider


class TJCEFullTextSpider(ESAJSpider):
    name = 'tjce_full_text'
    minimum_items_expected = 942  # TODO double-check
    url = 'https://esaj.tjce.jus.br/cposg5/open.do'

    default_source = '/mnt/data/SUS-CE-TJE-1301_viaLAIaté31122018.xls'
    fixed_part_of_the_court_order_number = '.8.06.'
    decision_labels = (
        'Concedida a Medida Liminar',
        'Expedição de Decisão Monocrática'
    )
    appeal_keywords = ('Recurso Extraordinário', 'Recurso Especial')
    years = range(2013, 2018 + 1)
    recaptcha = True

    @property
    def numbers(self):
        if not Path(self.source).exists():
            self.logger.error(
                f'{self.source} does not exists. Use -a '
                'source=/path/to/lai.xls to provide an existing path for the '
                'Excel file with the court orders numbers received via LAI'
            )
            return

        self.logger.info(f'Reading {self.source}')
        for year in self.years:
            for row in import_from_xls(self.source, sheet_name=str(year)):
                match = re.match(self.pattern, row.processo)
                if not match:
                    continue
                yield match.group(1), match.group(2)
