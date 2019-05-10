import rows
import rows.utils


class MoneyField(rows.fields.DecimalField):
    """Field to deserialize Brazilian money (like '1.234,56') into Decimal"""

    @classmethod
    def deserialize(cls, value):
        value = (
            (value or "")
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .replace("- ", "-")
            .strip()
        )
        return super().deserialize(value)


def detect_dialect(filename, encoding, sample_size=1024 * 1024):
    with open(filename, mode="rb") as fobj:
        sample = fobj.read(sample_size)
    return rows.plugins.csv.discover_dialect(sample, encoding)


def detect_encoding(filename):
    return rows.utils.detect_source(str(filename), verify_ssl=False, progress=False).encoding
