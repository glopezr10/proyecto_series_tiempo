Hola equipo. Ya integramos los aportes de Jessica y Guillermo en un prototipo completo: notebook ejecutado, informe Markdown, bases reducidas, auditoría, comparación de modelos, prueba final, pronóstico con intervalos y análisis de sensibilidad.

Creamos la rama `integracion-prototipo` con dos commits listos:

- `9c32413`: prototipo reproducible;
- `02dc27f`: sensibilidad a cobertura, interpolación, media/mediana y estado RE.

El modelo AutoReg con rezagos 1-4 y 52 obtuvo RMSE 27,53 en la prueba y sus residuos pasan Ljung-Box. La sensibilidad indica que el resultado no depende solamente de las diez semanas interpoladas.

Intentamos subir la rama, pero GitHub rechazó el push porque `EngelmannUC` todavía no tiene permiso en `glopezr10/proyecto_series_tiempo`. Guillermo, ¿puedes agregar a `EngelmannUC` como colaborador del repositorio? Apenas esté habilitado hacemos el push. No subiremos los CSV crudos de 3 GB; solo las bases filtradas y los artefactos reproducibles.

Para mañana quedan principalmente: confirmar el significado oficial de los códigos operacionales, revisar interpretaciones/referencias y convertir el informe a Word.
