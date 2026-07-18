"""Ruta estable: baselines y familia de suavizamiento exponencial."""

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing

import prototipo_modelado as piloto


def ajustar_modelos_estables(train, h):
    resultados = []
    for nombre, funcion in [
        ("Ingenuo último valor", piloto.pronostico_ingenuo),
        ("Ingenuo estacional 52", piloto.pronostico_estacional),
        ("Drift", piloto.pronostico_drift),
    ]:
        resultados.append(
            {"modelo": nombre, "ajuste": None, "pronostico": funcion(train, h), "AIC": np.nan}
        )

    especificaciones = [
        ("SES", lambda: SimpleExpSmoothing(train, initialization_method="estimated").fit(optimized=True)),
        (
            "Holt amortiguado",
            lambda: Holt(train, damped_trend=True, initialization_method="estimated").fit(optimized=True),
        ),
        (
            "ETS aditivo 52",
            lambda: ExponentialSmoothing(
                train,
                trend="add",
                damped_trend=True,
                seasonal="add",
                seasonal_periods=piloto.PERIODO_ESTACIONAL,
                initialization_method="estimated",
            ).fit(optimized=True, use_brute=False),
        ),
    ]
    for nombre, constructor in especificaciones:
        print(f"Ajustando {nombre}...", flush=True)
        ajuste = constructor()
        resultados.append(
            {
                "modelo": nombre,
                "ajuste": ajuste,
                "pronostico": np.asarray(ajuste.forecast(h)),
                "AIC": float(getattr(ajuste, "aic", np.nan)),
            }
        )
    return resultados


piloto.ajustar_modelos = ajustar_modelos_estables


if __name__ == "__main__":
    piloto.main()
