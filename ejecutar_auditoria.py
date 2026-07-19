"""Compatibilidad con los CSV SNIFA sin marca BOM; ejecuta la auditoría."""

import pandas as pd

_read_csv = pd.read_csv


def _read_csv_snifa(*args, **kwargs):
    if kwargs.get("encoding") == "utf-16":
        kwargs["encoding"] = "utf-16-le"
    return _read_csv(*args, **kwargs)


pd.read_csv = _read_csv_snifa

import auditoria_snifa


if __name__ == "__main__":
    auditoria_snifa.main()
