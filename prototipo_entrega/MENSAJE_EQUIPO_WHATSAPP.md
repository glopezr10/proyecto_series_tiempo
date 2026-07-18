Hola equipo. Ya integramos los aportes de Jessica y Guillermo en un prototipo completo: notebook ejecutado, informe Markdown, bases reducidas, auditoría, comparación de modelos, prueba final, pronóstico con intervalos y análisis de sensibilidad.

Creamos la rama `integracion-prototipo` con dos commits listos:

- `9c32413`: prototipo reproducible;
- `02dc27f`: sensibilidad a cobertura, interpolación, media/mediana y estado RE.

El modelo AutoReg con rezagos 1-4 y 52 obtuvo RMSE 27,53 en la prueba y sus residuos pasan Ljung-Box. La sensibilidad indica que el resultado no depende solamente de las diez semanas interpoladas.

Intentamos subir la rama, pero GitHub rechazó el push porque `EngelmannUC` todavía no tiene permiso en `glopezr10/proyecto_series_tiempo`. Guillermo, ¿puedes agregar a `EngelmannUC` como colaborador del repositorio? Apenas esté habilitado hacemos el push. No subiremos los CSV crudos de 3 GB; solo las bases filtradas y los artefactos reproducibles.

También confirmé los códigos operacionales y de calidad con la Resolución Exenta SMA N.º 404/2017 y dejé documentada la sensibilidad del resultado al usar solamente operación en régimen (`DM+RE`). Para mañana quedan principalmente la revisión conjunta de interpretaciones/nombres y la conversión del informe a Word.
