"""Pruebas del componente. Ejecutar con: python -m pytest -v"""

import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for carpeta in ("base_conocimiento", "data", "src"):
    sys.path.insert(0, str(RAIZ / carpeta))

import agrupamiento as ag  # noqa: E402
from base_conocimiento import buscar_ruta  # noqa: E402
from generar_dataset import generar  # noqa: E402


@pytest.fixture(scope="module")
def perfiles():
    df = generar().drop_duplicates()
    df["clima"] = df["clima"].fillna(df["clima"].mode()[0])
    return ag.construir_perfiles(df)


@pytest.fixture(scope="module")
def X(perfiles):
    return ag.escalar(perfiles)[0]


# ---------------- Base de conocimiento ----------------
def test_ruta_existente():
    ruta, _ = buscar_ruta("Portal Sur", "Calle 100")
    assert ruta[0] == "Portal Sur" and ruta[-1] == "Calle 100"


# ---------------- Preparación de datos ----------------
def test_un_perfil_por_estacion_y_hora(perfiles):
    assert len(perfiles) == 11 * 18
    assert not perfiles.duplicated(["estacion", "hora"]).any()


def test_variables_sin_nulos(perfiles):
    assert perfiles[ag.VARIABLES].isna().sum().sum() == 0


def test_no_usa_etiquetas(perfiles):
    """Aprendizaje no supervisado: la etiqueta de congestión no entra al modelo."""
    assert "nivel_congestion" not in ag.VARIABLES
    assert "nivel_congestion" not in perfiles.columns


def test_escalado_media_cero_desviacion_uno(X):
    assert np.allclose(X.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(X.std(axis=0), 1, atol=1e-9)


# ---------------- Modelo ----------------
def test_seleccion_k_respeta_minimo(X):
    tabla = ag.evaluar_k(X)
    assert ag.elegir_k(tabla) >= ag.K_MINIMO
    assert tabla["inercia"].is_monotonic_decreasing


def test_kmeans_reproducible(X):
    a = ag.entrenar_kmeans(X, 4).labels_
    b = ag.entrenar_kmeans(X, 4).labels_
    assert (a == b).all()


def test_calidad_minima_de_grupos(X):
    from sklearn.metrics import silhouette_score
    etiquetas = ag.entrenar_kmeans(X, 4).labels_
    assert silhouette_score(X, etiquetas) > 0.25


def test_kmeans_y_jerarquico_concuerdan(X):
    from sklearn.metrics import adjusted_rand_score
    km = ag.entrenar_kmeans(X, 4).labels_
    je = ag.entrenar_jerarquico(X, 4).labels_
    assert adjusted_rand_score(km, je) > 0.5


def test_perfiles_ordenados_por_ocupacion(perfiles, X):
    etiquetas = ag.entrenar_kmeans(X, 4).labels_
    nombres = ag.nombrar_perfiles(perfiles, etiquetas)
    medias = perfiles.assign(p=[nombres[e] for e in etiquetas]).groupby("p")["ocupacion_habil"].mean()
    assert medias["Demanda baja"] < medias["Demanda moderada"] < medias["Demanda alta"] < medias["Pico crítico"]


def test_hora_pico_vs_noche(perfiles, X):
    etiquetas = ag.entrenar_kmeans(X, 4).labels_
    nombres = ag.nombrar_perfiles(perfiles, etiquetas)
    p = perfiles.assign(perfil=[nombres[e] for e in etiquetas]).set_index(["estacion", "hora"])["perfil"]
    assert p[("Portal Norte", 7)] in ("Demanda alta", "Pico crítico")
    assert p[("Portal Norte", 22)] == "Demanda baja"


# ---------------- Integración ----------------
def test_integracion_ruta_perfiles():
    from perfil_ruta import mejores_horas, perfil_de_ruta
    if not ag.RUTA_PERFILES.exists():
        pytest.skip("Ejecute primero src/agrupamiento.py")
    tramo = perfil_de_ruta("Portal Norte", "Universidades", 7)
    assert len(tramo) == len(buscar_ruta("Portal Norte", "Universidades")[0])
    horas = mejores_horas("Portal Norte", "Universidades")
    assert len(horas) == 3 and all(h not in (6, 7, 8, 17, 18, 19) for h in horas)
