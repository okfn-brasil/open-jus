import pathlib

from ore_dpe_sp import convert_row, extract_metadata


def test_extract_metadata():
    output = extract_metadata(
        pathlib.Path("Dropbox/.../ORE-SP-DPE-1501-L180731_ativos.pdf")
    )
    expected = {
        "uf": "SP",
        "instituicao": "DPE",
        "ano": 2015,
        "mes": 1,
        "observacao": "L180731_ativos",
    }
    assert output == expected


def test_convert_row():
    output = convert_row(
        [
            "Ana Carolina Minutti Nori",
            "Defensor Público do Estado",
            "29.376,29",
            "0,00",
            "0,00",
            "0,00",
            "-14.229,16",
            "15.147,13",
            "0,00",
            "0,00",
            "667,95",
            "840,00",
            "16.655,08",
        ]
    )
    expected = {
        "nome": "Ana Carolina Minutti Nori",
        "cargo": "Defensor Público do Estado",
        "total_bruto": "29.376,29",
        "um_terco_ferias": "0,00",
        "decimo_terceiro": "0,00",
        "atrasados": "0,00",
        "descontos": "-14.229,16",
        "rendimento_liquido": "15.147,13",
        "diarias": "0,00",
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "667,95",
        "auxilio_alimentacao": "840,00",
        "total": "16.655,08",
        "referencia_atrasados": None,
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Aluisio Iunes Monti Ruggeri Re\nDefensor Público do Estado",
            "29.630,37",
            "0,00",
            "0,00",
            "47,46",
            "jan/2018",
            "-15.961,72",
            "13.716,11",
            "0,00",
            "0,00",
            "2.671,80",
            "960,00",
            "17.347,91",
        ]
    )
    expected = {
        "nome": "Aluisio Iunes Monti Ruggeri Re",
        "cargo": "Defensor Público do Estado",
        "total_bruto": "29.630,37",
        "um_terco_ferias": "0,00",
        "decimo_terceiro": "0,00",
        "atrasados": "47,46",
        "referencia_atrasados": "jan/2018",
        "descontos": "-15.961,72",
        "rendimento_liquido": "13.716,11",
        "diarias": "0,00",
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "2.671,80",
        "auxilio_alimentacao": "960,00",
        "total": "17.347,91",
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Ana Carvalho Ferreira Bueno De\nMoraes",
            "Defensor Público do Estado",
            "30.471,11",
            "0,00",
            "0,00",
            "0,00",
            "-12.463,39",
            "18.007,72",
            "0,00",
            "0,00",
            "0,00",
            "800,00",
            "18.807,72",
        ]
    )
    expected = {
        "nome": "Ana Carvalho Ferreira Bueno De Moraes",
        "cargo": "Defensor Público do Estado",
        "total_bruto": "30.471,11",
        "um_terco_ferias": "0,00",
        "decimo_terceiro": "0,00",
        "atrasados": "0,00",
        "descontos": "-12.463,39",
        "rendimento_liquido": "18.007,72",
        "diarias": "0,00",
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "0,00",
        "auxilio_alimentacao": "800,00",
        "total": "18.807,72",
        "referencia_atrasados": None,
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Paulo Ricardo De Divitiis Filho",
            "Defensor Público do Estado",
            "23.960,56",
            "0,00",
            "0,00",
            "2.764,68\nfev/2017",
            "-8.239,93",
            "18.485,31",
            "307,20",
            "0,00",
            "614,37",
            "828,00",
            "20.234,88",
        ]
    )
    expected = {
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "614,37",
        "atrasados": "2.764,68",
        "auxilio_alimentacao": "828,00",
        "cargo": "Defensor Público do Estado",
        "decimo_terceiro": "0,00",
        "descontos": "-8.239,93",
        "diarias": "307,20",
        "nome": "Paulo Ricardo De Divitiis Filho",
        "referencia_atrasados": "fev/2017",
        "rendimento_liquido": "18.485,31",
        "total": "20.234,88",
        "total_bruto": "23.960,56",
        "um_terco_ferias": "0,00",
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Pietro Da Silva Estabile",
            "Defensor Público do Estado",
            "30.457,56",
            "5.076,26",
            "10.160,20",
            "2.764,68 jun/2016 jul/2016\nout/2016",
            "-16.167,13",
            "32.291,57",
            "204,80",
            "0,00",
            "0,00",
            "828,00",
            "33.324,37",
        ]
    )
    expected = {
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "0,00",
        "atrasados": "2.764,68",
        "auxilio_alimentacao": "828,00",
        "cargo": "Defensor Público do Estado",
        "decimo_terceiro": "10.160,20",
        "descontos": "-16.167,13",
        "diarias": "204,80",
        "nome": "Pietro Da Silva Estabile",
        "referencia_atrasados": "jun/2016 jul/2016 out/2016",
        "rendimento_liquido": "32.291,57",
        "total": "33.324,37",
        "total_bruto": "30.457,56",
        "um_terco_ferias": "5.076,26",
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Rafael Barcelos Tristao",
            "Defensor Público do Estado",
            "25.803,68",
            "0,00",
            "0,00",
            "dez/2016\n3.686,24\nfev/2017",
            "-9.324,21",
            "20.165,71",
            "307,20",
            "0,00",
            "3.071,85",
            "828,00",
            "24.372,76",
        ]
    )
    expected = {
        "nome": "Rafael Barcelos Tristao",
        "cargo": "Defensor Público do Estado",
        "total_bruto": "25.803,68",
        "um_terco_ferias": "0,00",
        "decimo_terceiro": "0,00",
        "atrasados": "3.686,24",
        "descontos": "-9.324,21",
        "rendimento_liquido": "20.165,71",
        "diarias": "307,20",
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "3.071,85",
        "auxilio_alimentacao": "828,00",
        "total": "24.372,76",
        "referencia_atrasados": "dez/2016 fev/2017",
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Aurea Maria De Oliveira Manoel",
            "Defensor Público do Estado",
            "24.006,64",
            "0,00",
            "0,00",
            "abr/2017\n3.686,24\nmai/2017\nset/2017",
            "-9.660,67",
            "18.032,21",
            "0,00",
            "0,00",
            "0,00",
            "720,00",
            "0,00",
            "18.752,21",
        ]
    )
    expected = {
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": "720,00",
        "atrasados": "3.686,24",
        "auxilio_alimentacao": "0,00",
        "cargo": "Defensor Público do Estado",
        "decimo_terceiro": "0,00",
        "descontos": "18.032,21",
        "diarias": "0,00",
        "nome": "Aurea Maria De Oliveira Manoel",
        "referencia_atrasados": "abr/2017 mai/2017 set/2017",
        "rendimento_liquido": "0,00",
        "total": "18.752,21",
        "total_bruto": "24.006,64",
        "um_terco_ferias": "0,00",
        "devolucao_debito": None,
        "outras_indenizacoes": None,
        "um_terco_ferias_e_decimo_terceiro": None,
    }
    assert output == expected

    output = convert_row(
        [
            "Adele Aparecida Fernandes Morais",
            "Defensor Público do Estado",
            "19.520,81",
            "0,00",
            "7.864,50",
            "nov/2012 dez/2012",
            "-7.759,57",
            "19.625,74",
            "2.019,60",
            "0,00",
            "0,00",
            "0,00",
            "0,00",
        ],
        old=True,
    )
    expected = {
        "abono_permanencia": "0,00",
        "atividades_dias_nao_uteis": None,
        "atrasados": "7.864,50",
        "auxilio_alimentacao": "0,00",
        "cargo": "Defensor Público do Estado",
        "decimo_terceiro": None,
        "descontos": "-7.759,57",
        "devolucao_debito": "0,00",
        "diarias": "2.019,60",
        "nome": "Adele Aparecida Fernandes Morais",
        "outras_indenizacoes": "0,00",
        "referencia_atrasados": "nov/2012 dez/2012",
        "rendimento_liquido": "19.625,74",
        "total": None,
        "total_bruto": "19.520,81",
        "um_terco_ferias": None,
        "um_terco_ferias_e_decimo_terceiro": "0,00",
    }
    assert output == expected
