"""Regenera la figura de validación incluyendo el modelo AutoReg seleccionado."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.holtwinters import Holt


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "prototipo_entrega" / "data" / "angamos1_nox_semanal_modelo.csv"
OUT = ROOT / "prototipo_entrega" / "resultados" / "figuras" / "05_validacion_modelos.png"

serie = pd.read_csv(DATA, parse_dates=["semana_fin"]).set_index("semana_fin")["nox_modelo_mg_nm3"].astype(float)
train = serie.iloc[:-40]
validacion = serie.iloc[-40:-8]
h = len(validacion)

pronosticos = {
    "Ingenuo último valor": np.repeat(train.iloc[-1], h),
    "Drift": train.iloc[-1]
    + ((train.iloc[-1] - train.iloc[0]) / (len(train) - 1)) * np.arange(1, h + 1),
}
ar = AutoReg(train, lags=[1, 2, 3, 4, 52], trend="ct", old_names=False).fit()
pronosticos["AutoReg rezagos 1-4 y 52"] = np.asarray(
    ar.predict(start=len(train), end=len(train) + h - 1)
)
holt = Holt(train, damped_trend=True, initialization_method="estimated").fit(optimized=True)
pronosticos["Holt amortiguado"] = np.asarray(holt.forecast(h))

plt.figure(figsize=(12, 5))
plt.plot(validacion, label="Observado", color="black", linewidth=2.2)
for nombre, valores in pronosticos.items():
    plt.plot(validacion.index, valores, label=nombre, alpha=0.9)
plt.title("Comparación de los cuatro mejores modelos en validación")
plt.ylabel("mg/Nm³")
plt.xlabel("Semana")
plt.grid(alpha=0.2)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(OUT, dpi=180, bbox_inches="tight")
plt.close()
print(OUT)
