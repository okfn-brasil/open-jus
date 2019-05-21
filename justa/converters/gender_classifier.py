import csv
from decimal import Decimal
from pathlib import Path

from rows.utils import open_compressed, slug


class NameClassifier:
    def __init__(self, filename):
        self.filename = filename
        self.cache = {}

    def load(self):
        fobj = open_compressed(self.filename, encoding="utf-8")
        reader = csv.DictReader(fobj)
        for row in reader:
            if Decimal(row["ratio"]) < 0.95:
                continue
            self.cache[row["first_name"]] = row["classification"]
        fobj.close()

    def classify(self, name):
        if not self.cache:
            raise RuntimeError("Classification cache not loaded (must call .load())")
        name = slug(name).split("_")[0].upper()
        result = self.cache.get(name, None)
        if result in (None, ""):
            return None
        else:
            return result


if __name__ == "__main__":
    # Download this file from:
    # <https://dataset.brasil.io/genero-nomes/nomes.csv.gz>
    filename = Path(__file__).parent.parent.parent / "data" / "nomes.csv.gz"
    gender_classifier = NameClassifier(filename)
    gender_classifier.load()
