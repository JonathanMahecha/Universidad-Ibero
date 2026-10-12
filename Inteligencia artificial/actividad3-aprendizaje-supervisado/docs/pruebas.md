# Documento de pruebas del componente

**Herramienta:** pytest — **Comando:** `python -m pytest -v` — **Resultado:** 11 de 11 pruebas aprobadas (ver `resultados/resultado_pruebas.txt`).

## 1. Pruebas unitarias automatizadas

| ID | Componente | Caso de prueba | Resultado esperado | Estado |
|----|-----------|----------------|--------------------|--------|
| PU-01 | Base de conocimiento | Cargar estaciones | 11 estaciones | ✅ |
| PU-02 | Base de conocimiento | Ruta Portal Norte → Universidades | Ruta inicia y termina correctamente; nº líneas = nº tramos | ✅ |
| PU-03 | Base de conocimiento | Ruta hacia estación inexistente | `(None, None)` | ✅ |
| PU-04 | Reglas | `es_transbordo` en Centro y Calle 100 | Centro = sí, Calle 100 = no | ✅ |
| PU-05 | Dataset | Franja de las 7, 12, 18 y 22 h | Pico AM, Valle, Pico PM, Baja demanda | ✅ |
| PU-06 | Dataset | Generar dos veces con la misma semilla | Dataframes idénticos (reproducible) | ✅ |
| PU-07 | Limpieza | Nulos y duplicados tras `limpiar()` | 0 nulos, 0 duplicados | ✅ |
| PU-08 | Dataset | Etiquetas de la variable objetivo | Solo Baja, Media, Alta | ✅ |
| PU-09 | Modelo | Columnas con fuga de información | No están en X | ✅ |
| PU-10 | Modelo | Árbol de decisión vs. umbral | Accuracy > 0,75 y F1 macro > 0,70 | ✅ |
| PU-11 | Integración | Ruta Lunes 7:00 con lluvia vs. Domingo 22:00 | Mayor congestión en hora pico | ✅ |

## 2. Evaluación del modelo (conjunto de prueba, 2.218 registros)

| Modelo | Accuracy | F1 macro |
|--------|---------:|---------:|
| Línea base (clase más frecuente) | 0,521 | 0,228 |
| **Árbol de decisión (entropía)** | **0,851** | **0,845** |
| Random Forest | 0,826 | 0,818 |

Mejores hiperparámetros (GridSearchCV, 5 folds): `max_depth = 8`, `min_samples_leaf = 1`.

| Clase | Precisión | Recall | F1 |
|-------|---------:|-------:|---:|
| Baja | 0,91 | 0,89 | 0,90 |
| Media | 0,74 | 0,80 | 0,77 |
| Alta | 0,91 | 0,83 | 0,87 |

**Análisis:** el modelo nunca confunde Baja con Alta (ver `matriz_confusion.png`); los errores se concentran en la clase intermedia, que es la frontera natural entre ambos extremos.

## 3. Pruebas funcionales manuales

| ID | Entrada | Resultado esperado | Resultado obtenido |
|----|---------|-------------------|--------------------|
| PF-01 | `predecir.py "Portal Norte" "Universidades" --dia Lunes --hora 7 --clima Lluvia` | Congestión mayoritariamente Alta + recomendación | 5 estaciones Alta, 2 Media, muestra recomendación ✅ |
| PF-02 | `predecir.py "Portal Sur" "Calle 100" --dia Domingo --hora 21` | Congestión Baja | Todas Baja ✅ |
| PF-03 | Origen o destino inexistente | Mensaje "No se encontró una ruta" | ✅ |
