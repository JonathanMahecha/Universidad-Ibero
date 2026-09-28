import tkinter as tk
from tkinter import ttk, messagebox

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


def buscar():

    origen = combo_origen.get()
    destino = combo_destino.get()

    if not origen or not destino:

        messagebox.showwarning(
            "Datos incompletos",
            "Seleccione una estación de origen y una " "estación de destino.",
        )

        return

    if normalizar_texto(origen) == normalizar_texto(destino):

        messagebox.showwarning(
            "Estaciones iguales",
            "La estación de origen y destino deben ser diferentes.",
        )

        return

    resultado = generar_resultado(origen, destino)

    texto_resultado.config(state="normal")

    texto_resultado.delete("1.0", tk.END)

    texto_resultado.insert(tk.END, resultado)

    texto_resultado.config(state="disabled")


def limpiar():

    combo_origen.set("")
    combo_destino.set("")

    texto_resultado.config(state="normal")

    texto_resultado.delete("1.0", tk.END)

    texto_resultado.insert(
        tk.END, "Seleccione un origen y un destino\n" "para encontrar una ruta."
    )

    texto_resultado.config(state="disabled")


def salir():

    respuesta = messagebox.askyesno(
        "Salir", "¿Está seguro de que desea cerrar el sistema?"
    )

    if respuesta:
        ventana.destroy()


ventana = tk.Tk()

ventana.title("Sistema Inteligente de Rutas - Transporte Masivo")

ventana.geometry("850x650")

ventana.minsize(750, 550)

ventana.configure(bg="#f2f4f7")

estilo = ttk.Style()

estilo.theme_use("clam")

estilo.configure("Titulo.TLabel", font=("Arial", 22, "bold"), background="#f2f4f7")

estilo.configure("Subtitulo.TLabel", font=("Arial", 11), background="#f2f4f7")

estilo.configure("Campo.TLabel", font=("Arial", 11, "bold"), background="#f2f4f7")

estilo.configure("Buscar.TButton", font=("Arial", 11, "bold"), padding=8)

estilo.configure("Normal.TButton", font=("Arial", 10), padding=6)


frame_titulo = tk.Frame(ventana, bg="#f2f4f7")

frame_titulo.pack(fill="x", padx=30, pady=(25, 5))


titulo = ttk.Label(
    frame_titulo, text="Sistema Inteligente de Rutas", style="Titulo.TLabel"
)

titulo.pack()


subtitulo = ttk.Label(
    frame_titulo,
    text="Sistema basado en conocimiento para búsqueda de rutas",
    style="Subtitulo.TLabel",
)

subtitulo.pack(pady=(5, 0))


frame_seleccion = tk.LabelFrame(
    ventana,
    text=" Selección de ruta ",
    font=("Arial", 11, "bold"),
    bg="#ffffff",
    padx=20,
    pady=20,
)

frame_seleccion.pack(fill="x", padx=30, pady=20)


# Origen

label_origen = ttk.Label(
    frame_seleccion, text="Estación de origen:", style="Campo.TLabel"
)

label_origen.grid(row=0, column=0, padx=10, pady=10, sticky="w")


combo_origen = ttk.Combobox(
    frame_seleccion, values=obtener_estaciones(), state="readonly", width=30
)

combo_origen.grid(row=0, column=1, padx=10, pady=10)


# Destino

label_destino = ttk.Label(
    frame_seleccion, text="Estación de destino:", style="Campo.TLabel"
)

label_destino.grid(row=1, column=0, padx=10, pady=10, sticky="w")


combo_destino = ttk.Combobox(
    frame_seleccion, values=obtener_estaciones(), state="readonly", width=30
)

combo_destino.grid(row=1, column=1, padx=10, pady=10)


# ==========================================================
# 15. BOTONES
# ==========================================================

frame_botones = tk.Frame(frame_seleccion, bg="#ffffff")

frame_botones.grid(row=0, column=2, rowspan=2, padx=30)


boton_buscar = ttk.Button(
    frame_botones, text="🔎 Buscar ruta", style="Buscar.TButton", command=buscar
)

boton_buscar.pack(pady=5)


boton_limpiar = ttk.Button(
    frame_botones, text="Limpiar", style="Normal.TButton", command=limpiar
)

boton_limpiar.pack(pady=5)


# ==========================================================
# 16. ÁREA DE RESULTADOS
# ==========================================================

frame_resultado = tk.LabelFrame(
    ventana,
    text=" Resultado ",
    font=("Arial", 11, "bold"),
    bg="#ffffff",
    padx=15,
    pady=15,
)

frame_resultado.pack(fill="both", expand=True, padx=30, pady=(0, 20))


texto_resultado = tk.Text(
    frame_resultado,
    font=("Courier New", 11),
    bg="#fafafa",
    relief="flat",
    padx=15,
    pady=15,
    wrap="word",
)

texto_resultado.pack(fill="both", expand=True)


texto_resultado.insert(
    tk.END, "Seleccione un origen y un destino\n" "para encontrar una ruta."
)

texto_resultado.config(state="disabled")


# ==========================================================
# 17. BOTÓN SALIR
# ==========================================================

frame_salir = tk.Frame(ventana, bg="#f2f4f7")

frame_salir.pack(fill="x", padx=30, pady=(0, 20))


boton_salir = ttk.Button(
    frame_salir, text="Salir", style="Normal.TButton", command=salir
)

boton_salir.pack(side="right")


# ==========================================================
# 18. EJECUTAR APLICACIÓN
# ==========================================================

ventana.mainloop()
