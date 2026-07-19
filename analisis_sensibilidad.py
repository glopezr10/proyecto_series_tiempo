"""Sensibilidad del ARIMA(3,0,0) a la construccion de la serie semanal."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX


ROOT = Path(__file__).resolve().parent
ENTREGA = ROOT / "entrega"
TABLES = ENTREGA / "resultados" / "tablas"
FIGURES = ENTREGA / "resultados" / "figuras"
DATA = ENTREGA / "data"
H_VALIDACION = 32
H_PRUEBA = 8


def metricas(real, pred):
    real = np.asarray(real, dtype=float)
    pred = np.asarray(pred, dtype=float)
    return {
        "RMSE": float(np.sqrt(np.mean((real - pred) ** 2))),
        "MAE": float(np.mean(np.abs(real - pred))),
        "sMAPE": float(
            100 * np.mean(2 * np.abs(real - pred) / (np.abs(real) + np.abs(pred)))
        ),
    }


def ajustar(serie):
    return SARIMAX(
        serie,
        order=(3, 0, 0),
        trend="c",
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False, maxiter=200, cov_type="none")


def preparar_series():
    auditoria = pd.read_csv(TABLES / "06_auditoria_semanal.csv", parse_dates=["semana_fin"])
    auditoria = (
        auditoria.loc[auditoria["semana_completa_en_periodo"]]
        .set_index("semana_fin")
        .asfreq("W-SUN")
    )
    horaria = pd.read_csv(DATA / "angamos1_nox_horaria_filtrada.csv", parse_dates=["fecha"])
    re = (
        horaria.loc[horaria["valor_objetivo_valido"] & horaria["es_regimen_re"]]
        .set_index("fecha")["nox_mg_nm3"]
        .resample("W-SUN")
        .agg(["count", "mean"])
        .reindex(auditoria.index)
    )
    return {
        "Media, cobertura 75%": auditoria["nox_media_mg_nm3"].where(auditoria["cobertura"] >= 0.75),
        "Media, cobertura 50%": auditoria["nox_media_mg_nm3"].where(auditoria["cobertura"] >= 0.50),
        "Media, sin umbral": auditoria["nox_media_mg_nm3"],
        "Mediana, cobertura 75%": auditoria["nox_mediana_mg_nm3"].where(auditoria["cobertura"] >= 0.75),
        "Media DM+RE, cobertura 75%": re["mean"].where(re["count"] / 168 >= 0.75),
    }


def main():
    escenarios = {k: v.astype(float) for k, v in preparar_series().items()}
    base = escenarios["Media, cobertura 75%"].interpolate(method="time", limit_area="inside")
    filas = []
    pronosticos = {}

    for nombre, observada in escenarios.items():
        serie = observada.interpolate(method="time", limit_area="inside")
        if serie.isna().any():
            raise ValueError(f"El escenario {nombre} conserva valores ausentes")

        train = serie.iloc[: -(H_VALIDACION + H_PRUEBA)]
        validacion = serie.iloc[-(H_VALIDACION + H_PRUEBA) : -H_PRUEBA]
        prueba = serie.iloc[-H_PRUEBA:]
        prueba_observada = observada.iloc[-H_PRUEBA:].notna().to_numpy()

        fit_train = ajustar(train)
        pred_validacion = np.asarray(fit_train.get_forecast(H_VALIDACION).predicted_mean)
        fit_prueba = ajustar(serie.iloc[:-H_PRUEBA])
        pred_prueba = np.asarray(fit_prueba.get_forecast(H_PRUEBA).predicted_mean)
        fit_completo = ajustar(serie)
        pred_futuro = np.asarray(fit_completo.get_forecast(8).predicted_mean)
        lb = acorr_ljungbox(fit_completo.resid, lags=[10, 20], return_df=True)

        filas.append({
            "escenario": nombre,
            "semanas_imputadas": int(observada.isna().sum()),
            "correlacion_con_base": float(serie.corr(base)),
            **{f"validacion_{k}": v for k, v in metricas(validacion, pred_validacion).items()},
            **{
                f"prueba_{k}": v
                for k, v in metricas(
                    prueba.iloc[prueba_observada], pred_prueba[prueba_observada]
                ).items()
            },
            "prueba_semanas_observadas": int(prueba_observada.sum()),
            "ljung_p_10": float(lb.loc[10, "lb_pvalue"]),
            "ljung_p_20": float(lb.loc[20, "lb_pvalue"]),
            "pronostico_medio_8s": float(pred_futuro.mean()),
            "pronostico_min_8s": float(pred_futuro.min()),
            "pronostico_max_8s": float(pred_futuro.max()),
        })
        pronosticos[nombre] = pred_futuro

    resultados = pd.DataFrame(filas)
    resultados.to_csv(TABLES / "12_analisis_sensibilidad.csv", index=False)

    fechas = pd.date_range(base.index[-1] + pd.Timedelta(weeks=1), periods=8, freq="W-SUN")
    plt.figure(figsize=(11, 5))
    for nombre, valores in pronosticos.items():
        plt.plot(fechas, valores, marker="o", label=nombre)
    plt.xlabel("Semana")
    plt.ylabel("Concentración de NOx (mg/Nm³)")
    plt.title("Pronóstico bajo cinco definiciones de la serie")
    plt.grid(alpha=0.2)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "10_sensibilidad_pronostico.png", dpi=180, bbox_inches="tight")
    plt.close()

    print(resultados.to_string(index=False))


if __name__ == "__main__":
    main()
