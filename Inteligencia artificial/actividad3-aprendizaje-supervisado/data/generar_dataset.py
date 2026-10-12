import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "base_conocimiento"))
from base_conocimiento import ESTACIONES, linea_principal  # noqa: E402

SEMILLA = 42
FECHA_INICIO = date(2025, 9, 1)
SEMANAS = 8
HORAS = range(5, 23)  # operación 5:00 a 22:00
FESTIVOS = {date(2025, 10, 13)}  # Día de la Raza (Colombia, trasladado a lunes)
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

UMBRAL_MEDIA = 0.40  # ocupación >= 40 % de la capacidad
UMBRAL_ALTA = 0.65   # ocupación >= 65 % de la capacidad


def franja_horaria(hora):
    if 6 <= hora <= 8:
        return "Pico AM"
    if 17 <= hora <= 19:
        return "Pico PM"
    if hora >= 20 or hora == 5:
        return "Baja demanda"
    return "Valle"


FACTOR_FRANJA = {"Pico AM": 1.00, "Pico PM": 0.95, "Valle": 0.60, "Baja demanda": 0.35}
FACTOR_DIA = {"Sábado": 0.65, "Domingo": 0.40}


def generar(semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    filas = []

    for d in range(SEMANAS * 7):
        fecha = FECHA_INICIO + timedelta(days=d)
        dia = DIAS[fecha.weekday()]
        festivo = int(fecha in FESTIVOS)
        clima_dia = rng.choice(["Soleado", "Nublado", "Lluvia"], p=[0.40, 0.35, 0.25])

        for estacion, info in ESTACIONES.items():
            evento_dia = int(info["zona"] in ("Chapinero", "Centro") and rng.random() < 0.05)

            for hora in HORAS:
                franja = franja_horaria(hora)
                clima = clima_dia if rng.random() > 0.2 else rng.choice(["Soleado", "Nublado", "Lluvia"])
                evento = int(evento_dia and 16 <= hora <= 21)
                incidente = int(rng.random() < 0.04)

                # Frecuencia programada de buses (más buses en hora pico)
                buses_prog = 60 if franja.startswith("Pico") else 40 if franja == "Valle" else 25
                if dia in FACTOR_DIA or festivo:
                    buses_prog = int(buses_prog * 0.7)
                buses = int(buses_prog * (0.6 if incidente else 1.0) + rng.integers(-3, 4))

                # Ocupación latente = demanda / capacidad
                ocupacion = info["demanda_base"] * FACTOR_FRANJA[franja]
                if info["tipo_estacion"] == "Portal" and franja == "Pico AM":
                    ocupacion *= 1.20  # salida masiva desde los portales
                if info["zona"] == "Centro" and franja == "Pico PM":
                    ocupacion *= 1.15  # regreso desde el centro
                ocupacion *= FACTOR_DIA.get(dia, 1.0)
                if festivo:
                    ocupacion *= 0.45
                if clima == "Lluvia":
                    ocupacion *= 1.12
                if evento:
                    ocupacion *= 1.35
                ocupacion *= buses_prog / max(buses, 1)  # menos buses => más gente esperando
                ocupacion = max(0.02, ocupacion + rng.normal(0, 0.07))

                if ocupacion >= UMBRAL_ALTA:
                    nivel = "Alta"
                elif ocupacion >= UMBRAL_MEDIA:
                    nivel = "Media"
                else:
                    nivel = "Baja"

                filas.append({
                    "fecha": fecha.isoformat(),
                    "estacion": estacion,
                    "linea_principal": linea_principal(estacion),
                    "tipo_estacion": info["tipo_estacion"],
                    "zona": info["zona"],
                    "dia_semana": dia,
                    "es_fin_semana": int(dia in FACTOR_DIA),
                    "festivo": festivo,
                    "hora": hora,
                    "franja_horaria": franja,
                    "clima": clima,
                    "evento_especial": evento,
                    "incidente_operacional": incidente,
                    "buses_por_hora": buses,
                    "pasajeros_entrada": int(ocupacion * info["capacidad_hora"]),
                    "ocupacion_pct": round(ocupacion * 100, 1),
                    "nivel_congestion": nivel,
                })

    df = pd.DataFrame(filas)

    # Simula problemas reales de calidad de datos para la etapa de limpieza
    idx_nulos = rng.choice(df.index, size=int(len(df) * 0.01), replace=False)
    df.loc[idx_nulos, "clima"] = np.nan
    duplicados = df.sample(n=30, random_state=semilla)
    df = pd.concat([df, duplicados], ignore_index=True)
    return df


if __name__ == "__main__":
    df = generar()
    salida = RAIZ / "data" / "dataset_congestion.csv"
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"Dataset generado: {salida} ({len(df)} filas, {df.shape[1]} columnas)")
    print(df["nivel_congestion"].value_counts(normalize=True).round(3))
