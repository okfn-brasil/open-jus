from collections import OrderedDict

import rows

from base import FileExtractor
from magistrados import extract_magistrados
from utils import MoneyField


class MPECEFileExtractor(FileExtractor):

    filename_pattern = "CE/ORE-CE-MPE-*.ods"
    institution = "MPE"
    state = "CE"
    fields = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("lotacao", rows.fields.TextField),
            ("remuneracao_cargo_efetivo", MoneyField),
            ("remuneracao_outras", MoneyField),
            ("remuneracao_funcao_confianca_cc", MoneyField),
            ("remuneracao_gratificacao_natalina", MoneyField),
            ("remuneracao_ferias_13", MoneyField),
            ("remuneracao_abono_de_permanencia", MoneyField),
            ("total_bruto", MoneyField),
            ("desconto_contribuicao_previdenciaria", MoneyField),
            ("desconto_imposto_de_renda", MoneyField),
            ("desconto_retencao_teto", MoneyField),
            ("total_desconto", MoneyField),
            ("rendimento_liquido", MoneyField),
        ]
    )

    def extract(self):
        table = rows.import_from_html(
            self.filename,
            encoding="iso-8859-1",
            row_tag="//tr[not(@bgcolor)]",
            fields=self.fields,
            skip_header=False,
        )
        for row in table:
            yield row._asdict()


class TJECEFileExtractor(FileExtractor):

    filename_pattern = ("CE/*/ORE-CE-TJE-*.*", "contracheque.csv*")
    institution = "TJE"
    state = "CE"

    def extract(self):
        filename, metadata = self.filename, self.metadata

        # From 2017-11 to 2018-12, get data from Brasil.IO (in CSV) using the
        # `extract_magistrados` helper function.
        if "contracheque.csv" in filename.name:
            yield from extract_magistrados(filename, self.state)

        else:
            # TODO: check repeated months

            if metadata["ano"] == 2018 or (metadata["ano"] == 2017 and metadata["mes"] in (11, 12)):
                # Data already converted in contracheque.csv
                return

            extension = filename.name.split(".")[-1].lower()
            if extension == "xls":
                table = rows.import_from_xls(filename, start_row=3)
                for row in table:
                    yield {
                        "cargo": row.cargo_no_orgao,
                        "nome": row.nome,
                        "rendimento_bruto": row.total_decreditos_v,
                        "rendimento_liquido": row.rendimentoliquido_xi,
                    }

            elif extension == "ods":
                fields_1 = OrderedDict([
                    ("nome", rows.fields.TextField),
                    ("lotacao", rows.fields.TextField),
                    ("cargo_no_orgao", rows.fields.TextField),
                    ("remuneracao_paradigma", MoneyField),
                    ("vantagens_pessoais", MoneyField),
                    ("subsidio_diferenca_de_subsidio_funcao_de_confianca_ou_cargo_em_comissao", MoneyField),
                    ("auxilios_indenizacoes", MoneyField),
                    ("auxilios_indenizacoes_pagto_tesouraria", MoneyField),
                    ("vantagens_eventuais", MoneyField),
                    ("decimo_terceiro_adiantamento2a_parcela", MoneyField),
                    ("terco_constitucional_de_ferias", MoneyField),
                    ("pensao_provisoria_de_montepio", MoneyField),
                    ("total_de_creditos", MoneyField),
                    ("previdencia_publica", MoneyField),
                    ("imposto_de_renda", MoneyField),
                    ("descontos_diversos", MoneyField),
                    ("retencao_por_teto_constitucional", MoneyField),
                    ("total_de_descontos_debitos", MoneyField),
                    ("rendimento_liquido", MoneyField),
                    ("remuneracao_do_orgao_de_origem", MoneyField),
                    ("diarias", MoneyField),
                ])
                fields_2 = OrderedDict([
                    ("matricula", rows.fields.TextField),
                    ("nome", rows.fields.TextField),
                    ("lotacao", rows.fields.TextField),
                    ("cargo_no_orgao", rows.fields.TextField),
                    ("remuneracao_paradigma", MoneyField),
                    ("vantagens_pessoais", MoneyField),
                    ("subsidio_diferenca_de_subsidio_funcao_de_confianca_ou_cargo_em_comissao", MoneyField),
                    ("auxilios_indenizacoes", MoneyField),
                    ("auxilios_indenizacoes_pagto_tesouraria", MoneyField),
                    ("vantagens_eventuais", MoneyField),
                    ("decimo_terceiro_adiantamento2a_parcela", MoneyField),
                    ("terco_constitucional_de_ferias", MoneyField),
                    ("pensao_provisoria_de_montepio", MoneyField),
                    ("total_de_creditos", MoneyField),
                    ("previdencia_publica", MoneyField),
                    ("imposto_de_renda", MoneyField),
                    ("descontos_diversos", MoneyField),
                    ("retencao_por_teto_constitucional", MoneyField),
                    ("total_de_descontos_debitos", MoneyField),
                    ("rendimento_liquido", MoneyField),
                    ("remuneracao_do_orgao_de_origem", MoneyField),
                    ("diarias", MoneyField),
                ])
                import decimal
                try:
                    table = rows.import_from_ods(
                        filename,
                        start_row=3,
                        end_column=20,
                        skip_header=True,
                        fields=fields_1
                    )
                except (ValueError, decimal.InvalidOperation):  # "Matricula" is hidden
                    return  # TODO: fix this case
                else:
                    for row in table:
                        yield {
                            "nome": row.nome,
                            "cargo": row.cargo_no_orgao,
                            "rendimento_liquido": row.rendimento_liquido,
                            "rendimento_bruto": row.total_de_creditos,
                        }

            elif extension == "pdf":
                return
