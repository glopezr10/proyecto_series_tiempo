"""EDA, comparación temporal y pronóstico piloto para la serie semanal de NOx."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller


warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
PROTO = ROOT / "prototipo_entrega"
TABLES = PROTO / "resultados" / "tablas"
FIGURES = PROTO / "resultados" / "figuras"
DATA = PROTO / "data"
FIGURES.mkdir(parents=True, exist_ok=True)

H_VALIDACION = 32
H_PRUEBA = 8
H_PRONOSTICO = 8
PERIODO_ESTACIONAL = 52


def metricas(y: pd.Series, pred: np.ndarray) -> dict[str, float]:
    real = np.asarray(y, dtype=float)
    pronostico = np.asarray(pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(real, pronostico)))
    mae = float(mean_absolute_error(real, pronostico))
    mape = float(np.mean(np.abs((real - pronostico) / real)) * 100)
    smape = float(
        100
        * np.mean(
            2 * np.abs(real - pronostico) / (np.abs(real) + np.abs(pronostico))
        )
    )
    return {"RMSE": rmse, "MAE": mae, "MAPE": mape, "sMAPE": smape}


def pronostico_ingenuo(train: pd.Series, h: int) -> np.ndarray:
    return np.repeat(float(train.iloc[-1]), h)


def pronostico_estacional(train: pd.Series, h: int, periodo: int = 52) -> np.ndarray:
    if len(train) < periodo:
        raise ValueError("No hay una temporada completa para el ingenuo estacional")
    patron = train.iloc[-periodo:].to_numpy()
    return np.array([patron[i % periodo] for i in range(h)], dtype=float)


def pronostico_drift(train: pd.Series, h: int) -> np.ndarray:
    pendiente = (train.iloc[-1] - train.iloc[0]) / (len(train) - 1)
    return train.iloc[-1] + pendiente * np.arange(1, h + 1)


def ajustar_modelos(train: pd.Series, h: int) -> list[dict[str, object]]:
    resultados: list[dict[str, object]] = []

    for nombre, funcion in [
        ("Ingenuo último valor", pronostico_ingenuo),
        ("Ingenuo estacional 52", pronostico_estacional),
        ("Drift", pronostico_drift),
    ]:
        resultados.append(
            {"modelo": nombre, "ajuste": None, "pronostico": funcion(train, h), "AIC": np.nan}
        )

    especificaciones = [
        (
            "SES",
            lambda: SimpleExpSmoothing(train, initialization_method="estimated").fit(
                optimized=True
            ),
        ),
        (
            "Holt amortiguado",
            lambda: Holt(
                train, damped_trend=True, initialization_method="estimated"
            ).fit(optimized=True),
        ),
        (
            "ETS aditivo 52",
            lambda: ExponentialSmoothing(
                train,
                trend="add",
                damped_trend=True,
                seasonal="add",
                seasonal_periods=PERIODO_ESTACIONAL,
                initialization_method="estimated",
            ).fit(optimized=True, use_brute=False),
        ),
        (
            "SARIMA(1,0,1)(1,0,0)[52]",
            lambda: SARIMAX(
                train,
                order=(1, 0, 1),
                seasonal_order=(1, 0, 0, PERIODO_ESTACIONAL),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False, maxiter=200),
        ),
    ]

    for nombre, constructor in especificaciones:
        try:
            ajuste = constructor()
            if hasattr(ajuste, "get_forecast"):
                pred = np.asarray(ajuste.get_forecast(steps=h).predicted_mean)
            else:
                pred = np.asarray(ajuste.forecast(h))
            resultados.append(
                {
                    "modelo": nombre,
                    "ajuste": ajuste,
                    "pronostico": pred,
                    "AIC": float(getattr(ajuste, "aic", np.nan)),
                }
            )
        except Exception as error:
            print(f"Modelo omitido {nombre}: {error}")

    return resultados


def residuos_modelo(nombre: str, ajuste: object, serie: pd.Series) -> pd.Series:
    if ajuste is not None:
        resid = pd.Series(np.asarray(ajuste.resid).squeeze(), index=serie.index[-len(ajuste.resid) :])
        return resid.replace([np.inf, -np.inf], np.nan).dropna()
    if nombre == "Ingenuo estacional 52":
        return (serie - serie.shift(PERIODO_ESTACIONAL)).dropna()
    if nombre == "Drift":
        pendiente = (serie.iloc[-1] - serie.iloc[0]) / (len(serie) - 1)
        return (serie.diff() - pendiente).dropna()
    return serie.diff().dropna()


def reajustar(nombre: str, serie: pd.Series, h: int) -> dict[str, object]:
    candidatos = {r["modelo"]: r for r in ajustar_modelos(serie, h)}
    return candidatos[nombre]


def intervalo_pronostico(
    nombre: str, ajuste: object, punto: np.ndarray, residuos: pd.Series
) -> tuple[np.ndarray, np.ndarray, str]:
    if ajuste is not None and hasattr(ajuste, "get_forecast"):
        conf = ajuste.get_forecast(steps=len(punto)).conf_int(alpha=0.05)
        return (
            np.asarray(conf.iloc[:, 0]),
            np.asarray(conf.iloc[:, 1]),
            "Intervalo predictivo del modelo SARIMA, 95%",
        )

    # Aproximación transparente para modelos sin intervalos nativos en esta versión.
    q025, q975 = np.quantile(residuos, [0.025, 0.975])
    escala = np.sqrt(np.arange(1, len(punto) + 1))
    return (
        punto + q025 * escala,
        punto + q975 * escala,
        "Intervalo empírico de residuos escalado por horizonte, 95%",
    )


def guardar_figura(nombre: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / nombre, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    semanal = pd.read_csv(TABLES / "06_auditoria_semanal.csv", parse_dates=["semana_fin"])
    semanal = semanal.loc[semanal["semana_completa_en_periodo"]].copy()
    semanal = semanal.set_index("semana_fin").asfreq("W-SUN")
    semanal["valor_observado_mg_nm3"] = semanal["nox_media_mg_nm3"].where(
        semanal["semana_utilizable"]
    )
    semanal["valor_imputado"] = semanal["valor_observado_mg_nm3"].isna()
    semanal["nox_modelo_mg_nm3"] = semanal["valor_observado_mg_nm3"].interpolate(
        method="time", limit=2, limit_area="inside"
    )
    if semanal["nox_modelo_mg_nm3"].isna().any():
        faltantes = semanal.index[semanal["nox_modelo_mg_nm3"].isna()].tolist()
        raise ValueError(f"Quedaron semanas sin resolver: {faltantes}")

    semanal.reset_index().to_csv(DATA / "angamos1_nox_semanal_modelo.csv", index=False)
    serie = semanal["nox_modelo_mg_nm3"].astype(float)
    train = serie.iloc[: -(H_VALIDACION + H_PRUEBA)]
    validacion = serie.iloc[-(H_VALIDACION + H_PRUEBA) : -H_PRUEBA]
    prueba = serie.iloc[-H_PRUEBA:]

    modelos_validacion = ajustar_modelos(train, H_VALIDACION)
    filas = []
    pronosticos_validacion: dict[str, np.ndarray] = {}
    for resultado in modelos_validacion:
        nombre = str(resultado["modelo"])
        pred = np.asarray(resultado["pronostico"])
        pronosticos_validacion[nombre] = pred
        fila = {"modelo": nombre, **metricas(validacion, pred), "AIC": resultado["AIC"]}
        resid = residuos_modelo(nombre, resultado["ajuste"], train)
        fila["Ljung_Box_p_10"] = float(
            acorr_ljungbox(resid, lags=[10], return_df=True)["lb_pvalue"].iloc[0]
        )
        filas.append(fila)

    comparacion = pd.DataFrame(filas).sort_values(["RMSE", "MAE"]).reset_index(drop=True)
    comparacion["ranking_RMSE"] = np.arange(1, len(comparacion) + 1)
    comparacion.to_csv(TABLES / "07_comparacion_validacion.csv", index=False)
    mejor = str(comparacion.iloc[0]["modelo"])

    train_valid = serie.iloc[:-H_PRUEBA]
    resultado_prueba = reajustar(mejor, train_valid, H_PRUEBA)
    pred_prueba = np.asarray(resultado_prueba["pronostico"])
    metricas_prueba = metricas(prueba, pred_prueba)
    pd.DataFrame([{"modelo": mejor, **metricas_prueba}]).to_csv(
        TABLES / "08_metricas_prueba_final.csv", index=False
    )

    resultado_final = reajustar(mejor, serie, H_PRONOSTICO)
    pred_final = np.asarray(resultado_final["pronostico"])
    resid_final = residuos_modelo(mejor, resultado_final["ajuste"], serie)
    inferior, superior, metodo_intervalo = intervalo_pronostico(
        mejor, resultado_final["ajuste"], pred_final, resid_final
    )
    fechas_futuras = pd.date_range(
        serie.index[-1] + pd.Timedelta(weeks=1), periods=H_PRONOSTICO, freq="W-SUN"
    )
    pronostico_final = pd.DataFrame(
        {
            "semana_fin": fechas_futuras,
            "pronostico_nox_mg_nm3": pred_final,
            "limite_inferior_95": inferior,
            "limite_superior_95": superior,
            "modelo": mejor,
            "metodo_intervalo": metodo_intervalo,
        }
    )
    pronostico_final.to_csv(TABLES / "09_pronostico_final_8_semanas.csv", index=False)

    adf = adfuller(serie)
    ljung = acorr_ljungbox(resid_final, lags=[10, 20], return_df=True)
    ljung.reset_index(names="lag").to_csv(TABLES / "10_ljung_box_modelo_final.csv", index=False)
    descriptivos = serie.describe().rename("valor").reset_index(names="estadistico")
    descriptivos.to_csv(TABLES / "11_estadisticos_descriptivos.csv", index=False)

    plt.figure(figsize=(12, 5))
    plt.plot(serie, color="#173f5f", linewidth=1.3)
    plt.title("Concentración semanal media de NOx - Angamos 1")
    plt.ylabel("mg/Nm³")
    plt.xlabel("Semana")
    plt.grid(alpha=0.25)
    guardar_figura("01_serie_historica.png")

    descomp = seasonal_decompose(serie, model="additive", period=PERIODO_ESTACIONAL)
    fig = descomp.plot()
    fig.set_size_inches(12, 8)
    fig.suptitle("Descomposición aditiva de la serie semanal", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "02_descomposicion.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    plot_acf(serie, lags=104, ax=axes[0])
    plot_pacf(serie, lags=52, ax=axes[1], method="ywm")
    axes[0].set_title("ACF de la serie semanal")
    axes[1].set_title("PACF de la serie semanal")
    fig.tight_layout()
    fig.savefig(FIGURES / "03_acf_pacf.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    plt.figure(figsize=(12, 5))
    plt.plot(train, label="Entrenamiento", color="#173f5f")
    plt.plot(validacion, label="Validación", color="#f6a800")
    plt.plot(prueba, label="Prueba final", color="#d1495b")
    plt.axvline(validacion.index[0], color="gray", linestyle="--", linewidth=1)
    plt.axvline(prueba.index[0], color="gray", linestyle="--", linewidth=1)
    plt.title("Partición temporal sin mezcla de información futura")
    plt.ylabel("mg/Nm³")
    plt.legend()
    guardar_figura("04_particion_temporal.png")

    plt.figure(figsize=(12, 5))
    plt.plot(validacion, label="Observado", color="black", linewidth=2)
    for nombre in comparacion.head(4)["modelo"]:
        plt.plot(validacion.index, pronosticos_validacion[nombre], label=nombre, alpha=0.85)
    plt.title("Comparación de los cuatro mejores modelos en validación")
    plt.ylabel("mg/Nm³")
    plt.legend(fontsize=8)
    guardar_figura("05_validacion_modelos.png")

    plt.figure(figsize=(10, 4))
    plt.plot(prueba, label="Observado", marker="o", color="black")
    plt.plot(prueba.index, pred_prueba, label=f"Pronóstico: {mejor}", marker="o")
    plt.title("Evaluación única sobre la prueba final de ocho semanas")
    plt.ylabel("mg/Nm³")
    plt.legend()
    guardar_figura("06_prueba_final.png")

    plt.figure(figsize=(12, 5))
    plt.plot(serie.iloc[-104:], label="Histórico", color="#173f5f")
    plt.plot(fechas_futuras, pred_final, label="Pronóstico", color="#d1495b", marker="o")
    plt.fill_between(fechas_futuras, inferior, superior, color="#d1495b", alpha=0.2, label="Intervalo 95%")
    plt.title("Pronóstico final de concentración semanal de NOx")
    plt.ylabel("mg/Nm³")
    plt.legend()
    guardar_figura("07_pronostico_final.png")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    axes[0].plot(resid_final, color="#173f5f")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title(f"Residuos del modelo final: {mejor}")
    plot_acf(resid_final, lags=min(52, len(resid_final) // 3), ax=axes[1])
    axes[1].set_title("ACF de residuos")
    fig.tight_layout()
    fig.savefig(FIGURES / "08_diagnostico_residuos.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    resumen = {
        "n_semanas": int(len(serie)),
        "n_imputadas": int(semanal["valor_imputado"].sum()),
        "inicio": str(serie.index.min().date()),
        "fin": str(serie.index.max().date()),
        "media": float(serie.mean()),
        "desviacion_estandar": float(serie.std()),
        "adf_estadistico": float(adf[0]),
        "adf_p_value": float(adf[1]),
        "modelo_seleccionado": mejor,
        "rmse_validacion": float(comparacion.iloc[0]["RMSE"]),
        "mae_validacion": float(comparacion.iloc[0]["MAE"]),
        "metricas_prueba": metricas_prueba,
        "ljung_box_p_10": float(ljung.loc[10, "lb_pvalue"]),
        "ljung_box_p_20": float(ljung.loc[20, "lb_pvalue"]),
        "metodo_intervalo": metodo_intervalo,
    }
    (TABLES / "resumen_modelado.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print("\nComparación de validación:\n", comparacion.to_string(index=False))


if __name__ == "__main__":
    main()
