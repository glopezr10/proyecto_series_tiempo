"""Auditoría reproducible de los CSV horarios de SNIFA para Angamos 1.

Lee los archivos por bloques para evitar cargar cerca de 3 GB en memoria. Genera
una base horaria pequeña, resúmenes de calidad y una serie semanal candidata.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "Proyecto_final_ST"
OUT_DIR = ROOT / "prototipo_entrega" / "data"
TABLE_DIR = ROOT / "prototipo_entrega" / "resultados" / "tablas"

CENTRAL = "ANGAMOS"
UGE = "ANGAMOS 1"
MIN_COBERTURA_SEMANAL = 0.75
HORAS_SEMANA = 168

USECOLS = [
    "NombreCentral",
    "Chimenea",
    "UGE",
    "FECHA",
    "CONCENTRACION_NOX_MG_NM3",
    "POTENCIA_BRUTA_MWH",
    "ESTADO_UGE",
    "TIPO_DATO_NOX",
]


def periodo_desde_nombre(nombre: str) -> str | None:
    match = re.search(r"PH(\d{4}-\d)_", nombre)
    return match.group(1) if match else None


def a_numero(serie: pd.Series) -> pd.Series:
    """Convierte números con coma decimal sin alterar ausentes."""
    return pd.to_numeric(
        serie.astype("string").str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for bloque in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def leer_angamos() -> tuple[pd.DataFrame, pd.DataFrame]:
    archivos = sorted(RAW_DIR.glob("PH*.csv"))
    if not archivos:
        raise FileNotFoundError(f"No hay archivos PH*.csv en {RAW_DIR}")

    partes: list[pd.DataFrame] = []
    inventario: list[dict[str, object]] = []

    for posicion, archivo in enumerate(archivos, start=1):
        filas_archivo = 0
        filas_angamos = 0

        for bloque in pd.read_csv(
            archivo,
            sep=";",
            encoding="utf-16",
            usecols=USECOLS,
            dtype="string",
            chunksize=150_000,
            on_bad_lines="warn",
        ):
            filas_archivo += len(bloque)
            central = bloque["NombreCentral"].str.strip().str.upper()
            unidad = bloque["UGE"].str.strip().str.upper()
            seleccionado = bloque.loc[(central == CENTRAL) & (unidad == UGE)].copy()

            if seleccionado.empty:
                continue

            filas_angamos += len(seleccionado)
            seleccionado["archivo_origen"] = archivo.name
            seleccionado["periodo_archivo"] = periodo_desde_nombre(archivo.name)
            partes.append(seleccionado)

        inventario.append(
            {
                "archivo": archivo.name,
                "periodo": periodo_desde_nombre(archivo.name),
                "bytes": archivo.stat().st_size,
                "filas_archivo": filas_archivo,
                "filas_angamos_1": filas_angamos,
            }
        )
        print(
            f"[{posicion:02d}/{len(archivos):02d}] {archivo.name}: "
            f"{filas_angamos:,} filas de Angamos 1",
            flush=True,
        )

    if not partes:
        raise ValueError("No se encontraron registros de ANGAMOS / ANGAMOS 1")

    return pd.concat(partes, ignore_index=True), pd.DataFrame(inventario)


def preparar_horaria(datos: pd.DataFrame) -> pd.DataFrame:
    datos = datos.copy()
    datos["fecha"] = pd.to_datetime(
        datos["FECHA"].str.strip(),
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )
    datos["nox_mg_nm3"] = a_numero(datos["CONCENTRACION_NOX_MG_NM3"])
    datos["potencia_bruta_mwh"] = a_numero(datos["POTENCIA_BRUTA_MWH"])
    datos["tipo_dato_nox"] = datos["TIPO_DATO_NOX"].str.strip().str.upper()
    datos["estado_uge"] = datos["ESTADO_UGE"].str.strip().str.upper()
    datos["chimenea"] = datos["Chimenea"].str.strip().str.upper()
    datos["es_medicion"] = datos["tipo_dato_nox"].str.startswith("DM", na=False)
    datos["es_regimen_re"] = datos["estado_uge"].eq("RE")
    datos["valor_objetivo_valido"] = (
        datos["fecha"].notna() & datos["nox_mg_nm3"].notna() & datos["es_medicion"]
    )

    columnas = [
        "fecha",
        "nox_mg_nm3",
        "potencia_bruta_mwh",
        "tipo_dato_nox",
        "estado_uge",
        "chimenea",
        "es_medicion",
        "es_regimen_re",
        "valor_objetivo_valido",
        "archivo_origen",
        "periodo_archivo",
    ]
    return datos[columnas].sort_values(["fecha", "chimenea"], na_position="last")


def tabla_conteo(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    tabla = (
        datos[columna]
        .fillna("<AUSENTE>")
        .value_counts(dropna=False)
        .rename_axis(columna)
        .reset_index(name="n")
    )
    tabla["porcentaje"] = 100 * tabla["n"] / len(datos)
    return tabla


def construir_semanal(horaria: pd.DataFrame) -> pd.DataFrame:
    base = horaria.loc[horaria["valor_objetivo_valido"]].copy()
    if base["fecha"].duplicated().any():
        raise ValueError(
            "Existen horas duplicadas en la base válida. Revisar chimenea y rectificaciones."
        )

    semanal = (
        base.set_index("fecha")["nox_mg_nm3"]
        .resample("W-SUN")
        .agg(["count", "mean", "median", "std", "min", "max"])
        .rename(
            columns={
                "count": "horas_validas",
                "mean": "nox_media_mg_nm3",
                "median": "nox_mediana_mg_nm3",
                "std": "nox_sd_mg_nm3",
                "min": "nox_min_mg_nm3",
                "max": "nox_max_mg_nm3",
            }
        )
        .reset_index()
        .rename(columns={"fecha": "semana_fin"})
    )
    semanal["horas_esperadas"] = HORAS_SEMANA
    semanal["cobertura"] = semanal["horas_validas"] / semanal["horas_esperadas"]
    semanal["semana_utilizable"] = semanal["cobertura"] >= MIN_COBERTURA_SEMANAL

    fecha_min = base["fecha"].min().normalize()
    fecha_max = base["fecha"].max().normalize()
    semanal["semana_completa_en_periodo"] = (
        (semanal["semana_fin"] - pd.Timedelta(days=6) >= fecha_min)
        & (semanal["semana_fin"] <= fecha_max)
    )
    semanal["usar_modelamiento"] = (
        semanal["semana_utilizable"] & semanal["semana_completa_en_periodo"]
    )
    return semanal


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    cruda_filtrada, inventario = leer_angamos()
    horaria = preparar_horaria(cruda_filtrada)

    duplicados = horaria.loc[
        horaria["fecha"].notna() & horaria.duplicated("fecha", keep=False)
    ].copy()
    resumen_anual = (
        horaria.assign(anio=horaria["fecha"].dt.year)
        .groupby("anio", dropna=False)
        .agg(
            registros=("fecha", "size"),
            horas_unicas=("fecha", "nunique"),
            valores_nox=("nox_mg_nm3", "count"),
            mediciones_validas=("valor_objetivo_valido", "sum"),
            fecha_inicio=("fecha", "min"),
            fecha_fin=("fecha", "max"),
        )
        .reset_index()
    )

    semanal = construir_semanal(horaria)
    serie_modelamiento = semanal.loc[semanal["usar_modelamiento"]].copy()

    inventario.to_csv(TABLE_DIR / "00_inventario_archivos.csv", index=False)
    resumen_anual.to_csv(TABLE_DIR / "01_cobertura_anual.csv", index=False)
    tabla_conteo(horaria, "chimenea").to_csv(TABLE_DIR / "02_chimeneas.csv", index=False)
    tabla_conteo(horaria, "tipo_dato_nox").to_csv(TABLE_DIR / "03_tipo_dato_nox.csv", index=False)
    tabla_conteo(horaria, "estado_uge").to_csv(TABLE_DIR / "04_estado_uge.csv", index=False)
    duplicados.to_csv(TABLE_DIR / "05_duplicados_fecha_hora.csv", index=False)
    semanal.to_csv(TABLE_DIR / "06_auditoria_semanal.csv", index=False)
    horaria.to_csv(OUT_DIR / "angamos1_nox_horaria_filtrada.csv", index=False)
    serie_modelamiento.to_csv(OUT_DIR / "angamos1_nox_semanal.csv", index=False)

    resumen = {
        "archivos": int(len(inventario)),
        "periodo_archivos": [str(inventario["periodo"].min()), str(inventario["periodo"].max())],
        "registros_angamos": int(len(horaria)),
        "fechas_invalidas": int(horaria["fecha"].isna().sum()),
        "duplicados_fecha_hora": int(len(duplicados)),
        "valores_nox_numericos": int(horaria["nox_mg_nm3"].notna().sum()),
        "mediciones_validas": int(horaria["valor_objetivo_valido"].sum()),
        "semanas_totales": int(len(semanal)),
        "semanas_modelamiento": int(len(serie_modelamiento)),
        "porcentaje_semanas_utilizables": round(100 * len(serie_modelamiento) / max(len(semanal), 1), 2),
        "fecha_min": str(horaria["fecha"].min()),
        "fecha_max": str(horaria["fecha"].max()),
    }
    (TABLE_DIR / "resumen_auditoria.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    hash_base = sha256(OUT_DIR / "angamos1_nox_semanal.csv")
    (OUT_DIR / "angamos1_nox_semanal.sha256").write_text(
        f"{hash_base}  angamos1_nox_semanal.csv\n", encoding="ascii"
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
