import re

from cached_property import cached_property


regexp_year = re.compile("-([0-9]{4})[-_]")


class FileExtractor:

    __registry = []

    @classmethod
    def register(cls, child):
        cls.__registry.append(child)

    @classmethod
    def registry(cls):
        return cls.__registry

    @classmethod
    def get_child(cls, institution, state):
        for child in cls.__registry:
            if child.institution == institution and child.state == state:
                return child
        raise RuntimeError(f"There's no class registered for {institution}/{state}.")

    def __init__(self, filename):
        self.filename = filename

    @cached_property
    def metadata(self):
        """Extract metadata from filename"""
        # TODO: test
        if "contracheque.csv" in self.filename.name:
            return {
                "observacao": "CNJ",
            }

        extension = self.filename.name.split(".")[-1]
        year_month = regexp_year.findall(self.filename.name)[0]
        year, month = year_month[:2], year_month[2:]
        info = self.filename.name[: -len(extension) - 1].split("-")
        assert info[0] == "ORE"
        data = {
            "ano": int("20" + year),
            "instituicao": info[2],
            "mes": int(month),
            "uf": info[1],
        }
        data["observacao"] = self.filename.name[
            len(f"ORE-{data['uf']}-{data['instituicao']}-") : -len(extension) - 1
        ]
        return data

    def extract(self):
        raise NotImplementedError()

    @property
    def data(self):
        metadata = self.metadata
        for row in self.extract():
            row.update(metadata)
            yield row

    # TODO: create cached_property field_names and fill automatically
