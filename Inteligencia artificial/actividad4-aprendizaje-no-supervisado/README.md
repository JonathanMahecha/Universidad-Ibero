# Sistema Inteligente de Rutas – Actividad 4: Aprendizaje no supervisado

Curso de Inteligencia Artificial – Ingeniería de Software, Corporación Universitaria Iberoamericana.

**Integrantes:** Jonathan Mahecha · Juan Manuel Peña
**Tutora:** Sandra Bautista

Continuación del Sistema Inteligente de Rutas. En la Actividad 3 un árbol de decisión aprendió a predecir la congestión a partir de **datos etiquetados**. En esta actividad se usa **aprendizaje no supervisado**: sin ninguna etiqueta, **K-means** y el **agrupamiento jerárquico (Ward)** descubren **perfiles operativos** de cada estación según la hora (demanda baja, moderada, alta y pico crítico). Luego esos perfiles se integran con la búsqueda de rutas para recomendar las mejores horas para viajar.

## Estructura

```
├── base_conocimiento/
│   ├── conexiones.csv              # Hechos: conexiones entre estaciones
│   ├── estaciones.csv              # Hechos: atributos de cada estación
│   └── base_conocimiento.py        # Reglas y búsqueda de rutas (BFS)
├── data/
│   ├── generar_dataset.py          # Genera el dataset de operación
│   ├── dataset_operacion.csv       # 11.118 registros horarios (datos crudos)
│   └── perfiles_estacion_hora.csv  # 198 perfiles estación-hora + grupo asignado
├── src/
│   ├── agrupamiento.py             # Preparación, selección de k, K-means, jerárquico, gráficas
│   └── perfil_ruta.py              # Ruta + perfil de cada estación + horas recomendadas
├── tests/test_proyecto.py          # 12 pruebas automatizadas (pytest)
├── docs/
│   ├── descripcion_datos.md        # Fuentes de datos y diccionario de datos
│   └── pruebas.md                  # Documento de pruebas
└── resultados/                     # Métricas, gráficas, resumen de grupos y modelo
```

## Cómo ejecutar

```bash
pip install -r requirements.txt
python data/generar_dataset.py                                   # 1. Generar los datos
python src/agrupamiento.py                                       # 2. Agrupar y evaluar
python src/perfil_ruta.py "Portal Norte" "Universidades" --hora 7 # 3. Integración con rutas
python -m pytest -v                                              # 4. Pruebas
```

## Resultados

- **k = 4** grupos (método del codo + coeficiente de silueta).
- K-means: silueta 0,356 · Jerárquico Ward: silueta 0,359 · Concordancia (ARI): 0,736.

| Perfil | Registros | Ocupación hábil | Cuándo aparece |
|--------|---------:|---------------:|----------------|
| Demanda baja | 59 | 27,8 % | Primera hora, noche y algunas horas valle |
| Demanda moderada | 73 | 45,5 % | Horas valle |
| Demanda alta | 51 | 69,1 % | Horas pico |
| Pico crítico | 15 | 93,5 % | Portales en la mañana y Centro en la tarde |

Gráficas en `resultados/`: `seleccion_k.png`, `grupos_pca.png`, `mapa_estacion_hora.png` y `dendrograma.png`.

## Video

[Enlace al video en YouTube](PEGAR_ENLACE)
