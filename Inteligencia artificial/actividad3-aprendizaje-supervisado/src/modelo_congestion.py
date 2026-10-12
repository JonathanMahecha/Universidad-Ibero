import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import OneHotEncoder  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "dataset_congestion.csv"
CARPETA_RESULTADOS = RAIZ / "resultados"
SEMILLA = 42

OBJETIVO = "nivel_congestion"
CLASES = ["Baja", "Media", "Alta"]
VARIABLES_CATEGORICAS = [
    "estacion", "linea_principal", "tipo_estacion", "zona",
    "dia_semana", "franja_horaria", "clima",
]
VARIABLES_NUMERICAS = [
    "hora", "es_fin_semana", "festivo", "evento_especial",
    "incidente_operacional", "buses_por_hora",
]
# Columnas excluidas: 'pasajeros_entrada' y 'ocupacion_pct' se usan para
# calcular la etiqueta (fuga de información) y 'fecha' es solo identificador.
COLUMNAS_EXCLUIDAS = ["fecha", "pasajeros_entrada", "ocupacion_pct"]

AZUL = "#2a78d6"
TINTA = "#52514e"


# ------------------------------------------------------------------ 1. Carga
def cargar_datos(ruta=RUTA_DATOS):
    return pd.read_csv(ruta, encoding="utf-8")


def explorar(df):
    print("=" * 60)
    print("1. EXPLORACIÓN DE DATOS")
    print("=" * 60)
    print(f"Filas: {df.shape[0]}  Columnas: {df.shape[1]}")
    print("\nValores nulos por columna:")
    print(df.isna().sum()[df.isna().sum() > 0])
    print(f"\nFilas duplicadas: {df.duplicated().sum()}")
    print("\nDistribución de la variable objetivo:")
    print(df[OBJETIVO].value_counts())
    print("\nCongestión promedio (% ocupación) por franja horaria:")
    print(df.groupby("franja_horaria")["ocupacion_pct"].mean().round(1).sort_values())


# -------------------------------------------------------------- 2. Limpieza
def limpiar(df):
    df = df.drop_duplicates().copy()
    df["clima"] = df["clima"].fillna(df["clima"].mode()[0])
    return df


def separar_variables(df):
    X = df[VARIABLES_CATEGORICAS + VARIABLES_NUMERICAS]
    y = df[OBJETIVO]
    return X, y


# ----------------------------------------------------------- 3. Modelado
def crear_pipeline(clasificador):
    preprocesador = ColumnTransformer([
        ("categoricas", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         VARIABLES_CATEGORICAS),
        ("numericas", "passthrough", VARIABLES_NUMERICAS),
    ], verbose_feature_names_out=False)
    return Pipeline([("preprocesamiento", preprocesador), ("modelo", clasificador)])


def entrenar_arbol(X_train, y_train):
    pipeline = crear_pipeline(DecisionTreeClassifier(criterion="entropy", random_state=SEMILLA))
    parametros = {
        "modelo__max_depth": [3, 4, 6, 8, 10, 12],
        "modelo__min_samples_leaf": [1, 5, 10, 20],
    }
    busqueda = GridSearchCV(pipeline, parametros, cv=5, scoring="f1_macro", n_jobs=-1)
    busqueda.fit(X_train, y_train)
    return busqueda


def evaluar(nombre, modelo, X_test, y_test):
    pred = modelo.predict(X_test)
    return {
        "modelo": nombre,
        "accuracy": round(accuracy_score(y_test, pred), 4),
        "f1_macro": round(f1_score(y_test, pred, average="macro"), 4),
    }


