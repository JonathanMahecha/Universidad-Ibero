# Documento de pruebas del componente

**Herramienta:** pytest — **Comando:** `python -m pytest -v` — **Resultado:** 12 de 12 pruebas aprobadas (ver `resultados/resultado_pruebas.txt`).

## 1. Pruebas unitarias automatizadas

| ID | Componente | Caso de prueba | Resultado esperado | Estado |
|----|-----------|----------------|--------------------|--------|
| PU-01 | Base de conocimiento | Ruta Portal Sur → Calle 100 | Ruta inicia y termina en las estaciones indicadas | ✅ |
| PU-02 | Preparación | Construcción de perfiles | 198 filas (11 × 18), sin estación-hora repetida | ✅ |
| PU-03 | Preparación | Nulos en variables de agrupamiento | 0 nulos | ✅ |
| PU-04 | Preparación | Uso de etiquetas | `nivel_congestion` no entra al modelo (no supervisado) | ✅ |
| PU-05 | Preparación | Estandarización | Media 0 y desviación 1 en cada variable | ✅ |
| PU-06 | Modelo | Selección de k | k elegido ≥ 3 e inercia decreciente al aumentar k | ✅ |
| PU-07 | Modelo | Reproducibilidad de K-means | Mismas etiquetas en dos ejecuciones | ✅ |
| PU-08 | Modelo | Calidad de los grupos | Coeficiente de silueta > 0,25 | ✅ |
| PU-09 | Modelo | K-means vs. jerárquico | Índice Rand ajustado (ARI) > 0,5 | ✅ |
| PU-10 | Interpretación | Nombres de perfiles | Ocupación media: baja < moderada < alta < pico crítico | ✅ |
| PU-11 | Interpretación | Portal Norte 7:00 vs. 22:00 | 7:00 = alta o pico crítico; 22:00 = demanda baja | ✅ |
| PU-12 | Integración | Ruta + perfiles + horas recomendadas | Un perfil por estación; 3 horas recomendadas fuera de hora pico | ✅ |

## 2. Evaluación del agrupamiento (198 perfiles estación-hora)

**Selección de k** (método del codo y coeficiente de silueta):

| k | Inercia | Silueta |
|---|--------:|--------:|
| 2 | 537,41 | 0,489 |
| 3 | 403,22 | 0,339 |
| **4** | **300,01** | **0,356** |
| 5 | 260,45 | 0,334 |
| 6 | 226,52 | 0,320 |

k = 2 tiene la silueta más alta, pero solo separa "hora pico" de "no pico", algo obvio sin modelo. Desde k = 3, la mejor silueta es **k = 4**, que además coincide con el codo de la inercia (la caída de 3 a 4 es grande y luego se suaviza).

| Método | Silueta | Davies-Bouldin |
|--------|--------:|---------------:|
| K-means (k = 4) | 0,356 | 0,987 |
| Jerárquico Ward (k = 4) | 0,359 | 0,874 |

Concordancia entre ambos métodos: **ARI = 0,736**. Dos técnicas distintas encuentran grupos muy parecidos, lo que indica que los grupos son estables.

## 3. Perfiles encontrados

| Perfil | Registros | Ocupación hábil | Ocupación fin de semana | P90 | Efecto lluvia | Buses/hora | Cuándo aparece |
|--------|---------:|----:|----:|----:|----:|----:|----|
| Demanda baja | 59 | 27,8 % | 15,0 % | 37,1 % | +2,8 | 28,6 | 5:00, 20:00–22:00 y algunas horas valle |
| Demanda moderada | 73 | 45,5 % | 23,9 % | 56,2 % | +5,5 | 39,4 | Horas valle |
| Demanda alta | 51 | 69,1 % | 36,9 % | 80,1 % | +6,3 | 59,2 | Horas pico |
| Pico crítico | 15 | 93,5 % | 48,2 % | 109,7 % | +13,2 | 58,3 | Portales en la mañana, Centro en la tarde |

## 4. Pruebas funcionales manuales

| ID | Entrada | Resultado esperado | Resultado obtenido |
|----|---------|-------------------|--------------------|
| PF-01 | `perfil_ruta.py "Portal Norte" "Universidades" --hora 7` | Portal Norte en pico crítico, resto alto | Portal Norte: Pico crítico; 6 estaciones: Demanda alta; horas recomendadas 10:00, 11:00, 20:00 ✅ |
| PF-02 | `perfil_ruta.py "Portal Sur" "Calle 100" --hora 18` | Centro en pico crítico | Centro: Pico crítico; resto: Demanda alta ✅ |
| PF-03 | Estación inexistente | Mensaje "No se encontró una ruta" | ✅ |
