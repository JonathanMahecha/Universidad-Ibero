conexiones = [
    ("Portal Norte", "Calle 100", "Línea A"),
    ("Calle 100", "Calle 72", "Línea A"),
    ("Calle 72", "Calle 45", "Línea A"),
    ("Calle 45", "Museo", "Línea A"),
    ("Museo", "Centro", "Línea B"),
    ("Centro", "Las Aguas", "Línea B"),
    ("Las Aguas", "Universidades", "Línea B"),
    ("Calle 72", "Héroes", "Línea C"),
    ("Héroes", "Calle 45", "Línea C"),
    ("Calle 45", "Centro", "Línea C"),
    ("Portal Sur", "Restrepo", "Línea D"),
    ("Restrepo", "Centro", "Línea D"),
]


def normalizar_texto(texto):
    return texto.strip().lower()


def obtener_estaciones():
    estaciones = set()

    for origen, destino, linea in conexiones:
        estaciones.add(origen)
        estaciones.add(destino)

    return sorted(estaciones)


def buscar_estacion(nombre):

    nombre_normalizado = normalizar_texto(nombre)

    for estacion in obtener_estaciones():

        if normalizar_texto(estacion) == nombre_normalizado:
            return estacion

    return None


def obtener_vecinos(estacion):
    vecinos = []

    for origen, destino, linea in conexiones:

        if origen == estacion:
            vecinos.append((destino, linea))

        elif destino == estacion:
            vecinos.append((origen, linea))

    return vecinos


def buscar_ruta(origen, destino):

    cola = [(origen, [origen], [])]

    visitadas = set()

    while cola:

        estacion_actual, ruta, lineas = cola.pop(0)

        if estacion_actual == destino:
            return ruta, lineas

        if estacion_actual in visitadas:
            continue

        visitadas.add(estacion_actual)

        vecinos = obtener_vecinos(estacion_actual)

        for siguiente, linea in vecinos:

            if siguiente not in visitadas:

                nueva_ruta = ruta + [siguiente]
                nuevas_lineas = lineas + [linea]

                cola.append((siguiente, nueva_ruta, nuevas_lineas))

    return None, None


def generar_resultado(origen, destino):

    ruta, lineas = buscar_ruta(origen, destino)

    if ruta is None:

        return "NO SE ENCONTRÓ UNA RUTA\n\n" f"Origen: {origen}\n" f"Destino: {destino}"

    resultado = "RUTA ENCONTRADA\n"
    resultado += "=" * 45 + "\n\n"

    resultado += f"Origen:  {origen}\n"
    resultado += f"Destino: {destino}\n\n"

    resultado += "RECORRIDO:\n\n"

    for i, estacion in enumerate(ruta):

        if i == 0:
            resultado += f"  ● {estacion}\n"

        else:
            resultado += f"  │\n"
            resultado += f"  ├── {lineas[i - 1]}\n"
            resultado += f"  ↓\n"
            resultado += f"  ● {estacion}\n"

    resultado += "\n"
    resultado += "=" * 45 + "\n"

    resultado += f"Estaciones recorridas: {len(ruta) - 1}"

    return resultado


def mostrar_estaciones():
    print("\nEstaciones disponibles:")

    for estacion in obtener_estaciones():
        print(f"  - {estacion}")


def solicitar_estacion(mensaje):

    while True:

        entrada = input(mensaje).strip()

        estacion = buscar_estacion(entrada)

        if estacion:
            return estacion

        print(f"'{entrada}' no es una estación válida. Revisa la lista de arriba.\n")


def buscar():

    mostrar_estaciones()

    origen = solicitar_estacion("\nEstación de origen: ")
    destino = solicitar_estacion("Estación de destino: ")

    if normalizar_texto(origen) == normalizar_texto(destino):
        print("\nLa estación de origen y destino deben ser diferentes.")
        return

    print()
    print(generar_resultado(origen, destino))


def main():

    print("=" * 45)
    print("SISTEMA INTELIGENTE DE RUTAS - TRANSPORTE MASIVO")
    print("=" * 45)

    while True:

        buscar()

        respuesta = input("\n¿Buscar otra ruta? (s/n): ").strip().lower()

        if respuesta != "s":
            print("\n¡Hasta luego!")
            break


if __name__ == "__main__":
    main()