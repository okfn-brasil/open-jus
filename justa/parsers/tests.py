import pytest_regressions
import glob
import os
import shutil

import parser_parana_eixo_sus

def run_parser_parana():
    filename = 'output_tests'
    if os.path.exists(filename) and os.path.isdir(filename):
        shutil.rmtree(filename)
    
    os.system('python parser_parana_eixo_sus.py --folder tests')
    files = glob.glob("output_tests/*.txt")
    with open('output_tests/sus_pr.csv') as data:
        data_lines = data.readlines()
    return {
        "Data": {
            "columns": data_lines[0],
            "lines": data_lines[1:],
        },
    }

def test_parser_parana(data_regression):
    data = run_parser_parana()
    data_regression.check(data)
    shutil.rmtree('output_tests')
