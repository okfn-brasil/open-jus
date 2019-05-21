import csv
from collections import OrderedDict

import rows
from cached_property import cached_property

from base import FileExtractor
from magistrados import extract_magistrados
from utils import MoneyField, detect_dialect, detect_encoding


class DPESPFileExtractor(FileExtractor):

    filename_pattern = "SP/ORE-SP-DPE-*.*"
    institution = "DPE"
    state = "SP"
    HEADER_OLD = (
        "nome cargo total_bruto um_terco_ferias_e_decimo_terceiro atrasados "
        "referencia_atrasados descontos rendimento_liquido diarias "
        "abono_permanencia devolucao_debito auxilio_alimentacao outras_indenizacoes"
    ).split()
    HEADER_NEW = (
        "nome cargo total_bruto um_terco_ferias decimo_terceiro atrasados "
        "referencia_atrasados descontos rendimento_liquido diarias "
        "abono_permanencia atividades_dias_nao_uteis auxilio_alimentacao total"
    ).split()
    ADD_TO_NEW = (
        "um_terco_ferias_e_decimo_terceiro",
        "devolucao_debito",
        "outras_indenizacoes",
    )
    ADD_TO_OLD = (
        "um_terco_ferias",
        "decimo_terceiro",
        "atividades_dias_nao_uteis",
        "total",
    )
    TYPES = {
        "abono_permanencia": MoneyField,
        "atividades_dias_nao_uteis": MoneyField,
        "atrasados": MoneyField,
        "auxilio_alimentacao": MoneyField,
        "decimo_terceiro": MoneyField,
        "descontos": MoneyField,
        "devolucao_debito": MoneyField,
        "diarias": MoneyField,
        "outras_indenizacoes": MoneyField,
        "rendimento_liquido": MoneyField,
        "total": MoneyField,
        "total_bruto": MoneyField,
        "um_terco_ferias": MoneyField,
        "um_terco_ferias_e_decimo_terceiro": MoneyField,
    }

    @cached_property
    def header(self):
        return self.HEADER_NEW if not self.old else self.HEADER_OLD

    def convert_row(self, row):
        fixed_row = []
        for index, item in enumerate(row):
            if index == 0:
                item = item.replace(" Defensor", "\nDefensor")
                if item.count("\n") == 2:
                    # Case "Defensor Público do Estado\nFulano de Tal\nAssessor"
                    parts = item.splitlines()
                    item = f"{parts[1]}\n{parts[0]} {parts[2]}"
                elif "\n" in item:
                    if "\nDefensor" not in item and "\nCorregedor" not in item:
                        # TODO: what if there are other positions?
                        item = item.replace("\n", " ")  # Surname in the second line
            else:
                item = item.replace("\n", " ").strip()
            fixed_row.extend(item.splitlines())

        # Fix when "referencia_atrasados" is not filled
        if not self.old and len(fixed_row) == 13:
            fixed_row.insert(6, None)
        elif self.old and len(fixed_row) == 12:
            fixed_row.insert(5, None)
        row = dict(zip(self.header, fixed_row))
        if " " in row["atrasados"]:
            references = []
            parts = row["atrasados"].replace("\n", " ").split()
            for part in parts:
                if "/" not in part:
                    row["atrasados"] = part
                else:
                    references.append(part)
            row["referencia_atrasados"] = " ".join(references)

        # TODO: replace with "fill" from parent class
        keys_to_add = self.ADD_TO_NEW if not self.old else self.ADD_TO_OLD
        for key in keys_to_add:
            row[key] = None

        for key, value in self.TYPES.items():
            row[key] = value.deserialize(row[key])

        return row

    def extract(self):
        if self.filename.name.lower().endswith(".xlsx"):
            # TODO: extract xlsx
            yield from []
            return

        filename, metadata = self.filename, self.metadata
        pages = rows.plugins.pdf.number_of_pages(filename)
        self.old = (
            metadata["ano"] in (2013, 2014, 2015)
            or metadata["ano"] == 2016
            and metadata["mes"] <= 11
        )
        starts_after = "INDENIZ." if self.old else "INDEN.)"

        for page in range(2, pages + 1):
            table = rows.plugins.pdf.pdf_table_lines(
                filename, page_numbers=(page,), starts_after=starts_after
            )
            for row_data in table:
                if not row_data[0]:  # Almost empty header line
                    continue
                yield self.convert_row(row_data)


