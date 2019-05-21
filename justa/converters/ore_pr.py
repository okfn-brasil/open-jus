from collections import OrderedDict

import rows
from cached_property import cached_property
from openpyxl import load_workbook
from rows.plugins.utils import slug

from base import FileExtractor
from magistrados import extract_magistrados
from utils import MoneyField


EMPTY_SET = set([None, ""])


class DPEPRFileExtractor(FileExtractor):

    filename_pattern = "PR/ORE-PR-DPE-*.xlsx"
    institution = "DPE"
    state = "PR"

    def extract(self):
        header, empty_lines = None, 0
        wb = load_workbook(self.filename, read_only=True, data_only=True)
        sheet = wb.active
        for row in sheet.rows:
            line = [cell.value for cell in row]
            if set(line).issubset(EMPTY_SET):  # Skip empty lines
                empty_lines += 1
                if empty_lines == 50:
                    # Probably end of data, ignore other empty lines
                    break
                else:
                    continue

            line = [str(value or "").strip() for value in line]
            if header is None:  # Maybe the header
                line = [slug(value) for value in line]
                if "matricula" in line and "cargo" in line:  # Header line!
                    header = line
            else:  # Regular row
                # TODO: translate field names
                # TODO: convert data types
                row = {field: value for field, value in zip(header, line)}
                for f in [
                    "field_0",
                    "nomeacao",
                    "nome",
                    "matricula",
                    "cargo",
                    "funcao",
                    "lotacao",
                    "remuneracao",
                    "outras_verbas_remuneratorias",
                    "funcao_de_confianca_ou_cargo_em_comissao",
                    "gratificacao_natalina",
                    "ferias_13",
                    "abono_permanencia",
                    "total_de_rendimentos_brutos",
                    "contribuicao_previdenciaria",
                    "irrf",
                    "outros_descontos",
                    "total_de_descontos",
                    "rendimento_liquido_total",
                    "indenizacoes",
                    "outras_remuneracoes_retroativas_eou_temporarias",
                    "field_18",
                ]:
                    if f not in row:
                        row[f] = None
                yield row


class MPEPRFileExtractor(FileExtractor):

    filename_pattern = "PR/ORE-PR-MPE-*.ods"
    institution = "MPE"
    state = "PR"
    fields_2018_ativos = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("lotacao", rows.fields.TextField),
            ("situacao", rows.fields.TextField),
            ("remuneracao_cargo_efetivo", rows.fields.TextField),
            ("remuneracao_outras", rows.fields.TextField),
            ("remuneracao_funcao_confianca_cc", rows.fields.TextField),
            ("remuneracao_13", rows.fields.TextField),
            ("remuneracao_ferias", rows.fields.TextField),
            ("remuneracao_abono_de_permanencia", rows.fields.TextField),
            ("remuneracao_atrasados", rows.fields.TextField),
            ("total_rendimentos", rows.fields.TextField),
            ("descontos_contribuicao_previdenciaria", rows.fields.TextField),
            ("descontos_imposto_de_renda", rows.fields.TextField),
            ("descontos_retencao_teto", rows.fields.TextField),
            ("total_descontos", rows.fields.TextField),
            ("rendimento_liquido", rows.fields.TextField),
        ]
    )
    fields_2018_inativos = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("situacao", rows.fields.TextField),
            ("remuneracao_cargo_efetivo", rows.fields.TextField),
            ("remuneracao_outras", rows.fields.TextField),
            ("remuneracao_funcao_confianca_cc", rows.fields.TextField),
            ("remuneracao_13", rows.fields.TextField),
            ("remuneracao_ferias", rows.fields.TextField),
            ("remuneracao_abono_de_permanencia", rows.fields.TextField),
            ("remuneracao_atrasados", rows.fields.TextField),
            ("total_rendimentos", rows.fields.TextField),
            ("descontos_contribuicao_previdenciaria", rows.fields.TextField),
            ("descontos_imposto_de_renda", rows.fields.TextField),
            ("descontos_retencao_teto", rows.fields.TextField),
            ("total_descontos", rows.fields.TextField),
            ("rendimento_liquido", rows.fields.TextField),
        ]
    )
    fields_2016_ativos_e_inativos = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("situacao", rows.fields.TextField),
            ("remuneracao_fc_cc_proventos", rows.fields.TextField),
            ("remuneracao_funcao", rows.fields.TextField),
            ("remuneracao_ferias", rows.fields.TextField),
            ("remuneracao_13", rows.fields.TextField),
            ("remuneracao_auxilios_e_beneficios", rows.fields.TextField),
            (
                "remuneracao_servicos_extraordinarios_adicional_noturno",
                rows.fields.TextField,
            ),
            ("remuneracao_abono_de_permanencia", rows.fields.TextField),
            ("remuneracao_vantagens_eventuais", rows.fields.TextField),
            ("remuneracao_vantagens_pessoais", rows.fields.TextField),
            ("total_rendimentos", rows.fields.TextField),
            ("descontos_retencao_teto", rows.fields.TextField),
            ("descontos_imposto_de_renda", rows.fields.TextField),
            ("descontos_contribuicao_previdenciaria", rows.fields.TextField),
            ("descontos_outros", rows.fields.TextField),
            ("total_descontos", rows.fields.TextField),
            ("rendimento_liquido", rows.fields.TextField),
        ]
    )
    fields_2016_ativos_excecao = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("situacao", rows.fields.TextField),
            ("remuneracao_exercicios_anteriores", rows.fields.TextField),
        ]
    )
    fields_2015_ativos_e_inativos = OrderedDict(
        [
            ("nome", rows.fields.TextField),
            ("cargo", rows.fields.TextField),
            ("situacao", rows.fields.TextField),
            ("remuneracao_fc_cc_proventos", rows.fields.TextField),
            ("remuneracao_funcao", rows.fields.TextField),
            ("remuneracao_ferias", rows.fields.TextField),
            ("remuneracao_13", rows.fields.TextField),
            ("remuneracao_auxilios_e_beneficios", rows.fields.TextField),
            (
                "remuneracao_servicos_extraordinarios_adicional_noturno",
                rows.fields.TextField,
            ),
            ("remuneracao_abono_de_permanencia", rows.fields.TextField),
            ("remuneracao_indenizacoes", rows.fields.TextField),
            ("remuneracao_vantagens_eventuais", rows.fields.TextField),
            ("remuneracao_exercicios_anteriores", rows.fields.TextField),
            ("remuneracao_vantagens_pessoais", rows.fields.TextField),
            ("total_rendimentos", rows.fields.TextField),
            ("descontos_retencao_teto", rows.fields.TextField),
            ("descontos_imposto_de_renda", rows.fields.TextField),
            ("descontos_contribuicao_previdenciaria", rows.fields.TextField),
            ("descontos_outros", rows.fields.TextField),
            ("total_descontos", rows.fields.TextField),
            ("rendimento_liquido", rows.fields.TextField),
        ]
    )

    @cached_property
    def field_names(self):
        fields = set()
        for attribute in dir(self):
            if attribute.startswith("fields_"):
                for key, value in getattr(self, attribute).items():
                    fields.add(key)
        return fields

    def convert_row(self, row):
        situacoes = {
            "": None,
            "1": "Exonerado",
            "2": "Aposentado Paranaprevidência",
            "3": "Espólio",
            "4": "Herdeiro",
            "5": "Servidor cedido por outro órgão",
        }
        row["situacao"] = situacoes[str(row["situacao"] or "")]
        for field_name in self.field_names:
            if field_name not in row:
                row[field_name] = None
        return row

    def extract(self):
        filename, metadata = self.filename, self.metadata
        start_row, fields = None, None

        # TODO: remuneraçãodeexeciciosanteriores_ativos
        # TODO: remuneraçãodeexeciciosanteriores_inativos
        # TODO: verbasindenizatorias_ativos
        # TODO: verbasindenizatorias_inativos

        year_month = int(f"{metadata['ano']}{metadata['mes']:02d}")
        observation = metadata["observacao"]
        if len(observation.replace("_ativos", "")) == 4:
            if year_month >= 201_708:
                start_row = 3
                fields = self.fields_2018_ativos
            elif year_month >= 201_603:
                start_row = 1
                fields = self.fields_2016_ativos_e_inativos
            elif year_month == 201_602:
                start_row = 1
                fields = self.fields_2016_ativos_excecao
            elif year_month >= 201_511:
                start_row = 2
                fields = self.fields_2015_ativos_e_inativos
        elif len(observation.replace("_inativos", "")) == 4:
            if year_month >= 201_708:
                start_row = 3
                fields = self.fields_2018_inativos
            elif year_month >= 201_602:
                start_row = 1
                fields = self.fields_2016_ativos_e_inativos
            elif year_month >= 201_511:
                start_row = 2
                fields = self.fields_2015_ativos_e_inativos

        if start_row and fields:
            table = rows.import_from_ods(
                self.filename, start_row=start_row, fields=fields
            )
            for row in table:
                if "registros listados" in row.nome.lower():
                    break
                yield self.convert_row(row._asdict())


