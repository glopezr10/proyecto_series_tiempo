"""Ejecutor del modelado con herramientas utilizadas en la asignatura."""

import pandas as pd

import prototipo_modelado as piloto


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
    piloto.main()
