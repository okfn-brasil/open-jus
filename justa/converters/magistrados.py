import csv

from rows.utils import open_compressed


TRIBUNAL_UF = {
    "Tribunal de Justiça de São Paulo": "SP",
    "Tribunal de Justiça do Ceará": "CE",
    "Tribunal de Justiça do Paraná": "PR",
}


def extract_magistrados(filename, uf):
    for nome, sigla in TRIBUNAL_UF.items():
        if sigla == uf:
            tribunal = nome
            break

    reader_fobj = open_compressed(filename, mode="r", encoding="utf-8")
    for row in csv.DictReader(reader_fobj):
        row_ano, row_tribunal = row["ano_de_referencia"], row["tribunal"]
        if row_ano in ("2017", "2018") and row_tribunal == tribunal:
            yield {
                "ano": row_ano,
                "cargo": row["cargo"],
                "instituicao": "TJE",
                "mes": row["mes_de_referencia"],
                "nome": row["nome"],
                "observacao": "",
                "rendimento_bruto": row["total_de_rendimentos"],
                "rendimento_liquido": row["rendimento_liquido"],
                "uf": TRIBUNAL_UF[row_tribunal],
            }