class TJEPRFileExtractor(FileExtractor):

    filename_pattern = ("PR/ORE-PR-TJE-*.pdf", "contracheque.csv*")
    institution = "TJE"
    state = "PR"
    fields = OrderedDict([
        ("nome", rows.fields.TextField),
        ("cargo", rows.fields.TextField),
        ("lotacao", rows.fields.TextField),
        ("remuneracao_paradigma", MoneyField),
        ("vantagens_pessoais", MoneyField),
        ("subsidio_diferenca_de_subsidio_funcao_de_confianca_ou_cargo_em_comissao", MoneyField),
        ("indenizacoes", MoneyField),
        ("vantagens_eventuais", MoneyField),
        ("total_de_rendimentos", MoneyField),
        ("previdencia_publica", MoneyField),
        ("imposto_de_renda", MoneyField),
        ("descontos_diversos", MoneyField),
        ("retencao_por_teto_constitucional", MoneyField),
        ("total_de_descontos", MoneyField),
        ("rendimento_liquido", MoneyField),
        ("remuneracao_bruta_do_orgao_de_origem", MoneyField),
        ("diarias", MoneyField),
        ("observacao", rows.fields.TextField),
    ])

    def extract(self):
        filename, metadata = self.filename, self.metadata
        extension = filename.name.split(".")[-1].lower()

        # From 2017-11 to 2018-12, get data from Brasil.IO (in CSV) using the
        # `extract_magistrados` helper function.
        if "contracheque.csv" in filename.name:
            yield from extract_magistrados(filename, self.state)

        elif extension == "pdf":
            if metadata["ano"] == 2018 or (metadata["ano"] == 2017 and metadata["mes"] in (11, 12)):
                # Data already converted in contracheque.csv
                return

            total_pages = rows.plugins.pdf.number_of_pages(self.filename)
            for page in range(1, total_pages + 1):
                table = rows.import_from_pdf(
                    self.filename,
                    page_numbers=(page,),
                    fields=self.fields,
                    skip_header=page == 1,
                )
                for row in table:
                    yield {
                        "cargo": row.cargo,
                        "nome": row.nome.replace("\n", " ").strip(),
                        "rendimento_bruto": row.total_de_rendimentos,
                        "rendimento_liquido": row.rendimento_liquido,
                    }
