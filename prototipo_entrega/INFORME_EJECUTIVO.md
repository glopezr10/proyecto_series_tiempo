---
title: "PronÃ³stico semanal de concentraciÃ³n de NOx en la Central TermoelÃ©ctrica Angamos"
subtitle: "Trabajo final - Series de Tiempo"
author:
  - "Hans Engelmann"
  - "Jessica Anaid Aguilar MejÃ­a"
  - "MatÃ­as NicolÃ¡s GarcÃ­a Garcete"
  - "Guillermo Eder LÃ³pez Rojas"
date: "Julio de 2026"
lang: es-CL
---

# Resumen ejecutivo

Este trabajo modela la concentraciÃ³n semanal media de Ã³xidos de nitrÃ³geno (NOx) de la unidad Angamos 1, empleando registros horarios publicados por el Sistema Nacional de InformaciÃ³n de FiscalizaciÃ³n Ambiental (SNIFA) de la Superintendencia del Medio Ambiente de Chile. La colecciÃ³n local contiene 50.400 observaciones entre el 1 de enero de 2020 y el 30 de septiembre de 2025.

DespuÃ©s de auditar la cobertura, construir una serie semanal y comparar siete alternativas, se seleccionÃ³ un modelo autorregresivo con rezagos 1, 2, 3, 4 y 52. La selecciÃ³n exigiÃ³ primero residuos compatibles con ruido blanco y luego el menor RMSE de validaciÃ³n. En una prueba final de ocho semanas, no utilizada para escoger el modelo, se obtuvo RMSE de 27,53 mg/NmÂ³ y MAE de 24,70 mg/NmÂ³. El diagnÃ³stico final de Ljung-Box no encontrÃ³ autocorrelaciÃ³n residual significativa. El pronÃ³stico de las ocho semanas siguientes se mantiene aproximadamente entre 304 y 314 mg/NmÂ³, con intervalos predictivos del 95% que se amplÃ­an conforme aumenta el horizonte.

# 1. ContextualizaciÃ³n

La Superintendencia del Medio Ambiente publica en SNIFA datos abiertos reportados por centrales termoelÃ©ctricas en el marco del D.S. N.Âº 13/2011. Los archivos contienen promedios horarios de contaminantes atmosfÃ©ricos y variables operacionales. Para este anÃ¡lisis se seleccionÃ³ la central `ANGAMOS`, chimenea `ANGAMOS`, unidad generadora `ANGAMOS 1` y la variable `CONCENTRACION_NOX_MG_NM3`.

Esta variable representa concentraciÃ³n de NOx en mg/NmÂ³, corregida por oxÃ­geno y expresada en base seca. No representa masa total emitida, por lo que los resultados no deben interpretarse en toneladas ni como inventario total de emisiones.

La fuente advierte que los registros son reportados por los regulados y no necesariamente han sido procesados, analizados o verificados por la SMA. Por esa razÃ³n, la auditorÃ­a y las reglas de calidad forman parte central del trabajo.

# 2. Objetivos

## Objetivo general

Modelar y pronosticar la concentraciÃ³n semanal media de NOx de la unidad Angamos 1 mediante tÃ©cnicas de series de tiempo, comparando modelos con criterios explÃ­citos y generando un pronÃ³stico de ocho semanas con intervalos del 95%.

## Objetivos especÃ­ficos

1. Auditar continuidad, duplicados, cÃ³digos de calidad y cobertura de los registros horarios.
2. Construir una serie semanal regular y documentar el tratamiento de semanas incompletas.
3. Describir nivel, variabilidad, estacionalidad y autocorrelaciÃ³n de la serie.
4. Comparar baselines, suavizamiento exponencial y modelos autorregresivos mediante validaciÃ³n temporal.
5. Evaluar si el modelo seleccionado es apropiado mediante diagnÃ³stico de residuos.
6. Medir una sola vez el desempeÃ±o sobre ocho semanas de prueba y generar el pronÃ³stico futuro.

# 3. Datos y preparaciÃ³n

