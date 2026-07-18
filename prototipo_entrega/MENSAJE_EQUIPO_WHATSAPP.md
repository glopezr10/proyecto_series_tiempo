Hola equipo. Ya integramos los aportes de Jessica y Guillermo en un prototipo completo: notebook ejecutado, informe Markdown, bases reducidas, auditoría, comparación de modelos, prueba final, pronóstico con intervalos y análisis de sensibilidad.

Publicamos la rama `integracion-prototipo` en el repositorio de Guillermo:

- `9c32413`: prototipo reproducible;
- `02dc27f`: sensibilidad a cobertura, interpolación, media/mediana y estado RE;
- `ddecfee`: códigos oficiales y alcance del pronóstico;
- `2ec4ad9`: versión Word preliminar.

Rama: <https://github.com/glopezr10/proyecto_series_tiempo/tree/integracion-prototipo>

Pull request: <https://github.com/glopezr10/proyecto_series_tiempo/pull/new/integracion-prototipo>

El modelo AutoReg con rezagos 1-4 y 52 obtuvo RMSE 27,53 en la prueba y sus residuos pasan Ljung-Box. La sensibilidad indica que el resultado no depende solamente de las diez semanas interpoladas.

Gracias, Guillermo, por habilitar el acceso. No subimos los CSV crudos de 3 GB; la rama contiene solamente las bases filtradas y los artefactos reproducibles.

También confirmé los códigos operacionales y de calidad con la Resolución Exenta SMA N.º 404/2017 y dejé documentada la sensibilidad del resultado al usar solamente operación en régimen (`DM+RE`). Ya existe una versión Word preliminar con portada, estilos, tablas y figuras. Para mañana quedan principalmente la revisión conjunta de interpretaciones y nombres, y abrir el Word para el control visual final.
