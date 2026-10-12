"""Pruebas del componente. Ejecutar con: python -m pytest -v"""

import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for carpeta in ("base_conocimiento", "data", "src"):
    sys.path.insert(0, str(RAIZ / carpeta))

from base_conocimiento import buscar_ruta, es_transbordo, obtener_estaciones  # noqa: E402
from generar_dataset import franja_horaria, generar  # noqa: E402
import modelo_congestion as mc  # noqa: E402


@pytest.fixture(scope="module")
def datos():
    return mc.limpiar(generar())


# ---------------- Base de conocimiento ----------------
def test_base_conocimiento_tiene_11_estaciones():
    assert len(obtener_estaciones()) == 11


def test_ruta_existente():
    ruta, lineas = buscar_ruta("Portal Norte", "Universidades")
    assert ruta[0] == "Portal Norte" and ruta[-1] == "Universidades"
    assert len(lineas) == len(ruta) - 1


def test_ruta_estacion_inexistente():
    assert buscar_ruta("Portal Norte", "Estación X") == (None, None)


def test_reglas_transbordo():
    assert es_transbordo("Centro") and not es_transbordo("Calle 100")


# ---------------- Dataset ----------------
def test_franja_horaria():
    assert franja_horaria(7) == "Pico AM"
    assert franja_horaria(18) == "Pico PM"
    assert franja_horaria(12) == "Valle"
    assert franja_horaria(22) == "Baja demanda"


def test_dataset_reproducible():
    pd.testing.assert_frame_equal(generar(semilla=1), generar(semilla=1))


def test_limpieza_sin_nulos_ni_duplicados(datos):
    assert datos["clima"].isna().sum() == 0
    assert datos.duplicated().sum() == 0


def test_etiquetas_validas(datos):
    assert set(datos["nivel_congestion"]) == {"Baja", "Media", "Alta"}


def test_sin_fuga_de_informacion():
    X, _ = mc.separar_variables(mc.limpiar(generar()))
    for columna in mc.COLUMNAS_EXCLUIDAS:
        assert columna not in X.columns


# ---------------- Modelo ----------------
def test_modelo_supera_linea_base(datos):
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier

    X, y = mc.separar_variables(datos)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
    modelo = mc.crear_pipeline(DecisionTreeClassifier(criterion="entropy", max_depth=8,
                                                      random_state=0)).fit(X_tr, y_tr)
    metrica = mc.evaluar("arbol", modelo, X_te, y_te)
    assert metrica["accuracy"] > 0.75
    assert metrica["f1_macro"] > 0.70


def test_prediccion_ruta_hora_pico_vs_noche():
    from predecir import predecir_ruta

    if not mc.CARPETA_RESULTADOS.joinpath("modelo_congestion.joblib").exists():
        pytest.skip("Ejecute primero src/modelo_congestion.py")
    pico = predecir_ruta("Portal Norte", "Centro", "Lunes", 7, "Lluvia")
    noche = predecir_ruta("Portal Norte", "Centro", "Domingo", 22, "Soleado")
    orden = {"Baja": 0, "Media": 1, "Alta": 2}
    assert sum(orden[n] for *_, n in pico) > sum(orden[n] for *_, n in noche)
