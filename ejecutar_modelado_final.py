"""Ejecutor del modelado con herramientas utilizadas en la asignatura."""

import pandas as pd

import modelado_series as modelado


_reset_index = pd.Series.reset_index


def reset_index_compatible(self, *args, **kwargs):
    """Mantiene compatibilidad con pandas 1.5 del entorno del curso."""
    names = kwargs.pop("names", None)
    resultado = _reset_index(self, *args, **kwargs)
    if names is not None:
        resultado = resultado.rename(columns={resultado.columns[0]: names})
    return resultado


pd.Series.reset_index = reset_index_compatible


if __name__ == "__main__":
    modelado.main()
