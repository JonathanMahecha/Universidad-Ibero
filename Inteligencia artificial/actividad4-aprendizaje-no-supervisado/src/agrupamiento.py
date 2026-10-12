"""
Actividad 4 - Aprendizaje no supervisado: perfiles operativos de estaciones.

Agrupa cada combinación (estación, hora) según su patrón de demanda, sin usar
ninguna etiqueta. Técnicas del capítulo 16 (Técnicas de agrupamiento) de
Palma Méndez (2008):
    - K-means (agrupamiento por particiones)
    - Agrupamiento jerárquico aglomerativo (método de Ward) y dendrograma

Uso:
    python src/agrupamiento.py
Salidas en resultados/ y data/perfiles_estacion_hora.csv
"""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from scipy.cluster.hierarchy import dendrogram, linkage  # noqa: E402
from sklearn.cluster import AgglomerativeClustering, KMeans  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,  # noqa: E402
                             davies_bouldin_score, silhouette_score)
from sklearn.preprocessing import StandardScaler  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "dataset_operacion.csv"
RUTA_PERFILES = RAIZ / "data" / "perfiles_estacion_hora.csv"
CARPETA_RESULTADOS = RAIZ / "resultados"
SEMILLA = 42
RANGO_K = range(2, 9)
# k = 2 solo separa "hora pico" de "no pico", algo que ya se sabe sin modelo.
# Para obtener perfiles útiles se elige el k con mejor silueta a partir de 3.
K_MINIMO = 3

# Variables con las que se agrupa (todas numéricas y calculadas por estación-hora)
VARIABLES = [
    "ocupacion_habil",      # % de ocupación promedio en días hábiles
    "ocupacion_finde",      # % de ocupación promedio en fin de semana / festivo
    "variabilidad",         # desviación estándar de la ocupación en días hábiles
    "ocupacion_p90",        # percentil 90 de ocupación (días más críticos)
    "efecto_lluvia",        # diferencia de ocupación con lluvia vs. sin lluvia
    "buses_promedio",       # frecuencia promedio de buses
]

# Paleta categórica (orden fijo; color por perfil, no por posición)
COLORES = ["#2a78d6", "#1baf7a", "#eda100", "#eb6834", "#6250d6", "#e87ba4", "#008300", "#e34948"]
TINTA = "#52514e"


# --------------------------------------------------------------- 1. Datos
def cargar_datos(ruta=RUTA_DATOS):
    df = pd.read_csv(ruta, encoding="utf-8")
    df = df.drop_duplicates().copy()
    df["clima"] = df["clima"].fillna(df["clima"].mode()[0])
    return df


def construir_perfiles(df):
    """Ingeniería de características: un registro por (estación, hora)."""
    habil = df[(df["es_fin_semana"] == 0) & (df["festivo"] == 0)]
    descanso = df[(df["es_fin_semana"] == 1) | (df["festivo"] == 1)]
    claves = ["estacion", "hora"]

    perfiles = habil.groupby(claves).agg(
        ocupacion_habil=("ocupacion_pct", "mean"),
        variabilidad=("ocupacion_pct", "std"),
        ocupacion_p90=("ocupacion_pct", lambda s: s.quantile(0.9)),
        buses_promedio=("buses_por_hora", "mean"),
    )
    perfiles["ocupacion_finde"] = descanso.groupby(claves)["ocupacion_pct"].mean()

    lluvia = habil[habil["clima"] == "Lluvia"].groupby(claves)["ocupacion_pct"].mean()
    seco = habil[habil["clima"] != "Lluvia"].groupby(claves)["ocupacion_pct"].mean()
    perfiles["efecto_lluvia"] = (lluvia - seco).fillna(0)

    info = df.drop_duplicates("estacion").set_index("estacion")[
        ["tipo_estacion", "zona", "linea_principal"]]
    perfiles = perfiles.reset_index().merge(info, on="estacion")
    perfiles["franja_horaria"] = df.drop_duplicates("hora").set_index("hora").loc[
        perfiles["hora"], "franja_horaria"].values
    return perfiles.round(2)


def escalar(perfiles):
    escalador = StandardScaler()
    X = escalador.fit_transform(perfiles[VARIABLES])
    return X, escalador


# ------------------------------------------------------- 2. Elegir k
def evaluar_k(X):
    filas = []
    for k in RANGO_K:
        km = KMeans(n_clusters=k, n_init=20, random_state=SEMILLA).fit(X)
        filas.append({"k": k, "inercia": round(km.inertia_, 2),
                      "silueta": round(silhouette_score(X, km.labels_), 4)})
    return pd.DataFrame(filas)


