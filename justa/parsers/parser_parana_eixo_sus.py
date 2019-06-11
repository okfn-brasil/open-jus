import click
import glob
import os
import shutil

from collect_data_parana_sus import collect_data, create_csv


curpath = os.path.abspath(os.curdir)

@click.command()
@click.option('--folder', prompt='folder name',
             help='Folder with all files in PDF extension for data extraction.')


def main(folder):
    output = curpath+'/output_'+folder
    os.mkdir(output)

    process_list = glob.glob(folder+"/*.pdf")
    if len(process_list) > 0:
        click.echo('Collecting data from PDFs.')
        collect_data(process_list)
        click.echo('Generating a csv file.')
        create_csv(output)


if __name__ == '__main__':
    try:
        main()
    except(FileExistsError):
        click.echo('Data in this folder has already been collected.')
