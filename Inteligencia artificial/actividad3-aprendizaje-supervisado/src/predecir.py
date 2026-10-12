import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "base_conocimiento"))
sys.path.insert(0, str(RAIZ / "data"))
from base_conocimiento import ESTACIONES, buscar_ruta, linea_principal  # noqa: E402
from generar_dataset import franja_horaria  # noqa: E402

RUTA_MODELO = RAIZ / "resultados" / "modelo_congestion.joblib"
BUSES_PROGRAMADOS = {"Pico AM": 60, "Pico PM": 60, "Valle": 40, "Baja demanda": 25}


def construir_registro(estacion, dia, hora, clima, evento=0, incidente=0, festivo=0):
    franja = franja_horaria(hora)
    fin_semana = int(dia in ("Sábado", "Domingo"))
    buses = BUSES_PROGRAMADOS[franja]
    if fin_semana or festivo:
        buses = int(buses * 0.7)
    if incidente:
        buses = int(buses * 0.6)
    info = ESTACIONES[estacion]
    return {
        "estacion": estacion,
        "linea_principal": linea_principal(estacion),
        "tipo_estacion": info["tipo_estacion"],
        "zona": info["zona"],
        "dia_semana": dia,
        "franja_horaria": franja,
        "clima": clima,
        "hora": hora,
        "es_fin_semana": fin_semana,
        "festivo": festivo,
        "evento_especial": evento,
        "incidente_operacional": incidente,
        "buses_por_hora": buses,
    }


def predecir_ruta(origen, destino, dia, hora, clima, evento=0, incidente=0, modelo=None):
    modelo = modelo or joblib.load(RUTA_MODELO)
    ruta, lineas = buscar_ruta(origen, destino)
    if ruta is None:
        return None
    registros = pd.DataFrame([construir_registro(e, dia, hora, clima, evento, incidente) for e in ruta])
    niveles = modelo.predict(registros)
    return list(zip(ruta, ["(origen)"] + lineas, niveles))


def main():
    p = argparse.ArgumentParser(description="Ruta + predicción de congestión")
    p.add_argument("origen")
    p.add_argument("destino")
    p.add_argument("--dia", default="Lunes")
    p.add_argument("--hora", type=int, default=7)
    p.add_argument("--clima", default="Soleado", choices=["Soleado", "Nublado", "Lluvia"])
    p.add_argument("--evento", type=int, default=0, choices=[0, 1])
    p.add_argument("--incidente", type=int, default=0, choices=[0, 1])
    a = p.parse_args()

    resultado = predecir_ruta(a.origen, a.destino, a.dia, a.hora, a.clima, a.evento, a.incidente)
    if resultado is None:
        print("No se encontró una ruta entre las estaciones indicadas.")
        return

    print(f"\nRuta {a.origen} -> {a.destino} | {a.dia} {a.hora}:00 | Clima: {a.clima}\n")
    for estacion, linea, nivel in resultado:
        print(f"  {estacion:<15} {linea:<10} Congestión estimada: {nivel}")
    altas = [e for e, _, n in resultado if n == "Alta"]
    if altas:
        print(f"\nRecomendación: congestión alta en {', '.join(altas)}. Considere otro horario.")


if __name__ == "__main__":
    main()
