# Justa Converters

## Install dependencies

```bash
pip install -r requirements.txt
```

## Preparing Input Data

There are two main folders:

- Files from shared Dropbox folder
- Files from `data-to-copy/`

By default the script will try to figure out the Dropbox folder (you
can change the `ORE_DATA_PATH` variable inside `settings.py` if needed)
to read files from shared folder `Justa_dados/Dados/ETAPA_0/Eixo_ORE`.

Before running, copy the files inside `data-to-copy/` to the Dropbox shared
folder.

## Running

Just execute `cli.py` with the desired institution and state:

```bash
python cli.py {MPE,DPE,TJE} {CE,PR,SP}

```

The files will be read from the Dropbox shared folder and saved into
`data/ore-{institution}-{state}.csv.gz`.
