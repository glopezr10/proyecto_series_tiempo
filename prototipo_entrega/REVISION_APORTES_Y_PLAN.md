# Revisión de aportes y plan de cierre

## Qué se rescata de Jessica

- Los 23 CSV trimestrales ya descargados, con cobertura 2020-1 a 2025-3.
- La elección de Angamos 1 y de la concentración de NOx en mg/Nm³.
- La introducción, objetivo general y primera exploración gráfica.
- El uso de media semanal, descomposición, ADF, ACF y PACF.
- Los nombres completos del equipo y los enlaces de la fuente.

No se reutilizan sin revisión sus resultados exploratorios porque el notebook concatena cerca de 3 GB en memoria, no filtra códigos de calidad, no controla la cobertura semanal y todavía no incluye partición, comparación, diagnóstico, prueba ni intervalos.

## Qué se rescata de Guillermo

- Lectura por bloques y tolerancia a distintas codificaciones.
- Normalización de nombres y trazabilidad por archivo y periodo.
- Exportación de tablas de auditoría.
- Revisión explícita de duplicados y códigos `TIPO_DATO_NOX`.

No se reutilizan sus cifras ejecutadas: `dayfirst=True` interpretó incorrectamente las fechas ISO y dejó 19.896 fechas inválidas; además, la conversión numérica no reemplazó la coma decimal y reportó solo cinco valores válidos. Su repositorio contiene únicamente un notebook y un README, sin datos ni estructura de entrega.

## Resultado combinado

La auditoría corregida encontró:

- 50.400 horas entre 2020-01-01 y 2025-09-30;
- cero fechas inválidas y cero duplicados;
- 48.574 mediciones `DM` (96,38%);
- 299 semanas regulares para modelamiento, de las cuales diez fueron interpoladas;
- modelo final AutoReg con rezagos 1-4 y 52;
- RMSE de prueba 27,53 mg/Nm³;
- residuos compatibles con ruido blanco.

## Uso recomendado de GitHub

Conviene trabajar en el repositorio de Guillermo, pero no subir los CSV originales de aproximadamente 3 GB. La integración debería hacerse mediante una rama separada y una solicitud de incorporación revisable.

Archivos que sí conviene versionar:

- notebook final;
- informe Markdown;
- scripts de auditoría y modelamiento;
- base horaria filtrada de aproximadamente 6 MB;
- base semanal de aproximadamente 54 KB;
- tablas, figuras, README y archivo de dependencias.

Archivos que deben excluirse con `.gitignore`:

- `PH*.csv` originales;
- checkpoints de Jupyter;
- cachés de Python;
- documentos temporales y salidas locales no utilizadas.

## Calendario realizable

### Sábado 18

- Congelar base, reglas y partición.
- Construir notebook e informe prototipo.
- Obtener una comparación y un pronóstico completos.

### Domingo 19

- Revisar con el equipo las decisiones de calidad; el diccionario de códigos ya fue contrastado con la Resolución Exenta SMA N.º 404/2017.
- Revisar interpretaciones y sensibilidad de las diez imputaciones.
- Completar referencias, limitaciones y redacción final.
- Integrar aportes útiles del equipo mediante Git.

### Lunes 20

- Ejecutar el notebook desde cero.
- Convertir el informe con Pandoc y revisar visualmente Word.
- Verificar nombres, portada, tablas, figuras y anexos.
- Preparar el paquete final y comprobar que abre en otro equipo.
