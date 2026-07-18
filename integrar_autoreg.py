"""Integra un AR con rezago estacional 52 y actualiza la selección final."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.stattools import adfuller

import ejecutar_modelado_estable as estable
import prototipo_modelado as piloto


ROOT = Path(__file__).resolve().parent
PROTO = ROOT / "prototipo_entrega"
TABLES = PROTO / "resultados" / "tablas"
FIGURES = PROTO / "resultados" / "figuras"
DATA = PROTO / "data"
NOMBRE = "AutoReg rezagos 1-4 y 52"
REZAGOS = [1, 2, 3, 4, 52]


def ajustar_ar(serie):
    return AutoReg(serie, lags=REZAGOS, trend="ct", old_names=False).fit()


def predecir(modelo, h):
    return np.asarray(
        modelo.predict(start=modelo.nobs + modelo.hold_back, end=modelo.nobs + modelo.hold_back + h - 1)
    )


def resultado_ets(serie, h, nombre):
    return next(x for x in estable.ajustar_modelos_estables(serie, h) if x["modelo"] == nombre)


def main():
    semanal = pd.read_csv(DATA / "angamos1_nox_semanal_modelo.csv", parse_dates=["semana_fin"])
    serie = semanal.set_index("semana_fin")["nox_modelo_mg_nm3"].astype(float)
    train = serie.iloc[: -(piloto.H_VALIDACION + piloto.H_PRUEBA)]
    validacion = serie.iloc[-(piloto.H_VALIDACION + piloto.H_PRUEBA) : -piloto.H_PRUEBA]
    prueba = serie.iloc[-piloto.H_PRUEBA :]

    ar_train = ajustar_ar(train)
    pred_valid = np.asarray(ar_train.predict(start=len(train), end=len(train) + len(validacion) - 1))
    fila_ar = {
        "modelo": NOMBRE,
        **piloto.metricas(validacion, pred_valid),
        "AIC": float(ar_train.aic),
        "Ljung_Box_p_10": float(
            acorr_ljungbox(ar_train.resid, lags=[10], return_df=True)["lb_pvalue"].iloc[0]
        ),
    }

    comparacion = pd.read_csv(TABLES / "07_comparacion_validacion.csv")
    comparacion = comparacion.loc[comparacion["modelo"] != NOMBRE].drop(columns=["ranking_RMSE"], errors="ignore")
    comparacion = pd.concat([comparacion, pd.DataFrame([fila_ar])], ignore_index=True)
    comparacion = comparacion.sort_values(["RMSE", "MAE"]).reset_index(drop=True)
    comparacion["ranking_RMSE"] = np.arange(1, len(comparacion) + 1)
    comparacion.to_csv(TABLES / "07_comparacion_validacion.csv", index=False)

    apropiados = comparacion.loc[comparacion["Ljung_Box_p_10"] > 0.05].sort_values(["RMSE", "MAE"])
    mejor = str(apropiados.iloc[0]["modelo"])

    train_valid = serie.iloc[:-piloto.H_PRUEBA]
    if mejor == NOMBRE:
        ajuste_prueba = ajustar_ar(train_valid)
        pred_prueba = np.asarray(
            ajuste_prueba.predict(start=len(train_valid), end=len(train_valid) + piloto.H_PRUEBA - 1)
        )
        ajuste_final = ajustar_ar(serie)
        prediccion = ajuste_final.get_prediction(
            start=len(serie), end=len(serie) + piloto.H_PRONOSTICO - 1, dynamic=False
        )
        pred_final = np.asarray(prediccion.predicted_mean)
        conf = np.asarray(prediccion.conf_int(alpha=0.05))
        inferior, superior = conf[:, 0], conf[:, 1]
        residuos = pd.Series(np.asarray(ajuste_final.resid), index=serie.index[-len(ajuste_final.resid) :])
        metodo = "Intervalo predictivo normal del modelo AutoReg, 95%"
    else:
        prueba_ets = resultado_ets(train_valid, piloto.H_PRUEBA, mejor)
        pred_prueba = np.asarray(prueba_ets["pronostico"])
        final_ets = resultado_ets(serie, piloto.H_PRONOSTICO, mejor)
        pred_final = np.asarray(final_ets["pronostico"])
        residuos = piloto.residuos_modelo(mejor, final_ets["ajuste"], serie)
        inferior, superior, metodo = piloto.intervalo_pronostico(
            mejor, final_ets["ajuste"], pred_final, residuos
        )

    metricas_prueba = piloto.metricas(prueba, pred_prueba)
    pd.DataFrame([{"modelo": mejor, **metricas_prueba}]).to_csv(
        TABLES / "08_metricas_prueba_final.csv", index=False
    )

    fechas = pd.date_range(
        serie.index[-1] + pd.Timedelta(weeks=1), periods=piloto.H_PRONOSTICO, freq="W-SUN"
    )
    pronostico = pd.DataFrame(
        {
            "semana_fin": fechas,
            "pronostico_nox_mg_nm3": pred_final,
            "limite_inferior_95": inferior,
            "limite_superior_95": superior,
            "modelo": mejor,
            "metodo_intervalo": metodo,
        }
    )
    pronostico.to_csv(TABLES / "09_pronostico_final_8_semanas.csv", index=False)

    ljung = acorr_ljungbox(residuos, lags=[10, 20], return_df=True)
    ljung.index.name = "lag"
    ljung.reset_index().to_csv(TABLES / "10_ljung_box_modelo_final.csv", index=False)

    plt.figure(figsize=(10, 4))
    plt.plot(prueba, label="Observado", marker="o", color="black")
    plt.plot(prueba.index, pred_prueba, label=f"Pronóstico: {mejor}", marker="o")
    plt.title("Evaluación única sobre la prueba final de ocho semanas")
    plt.ylabel("mg/Nm³")
    plt.legend()
    piloto.guardar_figura("06_prueba_final.png")

    plt.figure(figsize=(12, 5))
    plt.plot(serie.iloc[-104:], label="Histórico", color="#173f5f")
    plt.plot(fechas, pred_final, label="Pronóstico", color="#d1495b", marker="o")
    plt.fill_between(fechas, inferior, superior, color="#d1495b", alpha=0.2, label="Intervalo 95%")
    plt.title("Pronóstico final de concentración semanal de NOx")
    plt.ylabel("mg/Nm³")
    plt.legend()
    piloto.guardar_figura("07_pronostico_final.png")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    axes[0].plot(residuos, color="#173f5f")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title(f"Residuos del modelo final: {mejor}")
    plot_acf(residuos, lags=min(52, len(residuos) // 3), ax=axes[1])
    axes[1].set_title("ACF de residuos")
    fig.tight_layout()
    fig.savefig(FIGURES / "08_diagnostico_residuos.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    adf = adfuller(serie)
    resumen = {
        "n_semanas": int(len(serie)),
        "n_imputadas": int(semanal["valor_imputado"].sum()),
        "inicio": str(serie.index.min().date()),
        "fin": str(serie.index.max().date()),
        "media": float(serie.mean()),
        "desviacion_estandar": float(serie.std()),
        "adf_estadistico": float(adf[0]),
        "adf_p_value": float(adf[1]),
        "regla_seleccion": "Ljung-Box p>0.05 y luego menor RMSE de validación",
        "modelo_seleccionado": mejor,
        "rmse_validacion": float(apropiados.iloc[0]["RMSE"]),
        "mae_validacion": float(apropiados.iloc[0]["MAE"]),
        "metricas_prueba": metricas_prueba,
        "ljung_box_p_10": float(ljung.loc[10, "lb_pvalue"]),
        "ljung_box_p_20": float(ljung.loc[20, "lb_pvalue"]),
        "metodo_intervalo": metodo,
    }
    (TABLES / "resumen_modelado.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nComparación:\n", comparacion.to_string(index=False))
    print("\nResumen:\n", json.dumps(resumen, ensure_ascii=False, indent=2))
    print("\nPronóstico:\n", pronostico.to_string(index=False))


if __name__ == "__main__":
    main()
