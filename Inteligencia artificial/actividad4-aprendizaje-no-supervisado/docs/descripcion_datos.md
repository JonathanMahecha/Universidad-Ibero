# Descripción de las fuentes de datos

**Proyecto:** Sistema Inteligente de Rutas – Transporte Masivo
**Actividad 4:** Métodos de aprendizaje no supervisado
**Problema no supervisado:** descubrir, **sin etiquetas**, grupos de estaciones-hora con un patrón de demanda parecido (perfiles operativos), usando K-means y agrupamiento jerárquico (cap. 16, Palma Méndez, 2008).

---

## 1. Fuentes de datos reales identificadas

| # | Fuente | Publicador | Qué contiene | Uso en el proyecto |
|---|--------|-----------|--------------|--------------------|
| 1 | *Consolidado de salidas del sistema troncal por franja horaria* — [datosabiertos.bogota.gov.co](https://datosabiertos.bogota.gov.co/dataset/consolidado-de-salidas-sistema-troncal-por-franja-horaria) | TransMilenio S.A. / Datos Abiertos Bogotá | Salidas de usuarios por estación troncal y franja horaria | Inspira la demanda por estación y hora, base de los perfiles |
| 2 | *Estaciones troncales de TransMilenio* — [bogota.tumidata.org](https://bogota.tumidata.org/dataset/transmilenio_trunk_stations_bogota) | TransMilenio S.A. | Ubicación, nombre y troncal de cada estación | Inspira los atributos de la base de conocimiento (`zona`, `tipo_estacion`) |
| 3 | *Rutas troncales de TransMilenio* — [bogota.tumidata.org](https://bogota.tumidata.org/dataset/transmilenio_trunk_routes_bogota) | TransMilenio S.A. | Rutas troncales y estaciones que recorren | Inspira la relación estación–línea (`conexiones.csv`) |
| 4 | Datos hidrometeorológicos — [datos.gov.co](https://www.datos.gov.co) | IDEAM | Precipitación | Justifica la variable `efecto_lluvia` |

### ¿Por qué un dataset sintético?

Las fuentes reales están agregadas a otro nivel y usan los nombres reales del sistema, mientras que el proyecto trabaja con una **red simplificada de 11 estaciones y 4 líneas**. Por eso, como lo permite la actividad, se reutiliza el **dataset sintético de operación** construido en la Actividad 3, coherente con la base de conocimiento y con los patrones observados en las fuentes reales.

> A diferencia de la Actividad 3, aquí **no se usa la etiqueta** `nivel_congestion`: el aprendizaje no supervisado debe encontrar los grupos por sí solo.

---

## 2. Archivos de datos del repositorio

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `base_conocimiento/conexiones.csv` | Hechos | 12 conexiones `(origen, destino, línea)` |
| `base_conocimiento/estaciones.csv` | Hechos | 11 estaciones con tipo, zona, capacidad y demanda base |
| `data/generar_dataset.py` | Código | Genera el dataset de operación (semilla 42, reproducible) |
| `data/dataset_operacion.csv` | Datos crudos | 11.118 registros horarios (11 estaciones × 56 días × 18 horas + 30 duplicados) |
| `data/perfiles_estacion_hora.csv` | Datos procesados | 198 perfiles (11 estaciones × 18 horas) con las variables de agrupamiento y el grupo asignado |

---

## 3. Datos crudos – `dataset_operacion.csv`

Periodo simulado: 1 de septiembre al 26 de octubre de 2025, de 5:00 a 22:00. Columnas principales:

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `fecha`, `dia_semana`, `es_fin_semana`, `festivo` | Calendario | Día del registro |
| `estacion`, `linea_principal`, `tipo_estacion`, `zona` | Categórica | Datos de la estación (de la base de conocimiento) |
| `hora`, `franja_horaria` | Tiempo | Hora del día (5–22) y franja (Pico AM, Pico PM, Valle, Baja demanda) |
| `clima` | Categórica | Soleado, Nublado o Lluvia (≈1 % nulos) |
| `evento_especial`, `incidente_operacional` | Binaria | Evento masivo cercano / falla que reduce la frecuencia |
| `buses_por_hora` | Entera | Buses que pasan por la estación en la hora |
| `pasajeros_entrada` | Entera | Validaciones estimadas en la hora |
| `ocupacion_pct` | Decimal | Ocupación respecto a la capacidad de la estación |
| `nivel_congestion` | Etiqueta | **No se usa en esta actividad** |

---

## 4. Datos procesados – `perfiles_estacion_hora.csv`

Cada fila resume **una estación a una hora** durante las 8 semanas. Las 6 variables de agrupamiento se escalan con `StandardScaler` (media 0, desviación 1) antes de entrenar, porque K-means usa distancias y las variables tienen escalas distintas.

| Variable | Cálculo | Qué representa |
|----------|---------|----------------|
| `ocupacion_habil` | Media de `ocupacion_pct` en días hábiles | Carga normal entre semana |
| `ocupacion_finde` | Media de `ocupacion_pct` en fines de semana y festivos | Carga en días de descanso |
| `variabilidad` | Desviación estándar de `ocupacion_pct` en días hábiles | Qué tan predecible es la carga |
| `ocupacion_p90` | Percentil 90 de `ocupacion_pct` en días hábiles | Carga en los días más críticos |
| `efecto_lluvia` | Ocupación con lluvia − ocupación sin lluvia (días hábiles) | Sensibilidad al clima |
| `buses_promedio` | Media de `buses_por_hora` en días hábiles | Frecuencia de servicio |

Columnas descriptivas (no entran al modelo, sirven para interpretar): `estacion`, `hora`, `tipo_estacion`, `zona`, `linea_principal`, `franja_horaria`.
Columnas de resultado: `grupo` (K-means), `grupo_jerarquico` (Ward) y `perfil` (nombre del grupo).

---

## 5. Calidad de los datos

| Problema | Cantidad | Tratamiento |
|----------|----------|-------------|
| Valores nulos en `clima` | 110 (≈1 %) | Imputación con la moda |
| Filas duplicadas | 30 | Eliminadas con `drop_duplicates()` |
| Variables en escalas distintas (% vs. buses) | 6 variables | Estandarización con `StandardScaler` |
