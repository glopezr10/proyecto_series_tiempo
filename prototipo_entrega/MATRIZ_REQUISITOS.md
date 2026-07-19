# Matriz de requisitos de la entrega

Esta matriz conecta la pauta oficial con los archivos que demuestran su cumplimiento. Se actualizará durante el desarrollo y será la lista de control antes de exportar el informe a Word.

| Requisito de la pauta | Evidencia principal | Estado | Revisión pendiente |
|---|---|---|---|
| Portada con integrantes | Portada de `TareaFinal_Engelmann_Aguilar_Garcia_Lopez.docx` | Cumple | Incluye los cuatro integrantes y la institución |
| Contextualización, periodo y fuente | Sección 1 del informe y sección 1 del notebook | Cumple | Revisar precisión ambiental y referencias |
| Objetivo y horizonte de predicción | Sección 2 del informe y secciones 1-2 del notebook | Cumple | Objetivo y horizonte de ocho semanas explícitos |
| Análisis exploratorio con indicadores, tablas y gráficas | Sección 4 del informe; auditoría, serie, descomposición, ACF, PACF y ADF en el notebook | Cumple | Revisar que cada gráfico tenga interpretación |
| Aplicación de técnicas de series de tiempo | Secciones 5-7 del informe y 5-7 del notebook | Cumple | Revisar supuestos y reproducibilidad |
| Comparación y selección explícita de modelos | Tabla de validación y regla RMSE más Ljung-Box | Cumple | ARIMA(3,0,0) seleccionado con regla previa y prueba reservada |
| Indicar si el modelo final es apropiado | Diagnóstico residual y Ljung-Box en sección 7 | Cumple | Explicar alcance y límites de la conclusión |
| Predicciones con intervalo | Sección 8, tabla y figura de pronóstico al 95% | Cumple | Se explica la diferencia entre intervalo predictivo e intervalo para la media |
| Conclusiones relacionadas con objetivos y resultados | Sección 9 del informe y notebook | Cumple | Revisar interpretación y evitar afirmaciones causales o normativas |
| Código Python en Notebook con buenas prácticas y Markdown | `Trabajo_Final_Series_Tiempo.ipynb` | Cumple | Trece celdas de código ejecutadas en orden, sin errores |
| Base de datos importada a Python e indicación de acceso | `data/angamos1_nox_horaria_filtrada.csv` y documentación de fuente abierta | Cumple | Extracto abierto, trazable a 23 archivos SNIFA y utilizado directamente por el notebook |
| Desarrollo completamente en Python | Notebook ejecutable de principio a fin | Cumple | Auditoría, gráficos, modelos, diagnóstico y sensibilidad reproducidos sin intervención manual |
| Informe, código y base como archivos separados | Word final, notebook y CSV horario en `data/` | Cumple | Los tres archivos exactos están documentados en `README.md` |

## Decisiones metodológicas confirmadas

### Decisión 1: variable objetivo

La serie principal será la concentración semanal media reportada y medida de NOx de Angamos 1:

- se conservarán los registros horarios clasificados como dato medido (`DM`);
- se excluirán de la serie principal los datos sustituidos (`DS`);
- se incluirán todos los estados operacionales;
- la restricción `DM+RE` se mantendrá como análisis de sensibilidad y no como definición principal;
- el resultado se interpretará como concentración semanal general medida, no como concentración exclusiva durante operación en régimen ni como evaluación normativa.

## Prioridades de desarrollo

1. Revisión humana opcional del Word en Microsoft Word antes de cargarlo.
2. Confirmar en la plataforma los tres archivos indicados en `README.md`.

## Criterio de cierre

Un requisito solo se considerará cerrado cuando la evidencia pueda reproducirse desde los archivos versionados y su interpretación haya sido revisada por el equipo.
