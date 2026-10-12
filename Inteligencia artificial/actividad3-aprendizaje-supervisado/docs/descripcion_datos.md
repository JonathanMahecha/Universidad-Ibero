# Descripción de las fuentes de datos

**Proyecto:** Sistema Inteligente de Rutas – Transporte Masivo
**Actividad 3:** Métodos de aprendizaje supervisado
**Problema supervisado:** predecir el **nivel de congestión** (Baja / Media / Alta) de una estación en una hora determinada.

---

## 1. Fuentes de datos reales identificadas

| # | Fuente | Publicador | Qué contiene | Uso en el proyecto |
|---|--------|-----------|--------------|--------------------|
| 1 | *Consolidado de salidas del sistema troncal por franja horaria* — [datosabiertos.bogota.gov.co](https://datosabiertos.bogota.gov.co/dataset/consolidado-de-salidas-sistema-troncal-por-franja-horaria) | TransMilenio S.A. / Portal de Datos Abiertos de Bogotá | Salidas de usuarios por estación troncal, agregadas por franja horaria | Inspira la variable `pasajeros_entrada`, las franjas horarias y la diferencia entre hora pico y valle |
| 2 | *Estaciones troncales de TransMilenio* — [bogota.tumidata.org](https://bogota.tumidata.org/dataset/transmilenio_trunk_stations_bogota) / Datos Abiertos Bogotá | TransMilenio S.A. | Ubicación, nombre y troncal de cada estación | Inspira los atributos de la base de conocimiento (`zona`, `tipo_estacion`) |
| 3 | *Rutas troncales de TransMilenio* — [bogota.tumidata.org](https://bogota.tumidata.org/dataset/transmilenio_trunk_routes_bogota) | TransMilenio S.A. | Rutas troncales y estaciones que recorren | Inspira la relación estación–línea (`conexiones.csv`) |
| 4 | Datos hidrometeorológicos — [datos.gov.co](https://www.datos.gov.co) | IDEAM | Precipitación por estación meteorológica | Justifica la variable `clima` (la lluvia aumenta la demanda del sistema) |

### ¿Por qué se construyó un dataset sintético?

Las fuentes anteriores son reales pero **no traen una etiqueta de congestión** por estación y hora, están agregadas a otro nivel y usan los nombres reales del sistema, mientras que nuestro proyecto (actividad anterior) trabaja con una **red simplificada de 11 estaciones y 4 líneas**. Por eso, siguiendo la indicación de la actividad (*"en caso de no existir dichas fuentes de datos, desarrolle un dataset con una muestra"*), se generó un dataset sintético **coherente con la base de conocimiento** y con los patrones observados en las fuentes reales.

---

## 2. Archivos de datos del repositorio

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `base_conocimiento/conexiones.csv` | Hechos | 12 conexiones `(origen, destino, línea)` — red de la actividad anterior |
| `base_conocimiento/estaciones.csv` | Hechos | 11 estaciones con tipo, zona, capacidad por hora y demanda base |
| `data/dataset_congestion.csv` | Dataset | 11.118 registros (11 estaciones × 56 días × 18 horas + 30 duplicados) |
| `data/generar_dataset.py` | Código | Script reproducible (semilla 42) que genera el dataset |

**Periodo simulado:** 1 de septiembre al 26 de octubre de 2025 (8 semanas), horario de operación de 5:00 a 22:00. Incluye el festivo del 13 de octubre de 2025.

---

## 3. Diccionario de datos – `dataset_congestion.csv`

| Variable | Tipo | Valores / rango | Descripción | ¿Se usa en el modelo? |
|----------|------|-----------------|-------------|------|
| `fecha` | Fecha | 2025-09-01 … 2025-10-26 | Día del registro | No (identificador) |
| `estacion` | Categórica | 11 estaciones | Nombre de la estación | Sí |
| `linea_principal` | Categórica | Línea A–D | Primera línea a la que pertenece | Sí |
| `tipo_estacion` | Categórica | Portal, Intercambio, Intermedia | Rol en la red | Sí |
| `zona` | Categórica | Norte, Chapinero, Centro, Sur | Zona de la ciudad | Sí |
| `dia_semana` | Categórica | Lunes … Domingo | Día de la semana | Sí |
| `es_fin_semana` | Binaria | 0 / 1 | Sábado o domingo | Sí |
| `festivo` | Binaria | 0 / 1 | Día festivo en Colombia | Sí |
| `hora` | Entera | 5 – 22 | Hora del día | Sí |
| `franja_horaria` | Categórica | Pico AM, Pico PM, Valle, Baja demanda | Agrupación de horas | Sí |
| `clima` | Categórica | Soleado, Nublado, Lluvia | Condición climática (≈1 % nulos) | Sí |
| `evento_especial` | Binaria | 0 / 1 | Concierto, partido u otro evento masivo cercano | Sí |
| `incidente_operacional` | Binaria | 0 / 1 | Falla o bloqueo que reduce la frecuencia | Sí |
| `buses_por_hora` | Entera | 7 – 63 | Buses que pasan por la estación en esa hora | Sí |
| `pasajeros_entrada` | Entera | ≥ 0 | Validaciones estimadas en la hora | **No** (fuga de información) |
| `ocupacion_pct` | Decimal | % | Ocupación respecto a la capacidad | **No** (fuga de información) |
| **`nivel_congestion`** | **Objetivo** | **Baja, Media, Alta** | **Etiqueta a predecir** | **Variable objetivo** |

### Regla de etiquetado

| Nivel | Condición |
|-------|-----------|
| Baja | ocupación < 40 % de la capacidad |
| Media | 40 % ≤ ocupación < 65 % |
| Alta | ocupación ≥ 65 % |

> `pasajeros_entrada` y `ocupacion_pct` se excluyen del modelo porque la etiqueta se calcula a partir de ellas; usarlas sería "hacer trampa" (fuga de información) y en la vida real no se conocen antes de que ocurra la congestión.

### Factores usados para simular la ocupación

- **Franja horaria:** Pico AM (100 %), Pico PM (95 %), Valle (60 %), Baja demanda (35 %).
- **Portales en Pico AM:** +20 % (salida masiva hacia el trabajo).
- **Zona Centro en Pico PM:** +15 % (regreso a casa).
- **Sábado:** 65 %; **Domingo:** 40 %; **Festivo:** 45 %.
- **Lluvia:** +12 %; **Evento especial:** +35 %.
- **Incidente operacional:** reduce los buses un 40 %, lo que aumenta la ocupación.
- **Ruido aleatorio:** normal (μ = 0, σ = 0,07) para simular la variabilidad real.

---

## 4. Calidad de los datos

| Problema | Cantidad | Tratamiento |
|----------|----------|-------------|
| Valores nulos en `clima` | 110 (≈1 %) | Imputación con la moda |
| Filas duplicadas | 30 | Eliminadas con `drop_duplicates()` |

**Distribución de clases (tras limpieza):** Baja ≈ 52 %, Media ≈ 31 %, Alta ≈ 17 %. Por el desbalance se usa división estratificada y la métrica **F1 macro**.
