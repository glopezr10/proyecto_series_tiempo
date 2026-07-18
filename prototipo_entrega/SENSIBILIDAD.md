# Análisis de sensibilidad

Se evaluó el modelo AutoReg con rezagos 1, 2, 3, 4 y 52 bajo cinco construcciones de la serie:

1. media con cobertura mínima 75%;
2. media con cobertura mínima 50%;
3. media sin umbral;
4. mediana con cobertura mínima 75%;
5. media de datos medidos en estado `RE` con cobertura mínima 75%.

El modelo conservó residuos compatibles con ruido blanco en todos los escenarios. La especificación principal obtuvo el menor RMSE de prueba, 27,53 mg/Nm³. Los escenarios de 50% y sin umbral obtuvieron 29,24 y 29,27 mg/Nm³, respectivamente, lo que indica que las diez interpolaciones no determinan por sí solas el resultado.

La mediana y la restricción `DM+RE` redujeron el pronóstico medio hacia 296 mg/Nm³ y presentaron errores de prueba mayores. Según la Resolución Exenta SMA N.º 404/2017, `RE` corresponde a operación en régimen. Por tanto, `DM+RE` no es solo otro filtro de calidad: cambia el estimando a concentración medida durante operación en régimen. La diferencia se reporta como una limitación sustantiva del pronóstico general.

## Reproducción

Desde la raíz del proyecto:

```powershell
python analisis_sensibilidad.py
python actualizar_entregables_sensibilidad.py
jupyter nbconvert --execute --to notebook --inplace prototipo_entrega/Trabajo_Final_Series_Tiempo.ipynb
```

Resultados:

- `resultados/tablas/12_analisis_sensibilidad.csv`;
- `resultados/figuras/09_sensibilidad_construccion_serie.png`;
- `resultados/figuras/10_sensibilidad_pronostico.png`.
