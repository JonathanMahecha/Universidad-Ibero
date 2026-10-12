# Sistema Inteligente de Rutas – Actividad 3: Aprendizaje supervisado

Curso de Inteligencia Artificial – Ingeniería de Software, Corporación Universitaria Iberoamericana.

**Integrantes:** Jonathan Mahecha · Juan Manuel Peña

Continuación del sistema basado en conocimiento de la actividad anterior (búsqueda de rutas con BFS). En esta actividad se agrega un **modelo de aprendizaje supervisado (árbol de decisión)** que predice el **nivel de congestión** (Baja / Media / Alta) de cada estación según el día, la hora, el clima, los eventos y la operación del sistema.

## Estructura

```
├── base_conocimiento/
│   ├── conexiones.csv          # Hechos: conexiones entre estaciones (actividad anterior)
│   ├── estaciones.csv          # Hechos: atributos de cada estación
│   └── base_conocimiento.py    # Reglas: vecinos, transbordo y búsqueda de rutas (BFS)
├── data/
│   ├── generar_dataset.py      # Genera el dataset sintético (reproducible)
│   └── dataset_congestion.csv  # 11.118 registros
├── src/
│   ├── modelo_congestion.py    # Exploración, limpieza, entrenamiento y evaluación
│   └── predecir.py             # Ruta + congestión estimada en cada estación
├── tests/test_proyecto.py      # 11 pruebas automatizadas (pytest)
├── docs/
│   ├── descripcion_datos.md    # Fuentes de datos y diccionario de datos
│   └── pruebas.md              # Documento de pruebas
└── resultados/                 # Métricas, gráficas, reglas del árbol y modelo entrenado
```

## Cómo ejecutar

```bash
pip install -r requirements.txt
python data/generar_dataset.py           # 1. Generar el dataset
python src/modelo_congestion.py          # 2. Entrenar y evaluar el modelo
python src/predecir.py "Portal Norte" "Universidades" --dia Lunes --hora 7 --clima Lluvia
python -m pytest -v                      # 3. Ejecutar las pruebas
```

## Resultados

| Modelo | Accuracy | F1 macro |
|--------|---------:|---------:|
| Línea base (clase más frecuente) | 0,521 | 0,228 |
| **Árbol de decisión (entropía)** | **0,851** | **0,845** |
| Random Forest | 0,826 | 0,818 |

Las reglas SI–ENTONCES aprendidas por el árbol están en `resultados/reglas_arbol.txt`.

## Video

[Enlace al video en YouTube](PEGAR_ENLACE)
