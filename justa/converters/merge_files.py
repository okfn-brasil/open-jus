import csv
import glob
from decimal import Decimal
from pathlib import Path

from rows.utils import open_compressed
from tqdm import tqdm


def read_csv(filename):
    fobj = open_compressed(filename, mode="r", encoding="utf-8")
    yield from csv.DictReader(fobj)
    fobj.close()


field_translation = {
    "ano": ("ano",),
    "instituicao": ("instituicao",),
    "mes": ("mes",),
    "uf": ("uf",),
    "observacao": ("observacao",),
    "genero": ("genero",),
    "nome": ("nome",),
    "cargo": ("cargo",),
    "rendimento_bruto": ("rendimento_bruto", "total_bruto", "total_rendimentos"),
    "rendimento_liquido": ("rendimento_liquido",),
}

# TODO: use settings.*DATA*
base_path = Path(__file__).parent.parent.parent
output_filename = base_path / "data" / "consolidado.csv.gz"
filename_pattern = (
    base_path / "justa/converters/data" / "ore-*.csv*"
)  # TODO: may change to .csv.gz
fobj = open_compressed(output_filename, mode="w", encoding="utf-8")
writer = csv.DictWriter(fobj, fieldnames=list(field_translation.keys()))
writer.writeheader()
for filename in tqdm(glob.glob(str(filename_pattern))):
    for row in read_csv(filename):
        data = {}

        # TODO: move these convertions to extractors
        for key, possible_field_names in field_translation.items():
            for field_name in possible_field_names:
                if field_name in row:
                    data[key] = row[field_name]
                    break

        if not data["rendimento_liquido"] and "ore-mpe-sp.csv" in filename:
            if data["rendimento_liquido"] and row["desconto_total"]:
                data["rendimento_liquido"] = str(
                    Decimal(data["rendimento_liquido"]) - Decimal(row["desconto_total"])
                )
fobj.close()
