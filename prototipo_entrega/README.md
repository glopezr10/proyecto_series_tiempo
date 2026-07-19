# Trabajo final de Series de Tiempo

Esta carpeta contiene la base de desarrollo de la entrega final. El notebook, el informe Markdown y las bases reducidas son los artefactos canónicos; las tablas, figuras y documentos auxiliares sirven como evidencia y apoyo para su revisión.

El estado de cumplimiento y las decisiones pendientes se registran en `MATRIZ_REQUISITOS.md`.

## Archivos principales

- `Trabajo_Final_Series_Tiempo.ipynb`: notebook narrativo.
- `INFORME_EJECUTIVO.md`: informe listo para revisión y conversión con Pandoc.
- `data/angamos1_nox_horaria_filtrada.csv`: base horaria reducida y trazable.
- `data/angamos1_nox_semanal_modelo.csv`: base semanal efectivamente modelada.
- `resultados/tablas/`: métricas, auditoría y pronóstico.
- `resultados/figuras/`: gráficos en formato PNG.

## Reconstrucción

Desde la raíz del proyecto y con el entorno `series-tiempo-darts`:

```powershell
python ejecutar_auditoria.py
python ejecutar_modelado_final.py
python analisis_sensibilidad.py
```

Luego se abre `prototipo_entrega/Trabajo_Final_Series_Tiempo.ipynb` y se
ejecutan sus celdas en orden. Los scripts `integrar_autoreg.py`,
`actualizar_figura_validacion.py` y `crear_notebook_piloto.py` pertenecen al
prototipo anterior y no forman parte de la ruta activa, porque pueden restaurar
resultados de AutoReg.

## Conversión del informe a Word

Desde `prototipo_entrega/`:

```powershell
pandoc INFORME_EJECUTIVO.md -o INFORME_EJECUTIVO.docx --resource-path=.
```

Los códigos operacionales y de calidad ya fueron contrastados con la Resolución Exenta SMA N.º 404/2017 y quedaron documentados en `CODIGOS_OFICIALES.md`. La exportación a Word se realizará al final, una vez cerrados el contenido, los nombres, la ortografía y las referencias.
