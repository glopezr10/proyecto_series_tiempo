# Prototipo de entrega

Esta carpeta contiene una versión completa y reproducible construida desde los requisitos finales de la pauta.

## Entregables principales

- `Trabajo_Final_Series_Tiempo.ipynb`: notebook narrativo.
- `INFORME_EJECUTIVO.md`: informe listo para revisión y conversión con Pandoc.
- `INFORME_EJECUTIVO.docx`: versión Word preliminar con portada, estilos, tablas y figuras.
- `data/angamos1_nox_horaria_filtrada.csv`: base horaria reducida y trazable.
- `data/angamos1_nox_semanal_modelo.csv`: base semanal efectivamente modelada.
- `resultados/tablas/`: métricas, auditoría y pronóstico.
- `resultados/figuras/`: gráficos en formato PNG.

## Reconstrucción

Desde la raíz del proyecto y con el entorno `series-tiempo-darts`:

```powershell
python ejecutar_auditoria.py
python ejecutar_modelado_final.py
python integrar_autoreg.py
python crear_notebook_piloto.py
```

## Conversión del informe a Word

Desde `prototipo_entrega/`:

```powershell
pandoc INFORME_EJECUTIVO.md -o INFORME_EJECUTIVO.docx --resource-path=.
```

Los códigos operacionales y de calidad ya fueron contrastados con la Resolución Exenta SMA N.º 404/2017 y quedaron documentados en `CODIGOS_OFICIALES.md`. El Word pasó controles estructurales y de accesibilidad; antes de entregar resta abrirlo en Microsoft Word para la revisión visual final, además de revisar nombres y ortografía.
