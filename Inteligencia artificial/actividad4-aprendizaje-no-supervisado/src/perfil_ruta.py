"""
Integra la búsqueda de rutas (base de conocimiento) con los perfiles
encontrados por K-means: muestra el perfil operativo de cada estación de la
ruta a una hora dada y las horas recomendadas para viajar.

Uso:
    python src/perfil_ruta.py "Portal Norte" "Universidades" --hora 7
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "base_conocimiento"))
from base_conocimiento import buscar_ruta  # noqa: E402

RUTA_PERFILES = RAIZ / "data" / "perfiles_estacion_hora.csv"
ORDEN = {"Demanda baja": 0, "Demanda moderada": 1, "Demanda alta": 2, "Pico crítico": 3}


def cargar_perfiles(ruta=RUTA_PERFILES):
    return pd.read_csv(ruta, encoding="utf-8")


def perfil_de_ruta(origen, destino, hora, perfiles=None):
    """Devuelve [(estacion, linea, perfil)] o None si no hay ruta."""
    perfiles = perfiles if perfiles is not None else cargar_perfiles()
    ruta, lineas = buscar_ruta(origen, destino)
    if ruta is None:
        return None
    indice = perfiles.set_index(["estacion", "hora"])["perfil"]
    return [(e, l, indice[(e, hora)]) for e, l in zip(ruta, ["(origen)"] + lineas)]


def mejores_horas(origen, destino, perfiles=None, top=3, desde=6, hasta=20):
    """Horas en las que la ruta tiene menor carga total según los perfiles."""
    perfiles = perfiles if perfiles is not None else cargar_perfiles()
    puntajes = {}
    for hora in range(desde, hasta + 1):
        tramo = perfil_de_ruta(origen, destino, hora, perfiles)
        if tramo is None:
            return []
        puntajes[hora] = sum(ORDEN.get(p, 0) for *_, p in tramo)
    return sorted(sorted(puntajes, key=lambda h: (puntajes[h], h))[:top])


def main():
    p = argparse.ArgumentParser(description="Perfil operativo de una ruta")
    p.add_argument("origen")
    p.add_argument("destino")
    p.add_argument("--hora", type=int, default=7, choices=range(5, 23))
    a = p.parse_args()

    tramo = perfil_de_ruta(a.origen, a.destino, a.hora)
    if tramo is None:
        print("No se encontró una ruta entre las estaciones indicadas.")
        return
    print(f"\nRuta {a.origen} -> {a.destino} a las {a.hora}:00 (día hábil)\n")
    for estacion, linea, perfil in tramo:
        print(f"  {estacion:<15} {linea:<10} Perfil: {perfil}")
    horas = mejores_horas(a.origen, a.destino)
    print(f"\nHoras recomendadas para esta ruta (entre 6:00 y 20:00): "
          f"{', '.join(f'{h}:00' for h in horas)}")


if __name__ == "__main__":
    main()