Se procesaron 23 archivos trimestrales en formato CSV, codificados como UTF-16 little-endian, con separador de punto y coma y coma decimal. Los archivos cubren desde el primer trimestre de 2020 hasta el tercer trimestre de 2025.

La lectura se realizÃ³ por bloques para no cargar simultÃ¡neamente cerca de 3 GB. Se normalizaron nombres, se filtrÃ³ Angamos 1 y se convirtiÃ³ la fecha mediante el formato ISO `%Y-%m-%d %H:%M:%S`. La conversiÃ³n numÃ©rica reemplazÃ³ explÃ­citamente la coma decimal.

## 3.1 AuditorÃ­a

| Indicador | Resultado |
|---|---:|
| Archivos procesados | 23 |
| Registros de Angamos 1 | 50.400 |
| Fechas invÃ¡lidas | 0 |
| Registros fecha-hora duplicados | 0 |
| Datos medidos (`DM`) | 48.574 (96,38%) |
| Datos sustituidos (`DS`) | 1.826 (3,62%) |
| Semanas formadas inicialmente | 301 |
| Semanas que superan reglas de cobertura y borde | 289 (96,01%) |

Los estados operacionales observados fueron `RE`, `HE`, `FA`, `DP`, `DNP` y `HA`. La mayor proporciÃ³n correspondiÃ³ a `RE` (93,67%). Debido a que el significado preciso de todos los cÃ³digos debe verificarse en el diccionario oficial, el filtro principal de calidad se basÃ³ en `TIPO_DATO_NOX`: solo se consideraron como observaciones vÃ¡lidas los cÃ³digos que comienzan por `DM`.

## 3.2 AgregaciÃ³n semanal

La concentraciÃ³n es una magnitud intensiva y no debe sumarse. Se calculÃ³ la media de las observaciones horarias vÃ¡lidas en semanas terminadas en domingo. Se exigiÃ³ un mÃ­nimo de 126 horas, equivalente al 75% de una semana de 168 horas.

Las dos semanas parciales de los extremos fueron excluidas. Para conservar un Ã­ndice temporal regular se interpolaron diez semanas interiores con cobertura insuficiente; todos los vacÃ­os fueron aislados o tuvieron una extensiÃ³n mÃ¡xima de dos semanas. La serie final contiene 299 semanas entre el 12 de enero de 2020 y el 28 de septiembre de 2025.

# 4. AnÃ¡lisis exploratorio

![Serie histÃ³rica semanal de concentraciÃ³n de NOx](resultados/figuras/01_serie_historica.png){width=90%}

La concentraciÃ³n semanal presentÃ³ una media de 312,24 mg/NmÂ³ y una desviaciÃ³n estÃ¡ndar de 52,68 mg/NmÂ³. Se observan cambios de nivel y episodios de volatilidad, pero no una tendencia monotÃ³nica permanente.

![DescomposiciÃ³n aditiva de la serie semanal](resultados/figuras/02_descomposicion.png){width=90%}

La descomposiciÃ³n sugiere movimientos de baja frecuencia y un componente anual, aunque la estabilidad de la estacionalidad no se asume Ãºnicamente a partir del grÃ¡fico. La ACF y la PACF muestran dependencia de corto plazo y seÃ±ales alrededor del rezago anual de 52 semanas.

![Funciones de autocorrelaciÃ³n y autocorrelaciÃ³n parcial](resultados/figuras/03_acf_pacf.png){width=90%}

La prueba Dickey-Fuller aumentada produjo un estadÃ­stico de -2,852 y valor p de 0,051. El resultado es limÃ­trofe: al 5% no se rechaza formalmente la hipÃ³tesis de raÃ­z unitaria. En lugar de decidir una diferenciaciÃ³n solo por este valor, se compararon modelos con distinta capacidad para representar persistencia y se utilizÃ³ el diagnÃ³stico residual como criterio de adecuaciÃ³n.

# 5. Estrategia de validaciÃ³n

La serie se dividiÃ³ cronolÃ³gicamente en entrenamiento, validaciÃ³n de 32 semanas y prueba final de 8 semanas. La prueba se mantuvo completamente fuera de la selecciÃ³n.

