# Códigos oficiales utilizados

Las definiciones se contrastaron con la *Guía del Sistema de Información para Centrales Termoeléctricas, versión 3*, aprobada por la Resolución Exenta SMA N.º 404/2017.

## Estado de la unidad generadora (`ESTADO_UGE`)

| Código | Significado |
|---|---|
| `RE` | Operación en régimen |
| `HE` | Horas de encendido |
| `HA` | Horas de apagado |
| `FA` | Falla |
| `DP` | Detención programada |
| `DNP` | Detención no programada |

La guía señala además que, si una unidad presenta varios estados dentro de una misma hora, el promedio horario se caracteriza según la peor condición desde el punto de vista de las emisiones. Define `FA` como un desperfecto intempestivo en un equipo de control de emisiones o de proceso que provoca un aumento de las emisiones.

## Tipo y condición del dato

| Código | Campo | Significado |
|---|---|---|
| `DM` | Tipo de dato | Dato medido |
| `DS` | Tipo de dato | Dato sustituido |
| `DMC` | Tipo de dato | Dato medido mediante CEMS en estado condicional |
| `MMC` | Estado CEMS | CEMS midiendo condicionalmente |
| `FC` | Estado CEMS | Fuera de control |

En los datos analizados se observaron `DM` y `DS` para NOx. El modelo principal conserva `DM` en todos los estados operacionales porque estima la concentración semanal general reportada y medida. El escenario `DM+RE` se presenta como sensibilidad y responde a una pregunta distinta: concentración durante operación en régimen.

## Fuentes

- [Resolución Exenta SMA N.º 404/2017](https://transparencia.sma.gob.cl/doc/resoluciones/RESOL_EXENTA_SMA_2017/RESOL%20EXENTA%20N%20404%20SMA.PDF)
- [Descripción oficial de los datos](https://drive.google.com/file/d/1A4ofyFi_Jq8aScbx0os99whqdTbL3WR3/view)
- [Instrucciones generales de la SMA en SNIFA](https://snifa.sma.gob.cl/v2/Resolucion/Instruccion)
