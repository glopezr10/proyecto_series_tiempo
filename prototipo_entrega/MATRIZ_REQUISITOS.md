# Matriz de requisitos de la entrega

Esta matriz conecta la pauta oficial con los archivos que demuestran su cumplimiento. Se actualizará durante el desarrollo y será la lista de control antes de exportar el informe a Word.

| Requisito de la pauta | Evidencia principal | Estado | Revisión pendiente |
|---|---|---|---|
| Portada con integrantes | Metadatos iniciales de `INFORME_EJECUTIVO.md` | Cumple | Confirmar nombres y orden del equipo |
| Contextualización, periodo y fuente | Sección 1 del informe y sección 1 del notebook | Cumple | Revisar precisión ambiental y referencias |
| Objetivo y horizonte de predicción | Sección 2 del informe y secciones 1-2 del notebook | Cumple con revisión | Objetivo estadístico confirmado; ratificar horizonte de ocho semanas |
| Análisis exploratorio con indicadores, tablas y gráficas | Sección 4 del informe; auditoría, serie, descomposición, ACF, PACF y ADF en el notebook | Cumple | Revisar que cada gráfico tenga interpretación |
| Aplicación de técnicas de series de tiempo | Secciones 5-7 del informe y 5-7 del notebook | Cumple | Revisar supuestos y reproducibilidad |
| Comparación y selección explícita de modelos | Tabla de validación y regla RMSE más Ljung-Box | Cumple con revisión | Confirmar que la regla represente el criterio acordado por el equipo |
| Indicar si el modelo final es apropiado | Diagnóstico residual y Ljung-Box en sección 7 | Cumple | Explicar alcance y límites de la conclusión |
| Predicciones con intervalo | Sección 8, tabla y figura de pronóstico al 95% | Cumple | Mantener el término intervalo predictivo y explicar su diferencia con un intervalo de confianza |
| Conclusiones relacionadas con objetivos y resultados | Sección 9 del informe y notebook | Cumple | Revisar interpretación y evitar afirmaciones causales o normativas |
| Código Python en Notebook con buenas prácticas y Markdown | `Trabajo_Final_Series_Tiempo.ipynb` | Cumple con revisión | Ejecutar desde un ambiente limpio y simplificar celdas si corresponde |
| Base de datos importada a Python e indicación de acceso | `data/angamos1_nox_horaria_filtrada.csv` y documentación de fuente abierta | Cumple con revisión | Confirmar que el equipo acepta entregar el extracto trazable utilizado por el notebook |
| Desarrollo completamente en Python | Notebook y scripts de reproducción | Cumple | Verificar ejecución completa sin intervención manual |
| Informe, código y base como archivos separados | Informe Markdown, notebook y CSV en `data/` | Cumple | Exportar el Word solamente al cerrar el contenido |

## Decisiones metodológicas confirmadas

### Decisión 1: variable objetivo

La serie principal será la concentración semanal media reportada y medida de NOx de Angamos 1:

- se conservarán los registros horarios clasificados como dato medido (`DM`);
- se excluirán de la serie principal los datos sustituidos (`DS`);
- se incluirán todos los estados operacionales;
- la restricción `DM+RE` se mantendrá como análisis de sensibilidad y no como definición principal;
- el resultado se interpretará como concentración semanal general medida, no como concentración exclusiva durante operación en régimen ni como evaluación normativa.

## Prioridades de desarrollo

1. Confirmar las reglas de calidad, cobertura semanal e interpolación.
2. Revisar la estrategia temporal de comparación y la selección del modelo.
3. Ejecutar el notebook completo en un ambiente nuevo usando `requirements.txt`.
4. Revisar que todas las cifras del informe coincidan con las salidas del notebook.
5. Cerrar interpretaciones, referencias, nombres y redacción.
6. Exportar y revisar visualmente el documento Word como último paso.

## Criterio de cierre

Un requisito solo se considerará cerrado cuando la evidencia pueda reproducirse desde los archivos versionados y su interpretación haya sido revisada por el equipo.
