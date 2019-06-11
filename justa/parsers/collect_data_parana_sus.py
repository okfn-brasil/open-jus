import csv
import glob
import os
import re
import textract


curpath = os.path.abspath(os.curdir)

key_words = {
    'petitioner_words': ['REQUERENTES:', 'REQUERENTE:', 'AGRAVADO:', 'EMBARGADO:', 'REQUERENTE :', 'Requerente:'],
    'requested_words': ['REQUERIDO:', 'AGRAVANTE:', 'INTERESSADOS:', 'INTERESSADA:', 'INTERESSADO:']
}

def collect_data(process_list):
    for filename in process_list:
        text = textract.process(filename, method='pdftotext')
        with open(curpath+"/output_"+filename+".txt", "w+") as text_file:
            text_file.write(filename+'; '+text.decode())

def create_csv(output):
    with open(output+'/sus_pr.csv', 'w+') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['id', 'source', 'number', 'decision', 'decision_date', 'year',
                             'status', 'source_numbers', 'reporter', 'category',
                             'petitioner', 'requested', 'judicial_organ', 'publication_date'])

        data_list = glob.glob(output+"/*.txt")
        for index, data in enumerate(data_list):
            row = {
                'id': None, 'source': None, 'number': None, 'decision': '', 'decision_date': None, 'year': None,
                'status': None, 'source_numbers': None, 'reporter': None, 'category': None,
                'petitioner': None, 'requested': None, 'judicial_organ': None, 'publication_date': None
            }
            row['id'] = index+1
            with open(data, 'r') as data_file:
                decision_creator = False

                lines = data_file.readlines()
                for index_line, line in enumerate(lines):
                    if decision_creator:
                        if not row['petitioner']:
                            if '1. ' in line and ('Câmara Municipal' in line or 'Estado do Paraná' in line):
                                row['petitioner'] = line.replace('\n', ' ').replace('1. ', '')
                            elif any(word in line for word in key_words['petitioner_words']):
                                row['petitioner'] = line.replace('\n', ' ')

                        row['decision'] += line.replace('\n', ' ')
                        if 'Acessado em: ' in line:
                            row['decision'] = row['decision']
                            row['decision'] = "'"+row['decision']+";'"
                            decision_creator = False
                    if ('Jurisprudência - TJPR' in line or 'Jurisprudência - TJPR' in line) and not row['source']:
                        row['source'] = 'TJPR'
                        row['number'] = lines[index_line+2][:-1].replace('Processo: ', '')
                        
                        if len(lines[index_line+3]) > 1:
                            row['reporter'] = lines[index_line+3][:-1].replace('Relator: ', '')
                        else:
                            row['reporter'] = lines[index_line+4][:-1].replace('Relator: ', '')

                        if len(lines[index_line+4]) > 1 and not row['reporter'] in lines[index_line+4]:
                            row['judicial_organ'] = lines[index_line+4][:-1].replace('Orgão Julgador: ', '')
                            if 'Publicação:' in lines[index_line+6]:
                                row['publication_date'] = lines[index_line+5][:-1].replace('Data de ', '')
                            else:
                                row['publication_date'] = lines[index_line+6][:-1].replace('Data de ', '')
                        elif row['reporter'] in lines[index_line+4]:
                            row['judicial_organ'] = lines[index_line+6][:-1].replace('Orgão Julgador: ', '')
                            row['publication_date'] = lines[index_line+8][:-1].replace('Data de ', '')
                        else:
                            row['judicial_organ'] = lines[index_line+5][:-1].replace('Orgão Julgador: ', '')
                            row['publication_date'] = lines[index_line+7][:-1].replace('Data de ', '')

                    elif ('Íntegra:' in line) and row['decision'] == '':
                        if 'segredo de justiça' in line:
                            row['source'] = 'TJPR'
                            row['number'] = lines[index_line-5][:-1].replace('Processo: ', '')
                            row['reporter'] = lines[index_line-4][:-1].replace('Relator: ', '')
                            row['judicial_organ'] = lines[index_line-3][:-1].replace('Orgão Julgador: ', '')
                            row['publication_date'] = lines[index_line-2][:-1].replace('Data de ', '')
                            row['decision'] = 'Não disponível- Segredo de justiça.'
                        else:
                            if ('PARANÁ.' in lines[index_line+1] or 'Estado do Paraná' in lines[index_line]) and not row['petitioner']:
                                row['petitioner'] = 'ESTADO DO PARANÁ'
                            elif ('Município' in lines[index_line] or 'MUNICÍPIO' in lines[index_line]) and not row['petitioner']:
                                print(lines[index_line])
                                row['petitioner'] = lines[index_line][-1]
                            decision_creator = True
                    elif any(word in line for word in key_words['petitioner_words']) and not row['petitioner']:
                        row['petitioner'] = lines[index_line][:-1]
                    elif any(word in line for word in key_words['requested_words']) and not row['requested']:
                        row['requested'] = lines[index_line][:-1]
                    if (bool(re.search('^Curitiba, [0-9]*(°| )', line)) or 'Acessado em: ' in line) and not row['decision_date']:
                        row['decision_date'] = lines[index_line][:-1].replace(',', '.')
                        start, end = re.search('[0-9]{4}', row['decision_date']).span(0)
                        row['year'] = row['decision_date'][start:end]

            os.remove(data)
            filewriter.writerow([row['id'], row['source'], row['number'], row['decision'], row['decision_date'],
                                 row['year'], '', '', row['reporter'], '', row['petitioner'], row['requested'],
                                 row['judicial_organ'], row['publication_date']])
