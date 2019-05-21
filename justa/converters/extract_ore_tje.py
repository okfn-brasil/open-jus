import csv
from pathlib import Path

from rows.utils import open_compressed
from tqdm import tqdm

from gender_classifier import NameClassifier


def convert_row(row):
    nome = row["nome"]
    if nome:
        genero = gender_classifier.classify(nome)
    else:
        genero = ""

    tribunal = row["tribunal"]
    if "São Paulo" in tribunal:
        uf = "SP"
    elif "Paraná" in tribunal:
        uf = "PR"
    elif "Ceará" in tribunal:
        uf = "CE"

    return {
        "ano": row["ano_de_referencia"],
        "genero": genero,
        "instituicao": "TJE",
        "mes": row["mes_de_referencia"],
        "uf": uf,
        "observacao": "",
        "nome": nome,
        "cargo": row["cargo"],
        "rendimento_bruto": row["total_de_rendimentos"],
        "rendimento_liquido": row["rendimento_liquido"],
    }


DATA_PATH = Path(__file__).parent.parent.parent / "data"
TRIBUNAIS = [
    "Tribunal de Justiça de São Paulo",
    "Tribunal de Justiça do Paraná",
    "Tribunal de Justiça do Ceará",
]
output_field_names = [
    "ano",
    "mes",
    "instituicao",
    "uf",
    "observacao",
    "genero",
    "nome",
    "cargo",
    "rendimento_bruto",
    "rendimento_liquido",
]
input_filename = DATA_PATH / "contracheque.csv.gz"
output_filename = DATA_PATH / "ore-tje.csv.gz"
gender_filename = DATA_PATH / "nomes.csv.gz"

gender_classifier = NameClassifier(gender_filename)
gender_classifier.load()

reader_fobj = open_compressed(input_filename, mode="r", encoding="utf-8")
reader = csv.DictReader(reader_fobj)
output_fobj = open_compressed(output_filename, mode="w", encoding="utf-8")
writer = csv.DictWriter(output_fobj, fieldnames=output_field_names)
writer.writeheader()

for row in tqdm(reader):
    if row["tribunal"] in TRIBUNAIS:
        writer.writerow(convert_row(row))

output_fobj.close()