# --------------------------------------------------------- 4. Resultados
def guardar_graficas(modelo, X_test, y_test):
    arbol = modelo.named_steps["modelo"]
    nombres = modelo.named_steps["preprocesamiento"].get_feature_names_out()

    # Matriz de confusión
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_estimator(modelo, X_test, y_test, labels=CLASES,
                                          cmap="Blues", colorbar=False, ax=ax)
    ax.set_title("Matriz de confusión - Árbol de decisión", color=TINTA)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "matriz_confusion.png", dpi=150)
    plt.close(fig)

    # Importancia de variables (top 12)
    importancias = (pd.Series(arbol.feature_importances_, index=nombres)
                    .sort_values(ascending=True).tail(12))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(importancias.index, importancias.values, color=AZUL, height=0.6)
    ax.set_title("Variables más importantes para predecir la congestión", color=TINTA)
    ax.set_xlabel("Importancia (reducción de entropía)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "importancia_variables.png", dpi=150)
    plt.close(fig)

    # Árbol (primeros 3 niveles para que sea legible)
    fig, ax = plt.subplots(figsize=(22, 10))
    plot_tree(arbol, feature_names=list(nombres), class_names=list(arbol.classes_),
              max_depth=3, filled=True, rounded=True, fontsize=8, ax=ax)
    ax.set_title("Árbol de decisión (primeros 3 niveles)")
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "arbol_decision.png", dpi=130)
    plt.close(fig)

    # Reglas de decisión SI-ENTONCES en texto
    reglas = export_text(arbol, feature_names=list(nombres), max_depth=6)
    (CARPETA_RESULTADOS / "reglas_arbol.txt").write_text(reglas, encoding="utf-8")


def main():
    CARPETA_RESULTADOS.mkdir(exist_ok=True)

    df = cargar_datos()
    explorar(df)
    df = limpiar(df)
    X, y = separar_variables(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEMILLA)
    print(f"\nEntrenamiento: {len(X_train)} filas | Prueba: {len(X_test)} filas")

    print("\n" + "=" * 60)
    print("2. ENTRENAMIENTO Y COMPARACIÓN DE MODELOS")
    print("=" * 60)
    base = crear_pipeline(DummyClassifier(strategy="most_frequent")).fit(X_train, y_train)
    busqueda = entrenar_arbol(X_train, y_train)
    arbol = busqueda.best_estimator_
    bosque = crear_pipeline(RandomForestClassifier(
        n_estimators=200, random_state=SEMILLA, n_jobs=-1)).fit(X_train, y_train)

    print(f"Mejores hiperparámetros del árbol: {busqueda.best_params_}")
    print(f"F1 macro en validación cruzada (5 folds): {busqueda.best_score_:.4f}")

    comparacion = [
        evaluar("Línea base (clase más frecuente)", base, X_test, y_test),
        evaluar("Árbol de decisión (entropía)", arbol, X_test, y_test),
        evaluar("Random Forest", bosque, X_test, y_test),
    ]
    print("\n" + pd.DataFrame(comparacion).to_string(index=False))

    print("\n" + "=" * 60)
    print("3. EVALUACIÓN DEL ÁRBOL DE DECISIÓN (conjunto de prueba)")
    print("=" * 60)
    reporte = classification_report(y_test, arbol.predict(X_test), labels=CLASES)
    print(reporte)

    guardar_graficas(arbol, X_test, y_test)
    joblib.dump(arbol, CARPETA_RESULTADOS / "modelo_congestion.joblib")

    metricas = {
        "filas_entrenamiento": len(X_train),
        "filas_prueba": len(X_test),
        "mejores_hiperparametros": busqueda.best_params_,
        "f1_macro_validacion_cruzada": round(busqueda.best_score_, 4),
        "comparacion_prueba": comparacion,
        "profundidad_arbol": int(arbol.named_steps["modelo"].get_depth()),
        "hojas_arbol": int(arbol.named_steps["modelo"].get_n_leaves()),
    }
    (CARPETA_RESULTADOS / "metricas.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    (CARPETA_RESULTADOS / "reporte_clasificacion.txt").write_text(reporte, encoding="utf-8")
    print("Resultados guardados en la carpeta 'resultados/'.")


if __name__ == "__main__":
    main()
