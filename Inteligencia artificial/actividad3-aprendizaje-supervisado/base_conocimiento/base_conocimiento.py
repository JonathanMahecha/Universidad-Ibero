"""
Base de conocimiento del Sistema Inteligente de Rutas (actividad anterior y actividad actual).

Hechos:
    - conexiones.csv : conexion(origen, destino, linea)
    - estaciones.csv : estacion(nombre, tipo, zona, capacidad_hora, demanda_base)

Reglas:
    - vecino(A, B, L)   <- conexion(A, B, L) o conexion(B, A, L)
    - es_transbordo(E)  <- E pertenece a 2 o más líneas
    - ruta(O, D)        <- búsqueda en anchura (BFS) sobre vecino/3
"""

import csv
from collections import deque
from pathlib import Path

CARPETA = Path(__file__).resolve().parent


def _leer_csv(nombre):
    with open(CARPETA / nombre, encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


# ---------------------------- HECHOS ----------------------------
CONEXIONES = [(f["origen"], f["destino"], f["linea"]) for f in _leer_csv("conexiones.csv")]

ESTACIONES = {
    f["estacion"]: {
        "tipo_estacion": f["tipo_estacion"],
        "zona": f["zona"],
        "capacidad_hora": int(f["capacidad_hora"]),
        "demanda_base": float(f["demanda_base"]),
    }
    for f in _leer_csv("estaciones.csv")
}


# ---------------------------- REGLAS ----------------------------
def obtener_estaciones():
    return sorted(ESTACIONES)


def obtener_vecinos(estacion):
    """Regla vecino(A, B, L): las conexiones son bidireccionales."""
    vecinos = []
    for origen, destino, linea in CONEXIONES:
        if origen == estacion:
            vecinos.append((destino, linea))
        elif destino == estacion:
            vecinos.append((origen, linea))
    return vecinos


def lineas_de_estacion(estacion):
    return sorted({linea for _, linea in obtener_vecinos(estacion)})


def es_transbordo(estacion):
    """Regla es_transbordo(E): la estación pertenece a dos o más líneas."""
    return len(lineas_de_estacion(estacion)) >= 2


def linea_principal(estacion):
    return lineas_de_estacion(estacion)[0]


def buscar_ruta(origen, destino):
    """Búsqueda en anchura (BFS): devuelve (ruta, lineas) o (None, None)."""
    if origen not in ESTACIONES or destino not in ESTACIONES:
        return None, None

    cola = deque([(origen, [origen], [])])
    visitadas = set()

    while cola:
        actual, ruta, lineas = cola.popleft()
        if actual == destino:
            return ruta, lineas
        if actual in visitadas:
            continue
        visitadas.add(actual)
        for siguiente, linea in obtener_vecinos(actual):
            if siguiente not in visitadas:
                cola.append((siguiente, ruta + [siguiente], lineas + [linea]))

    return None, None


if __name__ == "__main__":
    print("Estaciones:", obtener_estaciones())
    print("Transbordos:", [e for e in obtener_estaciones() if es_transbordo(e)])
    print("Ruta Portal Norte -> Universidades:", buscar_ruta("Portal Norte", "Universidades"))
