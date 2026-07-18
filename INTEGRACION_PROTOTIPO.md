# Integración del prototipo

Esta rama integra una propuesta completa de entrega basada en los datos descargados por Jessica y en la estructura de auditoría iniciada por Guillermo.

## Contenido principal

- notebook narrativo ejecutado y sin errores;
- informe ejecutivo en Markdown;
- base horaria filtrada y base semanal modelada;
- tablas, figuras y pronóstico de ocho semanas;
- scripts reproducibles de auditoría y modelamiento;
- revisión documentada de los aportes previos.

## Resultado piloto

El modelo seleccionado es AutoReg con rezagos 1, 2, 3, 4 y 52. En la prueba final obtuvo RMSE 27,53 mg/Nm³ y MAE 24,70 mg/Nm³. Los residuos del ajuste completo superaron Ljung-Box en los rezagos 10 y 20.

## Aspectos todavía abiertos

- confirmar en la documentación oficial los códigos operacionales;
- ejecutar sensibilidad de las diez semanas interpoladas;
- revisar redacción y referencias;
- convertir el informe a Word y efectuar control visual final.
