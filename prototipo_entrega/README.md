# Trabajo final de Series de Tiempo

Esta carpeta contiene la base de desarrollo de la entrega final. El notebook, el informe Markdown y las bases reducidas son los artefactos canónicos; las tablas, figuras y documentos auxiliares sirven como evidencia y apoyo para su revisión.

El estado de cumplimiento y las decisiones pendientes se registran en `MATRIZ_REQUISITOS.md`.

## Archivos principales

- `Trabajo_Final_Series_Tiempo.ipynb`: notebook ejecutable de principio a fin.
- `INFORME_EJECUTIVO.md`: informe listo para revisión y conversión con Pandoc.
- `data/angamos1_nox_horaria_filtrada.csv`: base horaria reducida y trazable.
- `data/angamos1_nox_semanal_modelo.csv`: base semanal efectivamente modelada.
- `resultados/tablas/`: métricas, auditoría y pronóstico.
- `resultados/figuras/`: gráficos en formato PNG.

## Ejecución principal

La base es abierta y proviene de SNIFA. Desde la raíz del repositorio se instala
el ambiente y se abre el notebook:

```powershell
python -m pip install -r requirements.txt
python -m jupyter lab prototipo_entrega/Trabajo_Final_Series_Tiempo.ipynb
```

Se selecciona **Run All**. El notebook importa la base horaria entregada y
reproduce auditoría, agregación semanal, análisis exploratorio, comparación de
modelos, prueba final, diagnóstico, pronóstico y sensibilidad. No requiere
ejecutar previamente los scripts de la raíz.

Los scripts `integrar_autoreg.py`, `actualizar_figura_validacion.py` y
`crear_notebook_piloto.py` pertenecen al prototipo anterior y no forman parte
de la ruta activa.

## Conversión del informe a Word

Desde `prototipo_entrega/`:

```powershell
New-Item -ItemType Directory -Force -Path ../tmp_word
pandoc INFORME_EJECUTIVO.md -o ../tmp_word/base.docx --resource-path=.
python ../preparar_word_final.py ../tmp_word/base.docx TareaFinal_Engelmann_Aguilar_Garcia_Lopez.docx
```

Los códigos operacionales y de calidad ya fueron contrastados con la Resolución Exenta SMA N.º 404/2017 y quedaron documentados en `CODIGOS_OFICIALES.md`.

## Archivos que se entregan

1. `TareaFinal_Engelmann_Aguilar_Garcia_Lopez.docx`: informe ejecutivo.
2. `Trabajo_Final_Series_Tiempo.ipynb`: código Python ejecutado y explicado.
3. `data/angamos1_nox_horaria_filtrada.csv`: base abierta importada directamente por el notebook.

La base semanal, las tablas y las figuras se mantienen como evidencia
reproducible, pero no reemplazan los tres archivos solicitados por la pauta.