![ParticiÃ³n temporal](resultados/figuras/04_particion_temporal.png){width=90%}

Se compararon siete alternativas:

- ingenuo de Ãºltimo valor;
- ingenuo estacional de 52 semanas;
- drift;
- suavizamiento exponencial simple;
- Holt amortiguado;
- ETS aditivo con periodo 52;
- AutoReg con rezagos 1, 2, 3, 4 y 52.

La regla se fijÃ³ antes de observar la prueba final: un modelo debÃ­a superar Ljung-Box al 5% y, entre los candidatos apropiados, se escogerÃ­a el menor RMSE de validaciÃ³n. MAE, MAPE y sMAPE se utilizaron como medidas complementarias. El AIC se informÃ³ Ãºnicamente como referencia dentro de modelos probabilÃ­sticos y no para ordenar familias diferentes.

# 6. ComparaciÃ³n de modelos

| Modelo | RMSE | MAE | MAPE (%) | sMAPE (%) | Ljung-Box p(10) |
|---|---:|---:|---:|---:|---:|
| Ingenuo Ãºltimo valor | 38,93 | 33,40 | 11,51 | 11,71 | <0,001 |
| Drift | 39,91 | 34,09 | 11,65 | 11,96 | <0,001 |
| **AutoReg rezagos 1-4 y 52** | **40,02** | **31,98** | **11,76** | **11,14** | **0,773** |
| Holt amortiguado | 41,93 | 36,13 | 12,20 | 12,71 | 0,076 |
| SES | 41,93 | 36,15 | 12,20 | 12,71 | 0,077 |
| ETS aditivo 52 | 49,07 | 38,57 | 13,22 | 13,67 | <0,001 |
| Ingenuo estacional 52 | 60,39 | 50,50 | 17,49 | 16,98 | <0,001 |

El ingenuo obtuvo el menor RMSE, pero dejÃ³ dependencia temporal clara en los errores. No satisface el requisito de modelo apropiado. AutoReg quedÃ³ tercero por RMSE, obtuvo el menor MAE entre los candidatos competitivos y superÃ³ ampliamente Ljung-Box. Por ello fue seleccionado.

![ComparaciÃ³n en validaciÃ³n](resultados/figuras/05_validacion_modelos.png){width=90%}

# 7. Prueba final y adecuaciÃ³n

Una vez seleccionado AutoReg, se reentrenÃ³ con entrenamiento mÃ¡s validaciÃ³n y se evaluÃ³ sobre las ocho semanas reservadas.

| MÃ©trica | Resultado |
|---|---:|
| RMSE | 27,53 mg/NmÂ³ |
| MAE | 24,70 mg/NmÂ³ |
| MAPE | 8,52% |
| sMAPE | 8,55% |

![EvaluaciÃ³n sobre la prueba final](resultados/figuras/06_prueba_final.png){width=85%}

Posteriormente el modelo se reentrenÃ³ con las 299 semanas. Ljung-Box produjo valores p de 0,713 y 0,801 para los rezagos 10 y 20. No se rechaza la ausencia de autocorrelaciÃ³n residual. Bajo este criterio, el modelo final se considera apropiado.

![DiagnÃ³stico de residuos](resultados/figuras/08_diagnostico_residuos.png){width=90%}

# 8. PronÃ³stico

| Semana terminada en | PronÃ³stico | LÃ­mite inferior 95% | LÃ­mite superior 95% |
|---|---:|---:|---:|
| 2025-10-05 | 304,14 | 248,43 | 359,85 |
| 2025-10-12 | 309,75 | 244,61 | 374,90 |
| 2025-10-19 | 313,87 | 246,22 | 381,52 |
| 2025-10-26 | 312,18 | 240,50 | 383,85 |
| 2025-11-02 | 310,75 | 234,09 | 387,40 |
| 2025-11-09 | 311,27 | 231,20 | 391,34 |
| 2025-11-16 | 311,63 | 228,96 | 394,31 |
| 2025-11-23 | 311,34 | 226,17 | 396,52 |

