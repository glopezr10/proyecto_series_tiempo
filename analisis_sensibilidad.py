"""Sensibilidad del AutoReg a cobertura, imputación, mediana y estado RE."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.ar_model import AutoReg


ROOT = Path(__file__).resolve().parent
PROTO = ROOT / "prototipo_entrega"
TABLES = PROTO / "resultados" / "tablas"
FIGURES = PROTO / "resultados" / "figuras"
DATA = PROTO / "data"
LAGS = [1, 2, 3, 4, 52]
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
    return AutoReg(serie, lags=LAGS, trend="ct", old_names=False).fit()


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

    escenarios = {
        "Media, cobertura 75%": auditoria["nox_media_mg_nm3"].where(auditoria["cobertura"] >= 0.75),
        "Media, cobertura 50%": auditoria["nox_media_mg_nm3"].where(auditoria["cobertura"] >= 0.50),
        "Media, sin umbral": auditoria["nox_media_mg_nm3"],
        "Mediana, cobertura 75%": auditoria["nox_mediana_mg_nm3"].where(auditoria["cobertura"] >= 0.75),
        "Media DM+RE, cobertura 75%": re["mean"].where(re["count"] / 168 >= 0.75),
    }
    return {nombre: valores.astype(float) for nombre, valores in escenarios.items()}


def main():
    escenarios = preparar_series()
    filas = []
    pronosticos = {}

    for nombre, observada in escenarios.items():
        imputadas = int(observada.isna().sum())
        serie = observada.interpolate(method="time", limit_area="inside")
        if serie.isna().any():
            raise ValueError(f"El escenario {nombre} conserva valores ausentes")

        train = serie.iloc[: -(H_VALIDACION + H_PRUEBA)]
        valid = serie.iloc[-(H_VALIDACION + H_PRUEBA) : -H_PRUEBA]
        test = serie.iloc[-H_PRUEBA:]

        fit_train = ajustar(train)
        pred_valid = np.asarray(
            fit_train.predict(start=len(train), end=len(train) + H_VALIDACION - 1)
        )
        fit_test = ajustar(serie.iloc[:-H_PRUEBA])
        pred_test = np.asarray(
            fit_test.predict(start=len(serie) - H_PRUEBA, end=len(serie) - 1)
        )
        fit_full = ajustar(serie)
        pred_future = np.asarray(
            fit_full.predict(start=len(serie), end=len(serie) + 7)
        )
        lb = acorr_ljungbox(fit_full.resid, lags=[10, 20], return_df=True)

        filas.append(
            {
                "escenario": nombre,
                "semanas_imputadas": imputadas,
                "correlacion_con_base": float(
                    serie.corr(
                        escenarios["Media, cobertura 75%"].interpolate(
                            method="time", limit_area="inside"
                        )
                    )
                ),
                **{f"validacion_{k}": v for k, v in metricas(valid, pred_valid).items()},
                **{f"prueba_{k}": v for k, v in metricas(test, pred_test).items()},
                "ljung_p_10": float(lb.loc[10, "lb_pvalue"]),
                "ljung_p_20": float(lb.loc[20, "lb_pvalue"]),
                "pronostico_medio_8s": float(pred_future.mean()),
                "pronostico_min_8s": float(pred_future.min()),
                "pronostico_max_8s": float(pred_future.max()),
            }
        )
        pronosticos[nombre] = pred_future

    resultados = pd.DataFrame(filas)
    resultados.to_csv(TABLES / "12_analisis_sensibilidad.csv", index=False)

    orden = resultados.sort_values("prueba_RMSE")
    plt.figure(figsize=(11, 5))
    colores = ["#173f5f" if x == "Media, cobertura 75%" else "#6c8ead" for x in orden["escenario"]]
    plt.barh(orden["escenario"], orden["prueba_RMSE"], color=colores)
    plt.xlabel("RMSE en prueba (mg/Nm³)")
    plt.title("Sensibilidad del modelo AutoReg a la construcción de la serie")
    plt.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIGURES / "09_sensibilidad_construccion_serie.png", dpi=180, bbox_inches="tight")
    plt.close()

    fechas = pd.date_range(
        next(iter(escenarios.values())).index[-1] + pd.Timedelta(weeks=1),
        periods=8,
        freq="W-SUN",
    )
    plt.figure(figsize=(11, 5))
    for nombre, valores in pronosticos.items():
        plt.plot(fechas, valores, marker="o", label=nombre)
    plt.ylabel("NOx pronosticado (mg/Nm³)")
    plt.title("Pronóstico AutoReg bajo cinco definiciones de la serie")
    plt.grid(alpha=0.2)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "10_sensibilidad_pronostico.png", dpi=180, bbox_inches="tight")
    plt.close()

    print(resultados.to_string(index=False))


if __name__ == "__main__":
    main()
