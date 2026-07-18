"""Inserta el análisis de sensibilidad en el informe y en el notebook."""

import json
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTO = ROOT / "prototipo_entrega"
REPORT = PROTO / "INFORME_EJECUTIVO.md"
NOTEBOOK = PROTO / "Trabajo_Final_Series_Tiempo.ipynb"


REPORT_SECTION = """<!-- SENSIBILIDAD_INICIO -->
# 8.1 Análisis de sensibilidad

Se evaluó el mismo modelo AutoReg bajo cinco construcciones de la serie para determinar si la conclusión dependía del umbral de cobertura, las diez interpolaciones, el estadístico semanal o el estado operacional.

| Escenario | Semanas imputadas | RMSE validación | RMSE prueba | Ljung-Box p(10) | Pronóstico medio 8 semanas |
|---|---:|---:|---:|---:|---:|
| Media, cobertura 75% | 10 | 40,02 | 27,53 | 0,713 | 310,62 |
| Media, cobertura 50% | 1 | 39,32 | 29,24 | 0,715 | 313,98 |
| Media, sin umbral | 0 | 39,28 | 29,27 | 0,713 | 313,94 |
| Mediana, cobertura 75% | 10 | 48,52 | 36,54 | 0,992 | 295,80 |
| Media DM+RE, cobertura 75% | 25 | 37,84 | 31,62 | 0,054 | 296,64 |

![Sensibilidad del RMSE de prueba](resultados/figuras/09_sensibilidad_construccion_serie.png){width=90%}

La familia AutoReg mantuvo residuos compatibles con ruido blanco en todos los escenarios. Reducir el umbral al 50% o utilizar todas las medias semanales produjo resultados muy cercanos, por lo que las diez interpolaciones de la especificación principal no determinan por sí solas la conclusión. La mediana y la restricción al estado `RE` redujeron el nivel pronosticado y empeoraron el RMSE de prueba.

![Sensibilidad del pronóstico](resultados/figuras/10_sensibilidad_pronostico.png){width=90%}

Se conserva como especificación principal la media de datos medidos con cobertura mínima del 75% porque corresponde al objetivo de concentración semanal general y presenta el menor RMSE de prueba. La diferencia de nivel observada bajo `DM+RE` se reporta como limitación sustantiva y muestra que el pronóstico no debe reinterpretarse como concentración exclusiva durante operación en régimen.
<!-- SENSIBILIDAD_FIN -->

"""


def markdown_cell(text):
    return {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {"tags": ["sensibilidad"]},
        "source": text.splitlines(keepends=True),
    }


def code_cell(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uuid.uuid4().hex[:8],
        "metadata": {"tags": ["sensibilidad"]},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


def actualizar_informe():
    text = REPORT.read_text(encoding="utf-8")
    start = "<!-- SENSIBILIDAD_INICIO -->"
    end = "<!-- SENSIBILIDAD_FIN -->"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before.rstrip() + "\n\n" + after.lstrip()
    marker = "# 9. Conclusiones"
    if marker not in text:
        raise ValueError("No se encontró la sección de conclusiones del informe")
    text = text.replace(marker, REPORT_SECTION + marker, 1)
    REPORT.write_text(text, encoding="utf-8")


def actualizar_notebook():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    nb["cells"] = [
        cell
        for cell in nb["cells"]
        if "sensibilidad" not in cell.get("metadata", {}).get("tags", [])
    ]
    index = next(
        i
        for i, cell in enumerate(nb["cells"])
        if "## 9. Conclusiones" in "".join(cell.get("source", []))
    )
    nuevas = [
        markdown_cell(
            """## 8.1 Análisis de sensibilidad

Se mantuvo el modelo AutoReg y se modificó la construcción de la serie: umbral 50%, ausencia de umbral, mediana semanal y restricción a mediciones en estado `RE`. Esto permite separar la estabilidad del modelo de las decisiones de limpieza."""
        ),
        code_cell(
            """sensibilidad = pd.read_csv(TABLES / "12_analisis_sensibilidad.csv")
display(sensibilidad.style.format({
    "correlacion_con_base": "{:.3f}",
    "validacion_RMSE": "{:.2f}", "prueba_RMSE": "{:.2f}",
    "prueba_MAE": "{:.2f}", "ljung_p_10": "{:.3f}",
    "ljung_p_20": "{:.3f}", "pronostico_medio_8s": "{:.2f}"
}))
display(Image(filename=str(FIGURES / "09_sensibilidad_construccion_serie.png")))
display(Image(filename=str(FIGURES / "10_sensibilidad_pronostico.png")))"""
        ),
        markdown_cell(
            """AutoReg mantuvo residuos compatibles con ruido blanco en los cinco escenarios. Los resultados con umbral 50% y sin umbral fueron cercanos a la especificación principal, por lo que las diez interpolaciones no explican por sí solas el resultado. La mediana y la restricción `DM+RE` redujeron el nivel esperado hacia 296 mg/Nm³ y aumentaron el RMSE de prueba.

Según la Resolución Exenta SMA N.º 404/2017, `RE` corresponde a operación en régimen. Se conserva la media de todos los datos medidos con cobertura 75% porque corresponde al objetivo de concentración semanal general y presenta el menor RMSE de prueba. `DM+RE` responde a una pregunta distinta: concentración medida durante operación en régimen."""
        ),
    ]
    nb["cells"][index:index] = nuevas
    NOTEBOOK.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    actualizar_informe()
    actualizar_notebook()
    print(REPORT)
    print(NOTEBOOK)