class MPESPFileExtractor(FileExtractor):

    filename_pattern = "SP/ORE-SP-MPE-*.ods"
    institution = "MPE"
    state = "SP"

    def convert_row(self, row):
        translate = dict(
            [
                ("bruto", "rendimento_bruto"),
                ("cargo_efetivo", "cargo"),
                ("contr_previd", "desconto_contribuicao_previdenciaria"),
                ("contrprevid", "desconto_contribuicao_previdenciaria"),
                ("dec_terceiro", "remuneracao_13o_salario"),
                ("deduc_mp", "desconto_mp"),
                ("descontos", "desconto_total"),
                ("field_13_de_ferias", "remuneracao_ferias"),
                ("field_13_ferias", "remuneracao_ferias"),
                ("imp_renda", "desconto_imposto_de_renda"),
                ("liquido", "rendimento_liquido"),
                ("matric", "matricula"),
                ("nome_completo", "nome"),
                ("out_obrig_jud", "desconto_outros"),
                ("out_remun_retr", "remuneracao_outras_retroativas"),
                ("out_remunretr", "remuneracao_outras_retroativas"),
                ("out_remumretr", "remuneracao_outras_retroativas"),
                ("outras_indeniz", "remuneracao_outras_indenizacoes"),
                ("remuneracao", "remuneracao_cargo_efetivo"),
                ("rendimento_liquido_total", "rendimento_liquido"),
                ("retr_valor_estornado", "valor_estornado_retr"),
                ("total_bruto", "rendimento_bruto"),
                ("total_descontos", "desconto_total"),
                ("unidadm", "lotacao"),
                ("vantagens", "remuneracao_outras"),
            ]
        )
        row = row._asdict()
        new = {}
        for key, value in row.items():
            if key in translate:
                key = translate[key]
            new[key] = value
            if key.startswith("field_") and value in ("", None, ";"):
                del new[key]

        if "situacao" not in new:
            new["situacao"] = "ATIVO" if "_ativos" in self.filename.name else "INATIVO"

        all_fields = (
            "auxilio_alimentacao",
            "auxilio_creche",
            "auxilio_ferias_em_pecunia",
            "auxilio_transporte",
            "desconto_retencao_teto",
            "numero_do_processo",
            "origem_do_processo_adminstrativo",
            "remuneracao_abono_de_permanencia",
            "remuneracao_funcao_confianca_ou_cc",
            "remuneracao_temporaria_outras",
            "rendimento_liquido",
            "valor_estornado_retr",
        )
        # TODO: write all of them
        for field_name in all_fields:
            if field_name not in new:
                new[field_name] = None

        return new

    def extract_inativos_2018(self):
        fields_inativos_2018 = OrderedDict(
            [
                ("matricula", rows.fields.IntegerField),
                ("nome", rows.fields.TextField),
                ("cargo", rows.fields.TextField),
                ("lotacao", rows.fields.TextField),
                ("remuneracao_cargo_efetivo", rows.fields.DecimalField),
                ("remuneracao_outras", rows.fields.DecimalField),
                ("remuneracao_13o_salario", rows.fields.DecimalField),
                ("rendimento_bruto", rows.fields.DecimalField),
                ("desconto_contribuicao_previdenciaria", rows.fields.DecimalField),
                ("desconto_imposto_de_renda", rows.fields.DecimalField),
                ("desconto_total", rows.fields.DecimalField),
                ("rendimento_liquido", rows.fields.DecimalField),
            ]
        )
        table = rows.import_from_ods(
            self.filename, start_row=3, skip_header=False, fields=fields_inativos_2018
        )
        for row in table:
            yield self.convert_row(row)

    def extract_ativos_2018(self):
        fields_ativos_2018 = OrderedDict(
            [
                ("matricula", rows.fields.IntegerField),
                ("nome", rows.fields.TextField),
                ("cargo", rows.fields.TextField),
                ("lotacao", rows.fields.TextField),
                ("remuneracao_cargo_efetivo", rows.fields.DecimalField),
                ("remuneracao_outras", rows.fields.DecimalField),
                ("remuneracao_funcao_confianca_ou_cc", rows.fields.DecimalField),
                ("remuneracao_13o_salario", rows.fields.DecimalField),
                ("remuneracao_ferias", rows.fields.DecimalField),
                ("remuneracao_abono_de_permanencia", rows.fields.DecimalField),
                ("rendimento_bruto", rows.fields.DecimalField),
                ("desconto_contribuicao_previdenciaria", rows.fields.DecimalField),
                ("desconto_imposto_de_renda", rows.fields.DecimalField),
                ("desconto_retencao_teto", rows.fields.DecimalField),
                ("desconto_total", rows.fields.DecimalField),
                ("rendimento_liquido", rows.fields.DecimalField),
                ("auxilio_alimentacao", rows.fields.DecimalField),
                ("auxilio_transporte", rows.fields.DecimalField),
                ("auxilio_creche", rows.fields.DecimalField),
                ("auxilio_ferias_em_pecunia", rows.fields.DecimalField),
                ("remuneracao_temporaria_outras", rows.fields.DecimalField),
            ]
        )
        table = rows.import_from_ods(
            self.filename, start_row=3, skip_header=False, fields=fields_ativos_2018
        )
        for row in table:
            yield self.convert_row(row)

    def extract_mpe_sp(self):
        table = rows.import_from_ods(self.filename, start_row=0, skip_header=False)
        for row in table:
            yield self.convert_row(row)

    def extract(self):
        filename, metadata = str(self.filename), self.metadata
        if metadata["ano"] == 2018:
            if "_inativos" in filename:
                extraction_method = self.extract_inativos_2018
            else:
                if metadata["mes"] >= 6:
                    extraction_method = self.extract_ativos_2018
                else:
                    extraction_method = self.extract_mpe_sp
        else:
            extraction_method = self.extract_mpe_sp

        for row in extraction_method():
            yield row


