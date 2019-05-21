#!/usr/bin/env python
import argparse
import glob
import os
from pathlib import Path

import rows


class MoneyField(rows.fields.DecimalField):
    """Field to deserialize Brazilian money (like '1.234,56') into Decimal"""

    @classmethod
    def deserialize(cls, value):
        value = (value or "").replace(".", "").replace(",", ".")
        return super().deserialize(value)


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
ADD_TO_NEW = ("um_terco_ferias_e_decimo_terceiro", "devolucao_debito", "outras_indenizacoes")
ADD_TO_OLD = ("um_terco_ferias", "decimo_terceiro", "atividades_dias_nao_uteis", "total")
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


def extract_metadata(filename):
    """Extract metadata from filename"""

    info = filename.name.split(".pdf")[0].split("-")
    assert info[0] == "ORE"
    return {
        "uf": info[1],
        "instituicao": info[2],
        "ano": int("20" + info[3][:2]),
        "mes": int(info[3][2:]),
        "observacao": info[4],
    }


def convert_row(row, old=False):
    """Given a table line from the PDF, converts to final dict"""

    header = HEADER_NEW
    if old:
        header = HEADER_OLD

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
    if not old and len(fixed_row) == 13:
        fixed_row.insert(6, None)
    elif old and len(fixed_row) == 12:
        fixed_row.insert(5, None)
    row = dict(zip(header, fixed_row))
    if " " in row["atrasados"]:
        references = []
        parts = row["atrasados"].replace("\n", " ").split()
        for part in parts:
            if "/" not in part:
                row["atrasados"] = part
            else:
                references.append(part)
        row["referencia_atrasados"] = " ".join(references)

    if old:
        for key in ADD_TO_OLD:
            row[key] = None
    else:
        for key in ADD_TO_NEW:
            row[key] = None

    return row


def parse_ore_pdf(filename):
    """Parse a SP-DPE PDF and yield rows (dicts)"""

    pages = rows.plugins.pdf.number_of_pages(filename)
    metadata = extract_metadata(filename)
    old = (
        metadata["ano"] in (2013, 2014, 2015)
        or metadata["ano"] == 2016 and metadata["mes"] <= 11
    )
    if old:
        starts_after = "INDENIZ."
    else:
        starts_after = "INDEN.)"

    for page in range(2, pages + 1):
        table = rows.plugins.pdf.pdf_table_lines(
            filename, page_numbers=(page,), starts_after=starts_after
        )
        for row_data in table:
            if not row_data[0]:  # Almost empty header line
                continue
            row = convert_row(row_data, old)
            row.update(metadata)
            yield row


if __name__ == "__main__":
    # The file pattern used to find the PDFs may change in other operating
    # systems or running inside Docker (needs to share the volume). If that's
    # the case, just define the `--path_path` command-line parameter.
    pdf_path = (
        Path(os.path.expanduser("~"))
        / "Dropbox"
        / "Justa_dados/Dados/ETAPA_0/Eixo_ORE/SP/"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_path", default=pdf_path.absolute())
    parser.add_argument("--filename", default="")
    parser.add_argument("--output", default="ore-dpe-sp.csv")
    args = parser.parse_args()
    if args.filename:
        filenames = [Path(args.pdf_path) / args.filename]
    else:
        file_pattern = Path(args.pdf_path) / "ORE-SP-DPE-*.pdf"
        filenames = sorted(glob.glob(str(file_pattern)))

    result = []
    total = len(filenames)
    for counter, filename in enumerate(filenames, start=1):
        basename = Path(filename).name
        print(f"[{counter:02d}/{total:02d}] {basename:40}:", end="")
        data = list(parse_ore_pdf(Path(filename)))
        result.extend(data)
        print(f" {len(data)} rows extracted")
    table = rows.import_from_dicts(result, force_types=TYPES)
    rows.export_to_csv(table, args.output)
