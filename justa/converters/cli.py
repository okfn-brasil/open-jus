#!/usr/bin/env python
import argparse
import csv
import glob
import os
from pathlib import Path

from rows.utils import open_compressed
from tqdm import tqdm

import settings
from gender_classifier import NameClassifier
from ore import FileExtractor


def main():
    # The file pattern used to find the files may change in other operating
    # systems or running inside Docker (needs to share the volume). If that's
    # the case, just define the `--data_path` parameter.
    data_path = settings.ORE_DATA_PATH
    institutions = set(Extractor.institution for Extractor in FileExtractor.registry())
    states = set(Extractor.state for Extractor in FileExtractor.registry())
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default=data_path.absolute())
    parser.add_argument("--filename")
    parser.add_argument("--output")
    parser.add_argument("institution", choices=institutions)
    parser.add_argument("state", choices=states)
    args = parser.parse_args()
    institution, state = args.institution, args.state
    output_path = Path("data")
    data_path = Path(args.data_path)
    gender_filename = data_path / "nomes.csv.gz"

    Extractor = FileExtractor.get_child(state=args.state, institution=args.institution)
    if args.filename:
        filenames = [data_path / args.filename]
    else:
        patterns = Extractor.filename_pattern
        if isinstance(patterns, str):
            patterns = [patterns]
        filename_patterns = [data_path / pattern for pattern in patterns]
        filenames = sorted(
            Path(filename)
            for filename_pattern in filename_patterns
            for filename in glob.glob(str(filename_pattern))
        )
    output_filename = (
        args.output or output_path / f"ore-{institution.lower()}-{state.lower()}.csv.gz"
    )
    if not output_filename.parent.exists():
        output_filename.parent.mkdir(parents=True)
    desc = f"{institution} {state}"

    field_names = (
        "ano",
        "mes",
        "instituicao",
        "uf",
        "cargo",
        "nome",
        "genero",
        "rendimento_bruto",
        "rendimento_liquido",
        "observacao",
    )
    gender_classifier = NameClassifier(gender_filename)
    gender_classifier.load()
    fobj = open_compressed(output_filename, mode="w", encoding="utf-8")
    writer = csv.DictWriter(fobj, fieldnames=field_names)
    writer.writeheader()
    for filename in tqdm(filenames, desc=desc):
        extractor = Extractor(filename)
        for row in extractor.data:
            nome = row["nome"]
            row["genero"] = gender_classifier.classify(nome) if nome else ""
            writer.writerow(row)
        # TODO: should force types anywhere here or in FileExtractor?
    fobj.close()


if __name__ == "__main__":
    main()