![PronÃ³stico final de ocho semanas](resultados/figuras/07_pronostico_final.png){width=90%}

El nivel central pronosticado permanece relativamente estable. La amplitud creciente de los intervalos refleja que la incertidumbre se acumula con el horizonte.

<!-- SENSIBILIDAD_INICIO -->
# 8.1 AnÃ¡lisis de sensibilidad

Se evaluÃ³ el mismo modelo AutoReg bajo cinco construcciones de la serie para determinar si la conclusiÃ³n dependÃ­a del umbral de cobertura, las diez interpolaciones, el estadÃ­stico semanal o el estado operacional.

| Escenario | Semanas imputadas | RMSE validaciÃ³n | RMSE prueba | Ljung-Box p(10) | PronÃ³stico medio 8 semanas |
|---|---:|---:|---:|---:|---:|
| Media, cobertura 75% | 10 | 40,02 | 27,53 | 0,713 | 310,62 |
| Media, cobertura 50% | 1 | 39,32 | 29,24 | 0,715 | 313,98 |
| Media, sin umbral | 0 | 39,28 | 29,27 | 0,713 | 313,94 |
| Mediana, cobertura 75% | 10 | 48,52 | 36,54 | 0,992 | 295,80 |
| Media DM+RE, cobertura 75% | 25 | 37,84 | 31,62 | 0,054 | 296,64 |

![Sensibilidad del RMSE de prueba](resultados/figuras/09_sensibilidad_construccion_serie.png){width=90%}

La familia AutoReg mantuvo residuos compatibles con ruido blanco en todos los escenarios. Reducir el umbral al 50% o utilizar todas las medias semanales produjo resultados muy cercanos, por lo que las diez interpolaciones de la especificaciÃ³n principal no determinan por sÃ­ solas la conclusiÃ³n. La mediana y la restricciÃ³n al estado `RE` redujeron el nivel pronosticado y empeoraron el RMSE de prueba.

![Sensibilidad del pronÃ³stico](resultados/figuras/10_sensibilidad_pronostico.png){width=90%}

Se conserva como especificaciÃ³n principal la media de datos medidos con cobertura mÃ­nima del 75% porque mantiene el significado de concentraciÃ³n semanal general, presenta el menor RMSE de prueba y evita condicionar la definiciÃ³n a cÃ³digos operacionales cuyo significado completo aÃºn debe verificarse. La diferencia de nivel observada bajo `DM+RE` se reporta como limitaciÃ³n sustantiva.
<!-- SENSIBILIDAD_FIN -->

# 9. Conclusiones

La base disponible permitiÃ³ construir una serie semanal de alta cobertura. Los modelos simples entregaron pronÃ³sticos competitivos, pero varios conservaron autocorrelaciÃ³n en los residuos. El modelo AutoReg con rezagos cortos y anual ofreciÃ³ el mejor compromiso entre error fuera de muestra, parsimonia y adecuaciÃ³n residual.

En la prueba final, el error porcentual absoluto medio fue cercano al 8,5%. El modelo final se considera apropiado respecto de la blancura residual y permite proyectar la concentraciÃ³n media semanal con intervalos explÃ­citos.

Los resultados no deben interpretarse como masa total emitida ni como evaluaciÃ³n normativa. Tampoco permiten establecer causalidad con potencia, combustible u otras variables operacionales. Las principales limitaciones son el carÃ¡cter reportado y no necesariamente verificado de los datos, la interpolaciÃ³n de diez semanas y la necesidad de confirmar el significado completo de los cÃ³digos operacionales.

# Referencias y fuentes

- Superintendencia del Medio Ambiente. Sistema Nacional de InformaciÃ³n de FiscalizaciÃ³n Ambiental, secciÃ³n Datos Abiertos: <https://snifa.sma.gob.cl/DatosAbiertos>.
- Superintendencia del Medio Ambiente. ColecciÃ³n pÃºblica de datos de centrales termoelÃ©ctricas bajo D.S. N.Âº 13/2011.
- Archivos trimestrales `PH2020-1` a `PH2025-3`, descargados y procesados en julio de 2026.