def elegir_k(tabla, k_minimo=K_MINIMO):
    candidatos = tabla[tabla["k"] >= k_minimo]
    return int(candidatos.loc[candidatos["silueta"].idxmax(), "k"])


# -------------------------------------------------- 3. Agrupamientos
def entrenar_kmeans(X, k):
    return KMeans(n_clusters=k, n_init=20, random_state=SEMILLA).fit(X)


def entrenar_jerarquico(X, k):
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit(X)


def nombrar_perfiles(perfiles, etiquetas):
    """Asigna un nombre interpretable a cada grupo según su ocupación media."""
    nombres_por_k = {
        2: ["Demanda baja", "Hora pico"],
        3: ["Demanda baja", "Demanda moderada", "Hora pico"],
        4: ["Demanda baja", "Demanda moderada", "Demanda alta", "Pico crítico"],
    }
    medias = perfiles.assign(grupo=etiquetas).groupby("grupo")["ocupacion_habil"].mean()
    orden = medias.sort_values().index
    nombres = nombres_por_k.get(len(orden), [f"Perfil {i + 1}" for i in range(len(orden))])
    return {grupo: nombre for grupo, nombre in zip(orden, nombres)}


# --------------------------------------------------- 4. Gráficas
def _estilo(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3)


def graficar_k(tabla, k):
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
    ejes[0].plot(tabla["k"], tabla["inercia"], marker="o", color=COLORES[0], lw=2)
    ejes[0].set(title="Método del codo", xlabel="Número de grupos (k)", ylabel="Inercia")
    ejes[1].plot(tabla["k"], tabla["silueta"], marker="o", color=COLORES[0], lw=2)
    ejes[1].axvline(k, color=TINTA, ls="--", lw=1)
    ejes[1].annotate(f"k = {k}", (k, tabla["silueta"].max()), xytext=(8, -12),
                     textcoords="offset points", color=TINTA)
    ejes[1].set(title="Coeficiente de silueta", xlabel="Número de grupos (k)", ylabel="Silueta")
    for ax in ejes:
        _estilo(ax)
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "seleccion_k.png", dpi=150)
    plt.close(fig)


def graficar_pca(X, perfiles, nombres):
    pca = PCA(n_components=2, random_state=SEMILLA)
    puntos = pca.fit_transform(X)
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, (grupo, nombre) in enumerate(nombres.items()):
        m = perfiles["grupo"] == grupo
        ax.scatter(puntos[m, 0], puntos[m, 1], s=45, color=COLORES[i], label=nombre,
                   edgecolor="white", linewidth=1)
    var = pca.explained_variance_ratio_ * 100
    ax.set(title="Perfiles de estación-hora (K-means) proyectados con PCA",
           xlabel=f"Componente 1 ({var[0]:.0f} % de la varianza)",
           ylabel=f"Componente 2 ({var[1]:.0f} % de la varianza)")
    ax.legend(frameon=False)
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "grupos_pca.png", dpi=150)
    plt.close(fig)


def graficar_mapa(perfiles, nombres):
    orden_nombres = list(nombres.values())
    codigo = {g: i for i, g in enumerate(nombres)}
    tabla = perfiles.pivot(index="estacion", columns="hora", values="grupo").replace(codigo)
    tabla = tabla.loc[perfiles.groupby("estacion")["ocupacion_habil"].mean().sort_values().index]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    cmap = ListedColormap(COLORES[:len(nombres)])
    ax.imshow(tabla.values.astype(int), cmap=cmap, aspect="auto", vmin=-0.5, vmax=len(nombres) - 0.5)
    ax.set_xticks(range(tabla.shape[1]), [f"{h}h" for h in tabla.columns])
    ax.set_yticks(range(tabla.shape[0]), tabla.index)
    ax.set_xticks(np.arange(-0.5, tabla.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, tabla.shape[0]), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    ax.set_title("Perfil operativo por estación y hora (días hábiles)", color=TINTA)
    manijas = [plt.Rectangle((0, 0), 1, 1, color=COLORES[i]) for i in range(len(orden_nombres))]
    ax.legend(manijas, orden_nombres, loc="upper center", bbox_to_anchor=(0.5, -0.1),
              ncol=len(orden_nombres), frameon=False)
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "mapa_estacion_hora.png", dpi=150)
    plt.close(fig)