class TJESPFileExtractor(FileExtractor):

    filename_pattern = ("SP/ORE-SP-TJE-*.*", "contracheque.csv*")
    institution = "TJE"
    state = "SP"

    def extract(self):
        filename, metadata = self.filename, self.metadata

        # From 2017-11 to 2018-12, get data from Brasil.IO (in CSV) using the
        # `extract_magistrados` helper function.
        if "contracheque.csv" in filename.name:
            yield from extract_magistrados(filename, self.state)

        else:
            ano, mes = metadata["ano"], metadata["mes"]
            extension = filename.name.lower().split(".")[-1]
            if ano == 2018 or (ano == 2017 and mes in (11, 12)):
                # Ignore this file, was processed in "contracheque.csv"
                return

            elif extension == "csv":
                encoding = detect_encoding(filename)
                dialect = detect_dialect(filename, encoding)
                with open(filename, encoding=encoding) as fobj:
                    reader = csv.DictReader(fobj, dialect=dialect)

                    # Define a field map so we can extract information from CSV and
                    # have a unified output
                    final_field_names = "cargo nome rendimento_bruto rendimento_liquido".split()
                    if "nome" in reader.fieldnames:
                        field_names = "cargo nome total_rendimentos rendimento_liquido".split()
                    elif "Nome" in reader.fieldnames:
                        field_names = ("Cargo", "Nome", "Total de Créditos", "Rendimento Liquido")
                    else:
                        raise ValueError(f"Unknown CSV header: {reader.fieldnames}")
                    field_map = {
                        old: new
                        for old, new in zip(field_names, final_field_names)
                    }

                    for row in reader:
                        data = {}
                        for old_field_name, field_name in field_map.items():
                            value = row[old_field_name]
                            if field_name in ("rendimento_bruto", "rendimento_liquido") and "," in value:
                                value = MoneyField.deserialize(value)
                            data[field_name] = value

                        yield data

            elif extension == "rds":
                # Ignore old RDS files (were converted to CSV)
                pass

            elif extension == "pdf":
                # TODO: read using OCR
                pass

            else:
                raise ValueError(f"Unknown file extension for {filename}")