def graficar_dendrograma(X, perfiles, k):
    Z = linkage(X, method="ward")
    corte = (Z[-k, 2] + Z[-(k - 1), 2]) / 2  # punto medio entre las dos últimas uniones
    fig, ax = plt.subplots(figsize=(12, 5))
    dendrogram(Z, truncate_mode="lastp", p=30, color_threshold=corte,
               above_threshold_color=TINTA, ax=ax)
    ax.axhline(corte, color=TINTA, ls="--", lw=1)
    ax.set(title=f"Dendrograma (Ward) – corte en {k} grupos",
           xlabel="Registros estación-hora (agrupados)", ylabel="Distancia")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(CARPETA_RESULTADOS / "dendrograma.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------- Principal
def main():
    CARPETA_RESULTADOS.mkdir(exist_ok=True)

    print("=" * 60)
    print("1. PREPARACIÓN DE DATOS")
    print("=" * 60)
    df = cargar_datos()
    perfiles = construir_perfiles(df)
    print(f"Registros originales (limpios): {len(df)}")
    print(f"Perfiles estación-hora: {len(perfiles)} ({perfiles['estacion'].nunique()} estaciones "
          f"x {perfiles['hora'].nunique()} horas)")
    print(perfiles[VARIABLES].describe().round(2).T[["mean", "std", "min", "max"]])
    X, escalador = escalar(perfiles)

    print("\n" + "=" * 60)
    print("2. SELECCIÓN DEL NÚMERO DE GRUPOS")
    print("=" * 60)
    tabla_k = evaluar_k(X)
    k = elegir_k(tabla_k)
    print(tabla_k.to_string(index=False))
    print(f"\nk elegido (máxima silueta con k >= {K_MINIMO}): {k}")

    print("\n" + "=" * 60)
    print("3. AGRUPAMIENTO")
    print("=" * 60)
    kmeans = entrenar_kmeans(X, k)
    jerarquico = entrenar_jerarquico(X, k)
    perfiles["grupo"] = kmeans.labels_
    perfiles["grupo_jerarquico"] = jerarquico.labels_
    nombres = nombrar_perfiles(perfiles, kmeans.labels_)
    perfiles["perfil"] = perfiles["grupo"].map(nombres)

    metricas = {
        "registros": int(len(perfiles)),
        "k": k,
        "seleccion_k": tabla_k.to_dict(orient="records"),
        "kmeans": {
            "silueta": round(silhouette_score(X, kmeans.labels_), 4),
            "davies_bouldin": round(davies_bouldin_score(X, kmeans.labels_), 4),
            "calinski_harabasz": round(calinski_harabasz_score(X, kmeans.labels_), 2),
        },
        "jerarquico_ward": {
            "silueta": round(silhouette_score(X, jerarquico.labels_), 4),
            "davies_bouldin": round(davies_bouldin_score(X, jerarquico.labels_), 4),
        },
        "concordancia_kmeans_vs_jerarquico_ARI": round(
            adjusted_rand_score(kmeans.labels_, jerarquico.labels_), 4),
    }
    print(f"K-means      -> silueta {metricas['kmeans']['silueta']}, "
          f"Davies-Bouldin {metricas['kmeans']['davies_bouldin']}")
    print(f"Jerárquico   -> silueta {metricas['jerarquico_ward']['silueta']}, "
          f"Davies-Bouldin {metricas['jerarquico_ward']['davies_bouldin']}")
    print(f"Concordancia entre ambos métodos (ARI): {metricas['concordancia_kmeans_vs_jerarquico_ARI']}")

    print("\n" + "=" * 60)
    print("4. INTERPRETACIÓN DE LOS GRUPOS")
    print("=" * 60)
    resumen = perfiles.groupby("perfil").agg(
        registros=("estacion", "size"), **{v: (v, "mean") for v in VARIABLES}).round(1)
    resumen = resumen.sort_values("ocupacion_habil")
    print(resumen.to_string())
    print("\nFranjas horarias por perfil:")
    print(pd.crosstab(perfiles["perfil"], perfiles["franja_horaria"]).loc[resumen.index].to_string())
    print("\nTipo de estación por perfil:")
    print(pd.crosstab(perfiles["perfil"], perfiles["tipo_estacion"]).loc[resumen.index].to_string())

    graficar_k(tabla_k, k)
    graficar_pca(X, perfiles, nombres)
    graficar_mapa(perfiles, nombres)
    graficar_dendrograma(X, perfiles, k)

    perfiles.to_csv(RUTA_PERFILES, index=False, encoding="utf-8")
    resumen.to_csv(CARPETA_RESULTADOS / "resumen_grupos.csv", encoding="utf-8")
    (CARPETA_RESULTADOS / "metricas.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    joblib.dump({"escalador": escalador, "kmeans": kmeans, "nombres": nombres, "variables": VARIABLES},
                CARPETA_RESULTADOS / "modelo_kmeans.joblib")
    print("\nResultados guardados en 'resultados/' y perfiles en 'data/perfiles_estacion_hora.csv'.")


if __name__ == "__main__":
    main()
