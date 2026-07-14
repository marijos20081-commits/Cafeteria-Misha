import tkinter as tk
from tkinter import messagebox


# Estas variables viven en la memoria mientras el programa está
# abierto. NO se guardan en archivos, así que al cerrar el programa
# se pierden. Esto mantiene el código simple (no se necesita json,
# ni leer/escribir archivos).


usuarios = {}       
pedidos = []        # lista de pedidos ya enviados a cocina

usuario_actual = None   # nombre de la persona que inició sesión
rol_actual = None       # "Recepcionista" o "Cocina"

pedido_actual = {}  # producto = [cantidad, precio]  (el pedido que se está armando)

MENU = {
    "Café americano": 1.50,
    "Café con leche": 1.75,
    "Cappuccino": 2.25,
    "Té": 1.00,
    "Jugo de naranja": 2.00,
    "Agua embotellada": 1.00,
    "Sánduche de jamón": 2.75,
    "Empanada": 1.50,
    "Torta de chocolate": 2.50,
}

# Cuanto hay de cada ingrediente en la cocina.Igual que "pedidos" y "usuarios", esto vive solo en memoria.

ingredientes = {
    "Café molido (g)": 2000,
    "Leche (ml)": 5000,
    "Agua (ml)": 10000,
    "Azúcar (g)": 2000,
    "Bolsitas de té": 100,
    "Naranjas (unidades)": 50,
    "Botellas de agua": 50,
    "Pan (rebanadas)": 100,
    "Jamón (Cortes)": 60,
    "Queso (Cortes)": 60,
    "Masa de empanada (unidades)": 50,
    "Torta de chocolate (porciones)": 30,}

# La "receta" de cada producto, qué ingredientes y cuánto de cada uno se gasta al preparar UNA unidad de ese producto.

RECETAS = {
    "Café americano": {"Café molido (g)": 10, "Agua (ml)": 150},
    "Café con leche": {"Café molido (g)": 10, "Leche (ml)": 100},
    "Cappuccino": {"Café molido (g)": 12, "Leche (ml)": 120},
    "Té": {"Bolsitas de té": 1, "Agua (ml)": 150},
    "Jugo de naranja": {"Naranjas (unidades)": 2, "Azúcar (g)": 10},
    "Agua embotellada": {"Botellas de agua": 1},
    "Sánduche de jamón": {"Pan (rebanadas)": 2, "Jamón (lonchas)": 2, "Queso (lonchas)": 1},
    "Empanada": {"Masa de empanada (unidades)": 1},
    "Torta de chocolate": {"Torta de chocolate (porciones)": 1},}

# Colores y fuentes usados en toda la interfaz
COLOR_FONDO = "#F5EFE1"
COLOR_VINO = "#7B2D3B"
COLOR_BLANCO = "#FFFFFF"
COLOR_NEGRO = "#221F1F"

FUENTE_TITULO = ("Arial", 20, "bold")
FUENTE_NORMAL = ("Arial", 11)
FUENTE_BOTON = ("Arial", 11, "bold")

# funciones de validacion

def campo_valido(texto):        #Revisa que el campo no esté vacío

    return len(texto.strip()) > 0


def numero_positivo(texto):   #Revisa que el texto sea un número entero mayor a 0.
    
    texto = texto.strip()
    return texto.isdigit() and int(texto) > 0


def numero_no_negativo(texto): #Revisa que el texto sea un número entero mayor o igual a 0 (permite el 0)
    
    return texto.strip().isdigit()



# inventario: cuánto se necesita y si alcanza 


def calcular_ingredientes_necesarios(items):  #items: diccionario producto = cantidad. Devuelve cuánto se necesita de cada ingrediente para preparar todo eso.
   
    necesarios = {}
    for producto, cantidad in items.items():
        receta = RECETAS.get(producto, {})
        for ingrediente, cantidad_por_unidad in receta.items():
            necesarios[ingrediente] = necesarios.get(ingrediente, 0) + cantidad_por_unidad * cantidad
    return necesarios


def ingredientes_faltantes(items):         #Devuelve una lista de textos con los ingredientes que no alcanzan para preparar los "items". Si la lista está vacía, es porque sí hay suficiente stock.
    
    necesarios = calcular_ingredientes_necesarios(items)
    faltantes = []
    for ingrediente, cantidad_necesaria in necesarios.items():
        disponible = ingredientes.get(ingrediente, 0)
        if cantidad_necesaria > disponible:
            faltantes.append(f"{ingrediente}: se necesitan {cantidad_necesaria}, hay {disponible}")
    return faltantes



# registro y inicio 


def registrar_usuario():
    nombre = entry_nombre_registro.get()
    usuario = entry_usuario_registro.get().strip()
    clave = entry_clave_registro.get()
    confirmar = entry_confirmar_registro.get()
    rol = rol_var.get()

    if not campo_valido(nombre):
        messagebox.showwarning("Nombre inválido", "Escribe tu nombre completo.")
        return
    if not campo_valido(usuario):
        messagebox.showwarning("Usuario inválido", "Escribe un nombre de usuario.")
        return
    if len(clave) < 4:
        messagebox.showwarning("Contraseña inválida", "La contraseña debe tener al menos 4 caracteres.")
        return
    if clave != confirmar:
        messagebox.showwarning("No coinciden", "Las contraseñas no son iguales.")
        return
    if usuario in usuarios:
        messagebox.showwarning("Usuario ocupado", "Ese usuario ya existe, elige otro.")
        return

    usuarios[usuario] = {"nombre": nombre.strip(), "clave": clave, "rol": rol}
    messagebox.showinfo("Registro exitoso", f"¡Listo, {nombre.strip()}! Ya puedes iniciar sesión.")
    ventana_registro.destroy()


def iniciar_sesion():
    global usuario_actual, rol_actual

    usuario = entry_usuario_login.get().strip()
    clave = entry_clave_login.get()

    if usuario not in usuarios or usuarios[usuario]["clave"] != clave:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        return

    usuario_actual = usuarios[usuario]["nombre"]
    rol_actual = usuarios[usuario]["rol"]
    frame_login.destroy()

    if rol_actual == "Cocina":
        pantalla_cocina()
    else:
        pantalla_pedidos()


def cerrar_sesion():
    global usuario_actual, rol_actual

    if not messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas salir?"):
        return

    pedido_actual.clear()
    usuario_actual = None
    rol_actual = None
    frame_principal.destroy()
    pantalla_login()



# pantalla de pedidos 1


def agregar_producto():
    seleccion = lista_menu.curselection()
    if not seleccion:
        messagebox.showwarning("Selecciona un producto", "Elige un producto del menú.")
        return

    texto = lista_menu.get(seleccion[0])
    nombre_producto, precio_texto = texto.split(" - $")
    precio = float(precio_texto)

    cantidad_texto = entry_cantidad.get()
    if not numero_positivo(cantidad_texto):
        messagebox.showwarning("Cantidad inválida", "Ingresa una cantidad mayor a 0.")
        return
    cantidad = int(cantidad_texto)

   # Simulamos cómo quedaría el pedido con este producto agregado,para revisar si a cocina le alcanzan los ingredientes

    items_probables = {nombre: datos[0] for nombre, datos in pedido_actual.items()}
    items_probables[nombre_producto] = items_probables.get(nombre_producto, 0) + cantidad

    faltantes = ingredientes_faltantes(items_probables)
    if faltantes:
        mensaje = "A cocina le faltan estos ingredientes:\n\n" + "\n".join(faltantes)
        messagebox.showwarning("Ingredientes insuficientes", mensaje)
        return

    if nombre_producto in pedido_actual:
        pedido_actual[nombre_producto][0] += cantidad
    else:
        pedido_actual[nombre_producto] = [cantidad, precio]

    entry_cantidad.delete(0, tk.END)
    actualizar_lista_pedido()


def quitar_producto():
    seleccion = lista_pedido.curselection()
    if not seleccion:
        messagebox.showwarning("Selecciona un producto", "Elige un producto del pedido.")
        return

    nombre_producto = list(pedido_actual.keys())[seleccion[0]]
    del pedido_actual[nombre_producto]
    actualizar_lista_pedido()


def actualizar_lista_pedido():
    lista_pedido.delete(0, tk.END)
    total = 0
    for nombre, (cantidad, precio) in pedido_actual.items():
        subtotal = cantidad * precio
        total += subtotal
        lista_pedido.insert(tk.END, f"{cantidad} x {nombre} = ${subtotal:.2f}")
    label_total.config(text=f"TOTAL: ${total:.2f}")


def finalizar_pedido():
    cliente = entry_cliente.get()
    mesa = entry_mesa.get()

    if not campo_valido(cliente):
        messagebox.showwarning("Nombre inválido", "Escribe el nombre del cliente.")
        return
    if not numero_positivo(mesa):
        messagebox.showwarning("Mesa inválida", "Ingresa un número de mesa válido.")
        return
    if not pedido_actual:
        messagebox.showwarning("Pedido vacío", "Agrega al menos un producto.")
        return

    items_pedido = {nombre: datos[0] for nombre, datos in pedido_actual.items()}
    faltantes = ingredientes_faltantes(items_pedido)
    if faltantes:
        mensaje = "No se puede enviar el pedido, faltan ingredientes:\n\n" + "\n".join(faltantes)
        messagebox.showwarning("Ingredientes insuficientes", mensaje)
        return


   


    necesarios = calcular_ingredientes_necesarios(items_pedido)
    for ingrediente, cantidad_necesaria in necesarios.items():
        ingredientes[ingrediente] -= cantidad_necesaria

    total = sum(cantidad * precio for cantidad, precio in pedido_actual.values())

    nuevo_pedido = {
        "atendido_por": usuario_actual,
        "cliente": cliente.strip(),
        "mesa": mesa.strip(),
        "items": dict(pedido_actual),
        "total": total,
        "listo": False,
    }
    pedidos.append(nuevo_pedido)

    messagebox.showinfo("Pedido enviado",
                         f"Pedido de {cliente} (mesa {mesa}) enviado a cocina.\nTotal: ${total:.2f}")
    cancelar_pedido()


def cancelar_pedido():
    pedido_actual.clear()
    entry_cliente.delete(0, tk.END)
    entry_mesa.delete(0, tk.END)
    entry_cantidad.delete(0, tk.END)
    actualizar_lista_pedido()



# Pantalla de cocina <3


def refrescar_lista_ingredientes():
    lista_ingredientes.delete(0, tk.END)
    for ingrediente, cantidad in ingredientes.items():
        texto = f"{ingrediente}: {cantidad}"
        if cantidad <= 0:
            texto += "  (SIN STOCK)"
        elif cantidad < 20:
            texto += "  ⚠️"
        lista_ingredientes.insert(tk.END, texto)


def actualizar_stock():
    seleccion = lista_ingredientes.curselection()
    if not seleccion:
        messagebox.showwarning("Selecciona un ingrediente", "Elige un ingrediente de la lista.")
        return

    nuevo_valor = entry_nuevo_stock.get()
    if not numero_no_negativo(nuevo_valor):
        messagebox.showwarning("Cantidad inválida", "Ingresa un número entero mayor o igual a 0.")
        return

    ingrediente = list(ingredientes.keys())[seleccion[0]]
    ingredientes[ingrediente] = int(nuevo_valor)

    entry_nuevo_stock.delete(0, tk.END)
    refrescar_lista_ingredientes()


def pedidos_pendientes():
    return [pedido for pedido in pedidos if not pedido["listo"]]


def refrescar_pedidos_cocina():
    lista_cocina.delete(0, tk.END)
    for pedido in pedidos_pendientes():
        lista_cocina.insert(tk.END, f"Mesa {pedido['mesa']} - {pedido['cliente']} - ${pedido['total']:.2f}")


def ver_detalle_pedido():
    seleccion = lista_cocina.curselection()
    if not seleccion:
        messagebox.showwarning("Selecciona un pedido", "Elige un pedido de la lista.")
        return

    pedido = pedidos_pendientes()[seleccion[0]]
    lineas = [f"Cliente: {pedido['cliente']}",f"Mesa: {pedido['mesa']}", f"Atendido por: {pedido['atendido_por']}","-" * 25,]
    for nombre, (cantidad, precio) in pedido["items"].items():
        lineas.append(f"{cantidad} x {nombre}")
    lineas.append("-" * 25)
    lineas.append(f"TOTAL: ${pedido['total']:.2f}")

    messagebox.showinfo("Detalle del pedido", "\n".join(lineas))


def marcar_pedido_listo():
    seleccion = lista_cocina.curselection()
    if not seleccion:
        messagebox.showwarning("Selecciona un pedido", "Elige un pedido de la lista.")
        return

    pedido = pedidos_pendientes()[seleccion[0]]
    pedido["listo"] = True
    refrescar_pedidos_cocina()


# ventanas

def abrir_registro():
    global ventana_registro, entry_nombre_registro, entry_usuario_registro
    global entry_clave_registro, entry_confirmar_registro, rol_var

    ventana_registro = tk.Toplevel(ventana)
    ventana_registro.title("Registro de trabajador")
    ventana_registro.configure(bg=COLOR_FONDO)
    ventana_registro.geometry("380x430")
    ventana_registro.resizable(False, False)

    tk.Label(ventana_registro, text="Registro de trabajador", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_VINO).pack(pady=15)

    tk.Label(ventana_registro, text="Nombre completo:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(anchor="w", padx=30)
    entry_nombre_registro = tk.Entry(ventana_registro, font=FUENTE_NORMAL, width=30)
    entry_nombre_registro.pack(padx=30, pady=(0, 10))

    tk.Label(ventana_registro, text="Usuario:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(anchor="w", padx=30)
    entry_usuario_registro = tk.Entry(ventana_registro, font=FUENTE_NORMAL, width=30)
    entry_usuario_registro.pack(padx=30, pady=(0, 10))

    tk.Label(ventana_registro, text="Rol:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(anchor="w", padx=30)
    rol_var = tk.StringVar(value="Recepcionista")
    frame_rol = tk.Frame(ventana_registro, bg=COLOR_FONDO)
    frame_rol.pack(anchor="w", padx=30, pady=(0, 10))
    tk.Radiobutton(frame_rol, text="Recepcionista", variable=rol_var, value="Recepcionista",
                    bg=COLOR_FONDO).pack(side="left", padx=(0, 15))
    tk.Radiobutton(frame_rol, text="Cocina", variable=rol_var, value="Cocina",
                    bg=COLOR_FONDO).pack(side="left")

    tk.Label(ventana_registro, text="Contraseña:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(anchor="w", padx=30)
    entry_clave_registro = tk.Entry(ventana_registro, font=FUENTE_NORMAL, width=30, show="*")
    entry_clave_registro.pack(padx=30, pady=(0, 10))

    tk.Label(ventana_registro, text="Confirmar contraseña:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(anchor="w", padx=30)
    entry_confirmar_registro = tk.Entry(ventana_registro, font=FUENTE_NORMAL, width=30, show="*")
    entry_confirmar_registro.pack(padx=30, pady=(0, 15))

    tk.Button(ventana_registro, text="Registrar", font=FUENTE_BOTON, bg=COLOR_VINO, fg=COLOR_BLANCO,
              command=registrar_usuario).pack(pady=5)


def pantalla_login():
    global frame_login, entry_usuario_login, entry_clave_login

    frame_login = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_login.pack(fill="both", expand=True)

    tk.Label(frame_login, text="☕ Cafetería Misha", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_VINO).pack(pady=40)

    tk.Label(frame_login, text="Usuario:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack()
    entry_usuario_login = tk.Entry(frame_login, font=FUENTE_NORMAL, width=30)
    entry_usuario_login.pack(pady=(0, 10))

    tk.Label(frame_login, text="Contraseña:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack()
    entry_clave_login = tk.Entry(frame_login, font=FUENTE_NORMAL, width=30, show="*")
    entry_clave_login.pack(pady=(0, 20))
    entry_clave_login.bind("<Return>", lambda evento: iniciar_sesion())

    tk.Button(frame_login, text="Ingresar", font=FUENTE_BOTON, bg=COLOR_VINO, fg=COLOR_BLANCO,
              width=20, command=iniciar_sesion).pack(pady=5)

    tk.Button(frame_login, text="Registrarse", font=FUENTE_NORMAL, bg=COLOR_FONDO, fg=COLOR_VINO,
              relief="flat", command=abrir_registro).pack()


def pantalla_pedidos():
    global frame_principal, lista_menu, entry_cantidad, lista_pedido, label_total
    global entry_cliente, entry_mesa

    frame_principal = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_principal.pack(fill="both", expand=True)

    frame_superior = tk.Frame(frame_principal, bg=COLOR_VINO)
    frame_superior.pack(fill="x")
    tk.Label(frame_superior, text=f"👤 {usuario_actual} (Recepción)", font=FUENTE_NORMAL,
             bg=COLOR_VINO, fg=COLOR_BLANCO).pack(side="left", padx=10, pady=8)
    tk.Button(frame_superior, text="Cerrar sesión", command=cerrar_sesion,
              bg=COLOR_VINO, fg=COLOR_BLANCO, relief="flat").pack(side="right", padx=10, pady=5)

    frame_cliente = tk.Frame(frame_principal, bg=COLOR_FONDO, pady=10)
    frame_cliente.pack()
    tk.Label(frame_cliente, text="Cliente:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(side="left")
    entry_cliente = tk.Entry(frame_cliente, font=FUENTE_NORMAL, width=20)
    entry_cliente.pack(side="left", padx=(5, 20))
    tk.Label(frame_cliente, text="Mesa:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(side="left")
    entry_mesa = tk.Entry(frame_cliente, font=FUENTE_NORMAL, width=5)
    entry_mesa.pack(side="left", padx=5)

    frame_cuerpo = tk.Frame(frame_principal, bg=COLOR_FONDO)
    frame_cuerpo.pack(fill="both", expand=True, padx=20)

    frame_menu = tk.Frame(frame_cuerpo, bg=COLOR_FONDO)
    frame_menu.pack(side="left", fill="both", expand=True, padx=(0, 10))
    tk.Label(frame_menu, text="MENÚ", font=FUENTE_BOTON, bg=COLOR_FONDO, fg=COLOR_VINO).pack(anchor="w")
    lista_menu = tk.Listbox(frame_menu, font=FUENTE_NORMAL, height=14)
    lista_menu.pack(fill="both", expand=True)
    for nombre_producto, precio in MENU.items():
        lista_menu.insert(tk.END, f"{nombre_producto} - ${precio:.2f}")

    frame_agregar = tk.Frame(frame_menu, bg=COLOR_FONDO, pady=8)
    frame_agregar.pack(fill="x")
    tk.Label(frame_agregar, text="Cantidad:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(side="left")
    entry_cantidad = tk.Entry(frame_agregar, font=FUENTE_NORMAL, width=5)
    entry_cantidad.pack(side="left", padx=5)
    tk.Button(frame_agregar, text="Agregar ➜", font=FUENTE_BOTON, bg=COLOR_VINO, fg=COLOR_BLANCO,
              command=agregar_producto).pack(side="left", padx=5)

    frame_pedido = tk.Frame(frame_cuerpo, bg=COLOR_FONDO)
    frame_pedido.pack(side="left", fill="both", expand=True, padx=(10, 0))
    tk.Label(frame_pedido, text="PEDIDO ACTUAL", font=FUENTE_BOTON, bg=COLOR_FONDO, fg=COLOR_VINO).pack(anchor="w")
    lista_pedido = tk.Listbox(frame_pedido, font=FUENTE_NORMAL, height=14)
    lista_pedido.pack(fill="both", expand=True)
    tk.Button(frame_pedido, text="Quitar producto", font=FUENTE_NORMAL, bg=COLOR_NEGRO, fg=COLOR_BLANCO,
              command=quitar_producto).pack(fill="x", pady=(8, 0))

    frame_footer = tk.Frame(frame_principal, bg=COLOR_VINO, pady=10)
    frame_footer.pack(fill="x", side="bottom")
    label_total = tk.Label(frame_footer, text="TOTAL: $0.00", font=FUENTE_TITULO,
                            bg=COLOR_VINO, fg=COLOR_BLANCO)
    label_total.pack(pady=5)

    frame_botones = tk.Frame(frame_footer, bg=COLOR_VINO)
    frame_botones.pack()
    tk.Button(frame_botones, text="Finalizar pedido", font=FUENTE_BOTON, bg=COLOR_FONDO, fg=COLOR_VINO,
              command=finalizar_pedido).pack(side="left", padx=10)
    tk.Button(frame_botones, text="Cancelar pedido", font=FUENTE_BOTON, bg=COLOR_NEGRO, fg=COLOR_BLANCO,
              command=cancelar_pedido).pack(side="left", padx=10)


def pantalla_cocina():
    global frame_principal, lista_cocina, lista_ingredientes, entry_nuevo_stock

    frame_principal = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_principal.pack(fill="both", expand=True)

    frame_superior = tk.Frame(frame_principal, bg=COLOR_VINO)
    frame_superior.pack(fill="x")
    tk.Label(frame_superior, text=f"👨‍🍳 {usuario_actual} (Cocina)", font=FUENTE_NORMAL,
             bg=COLOR_VINO, fg=COLOR_BLANCO).pack(side="left", padx=10, pady=8)
    tk.Button(frame_superior, text="Cerrar sesión", command=cerrar_sesion,
              bg=COLOR_VINO, fg=COLOR_BLANCO, relief="flat").pack(side="right", padx=10, pady=5)

    frame_cuerpo = tk.Frame(frame_principal, bg=COLOR_FONDO)
    frame_cuerpo.pack(fill="both", expand=True, padx=20, pady=15)

                                                                       #  Columna izquierda: inventario de ingredientes 

    frame_inventario = tk.Frame(frame_cuerpo, bg=COLOR_FONDO)
    frame_inventario.pack(side="left", fill="both", expand=True, padx=(0, 10))

    tk.Label(frame_inventario, text="🧂 INVENTARIO", font=FUENTE_BOTON,
             bg=COLOR_FONDO, fg=COLOR_VINO).pack(anchor="w")

    lista_ingredientes = tk.Listbox(frame_inventario, font=FUENTE_NORMAL, height=14)
    lista_ingredientes.pack(fill="both", expand=True)

    frame_stock = tk.Frame(frame_inventario, bg=COLOR_FONDO, pady=8)
    frame_stock.pack(fill="x")
    tk.Label(frame_stock, text="Nuevo stock:", font=FUENTE_NORMAL, bg=COLOR_FONDO).pack(side="left")
    entry_nuevo_stock = tk.Entry(frame_stock, font=FUENTE_NORMAL, width=8)
    entry_nuevo_stock.pack(side="left", padx=5)
    tk.Button(frame_stock, text="Actualizar", font=FUENTE_BOTON, bg=COLOR_VINO, fg=COLOR_BLANCO,
              command=actualizar_stock).pack(side="left", padx=5)

                                                                        # Columna derecha: pedidos que manda el recepcionista 
    frame_pedidos = tk.Frame(frame_cuerpo, bg=COLOR_FONDO)
    frame_pedidos.pack(side="left", fill="both", expand=True, padx=(10, 0))

    tk.Label(frame_pedidos, text="🧾 PEDIDOS PENDIENTES", font=FUENTE_BOTON,
             bg=COLOR_FONDO, fg=COLOR_VINO).pack(anchor="w")

    lista_cocina = tk.Listbox(frame_pedidos, font=FUENTE_NORMAL, height=14)
    lista_cocina.pack(fill="both", expand=True)

    frame_botones = tk.Frame(frame_pedidos, bg=COLOR_FONDO, pady=8)
    frame_botones.pack(fill="x")
    tk.Button(frame_botones, text="Ver detalle", font=FUENTE_BOTON, bg=COLOR_NEGRO, fg=COLOR_BLANCO,
              command=ver_detalle_pedido).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Marcar listo", font=FUENTE_BOTON, bg=COLOR_VINO, fg=COLOR_BLANCO,
              command=marcar_pedido_listo).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Actualizar", font=FUENTE_NORMAL, bg=COLOR_FONDO, fg=COLOR_VINO,
              command=refrescar_pedidos_cocina).pack(side="left", padx=5)

    refrescar_lista_ingredientes()
    refrescar_pedidos_cocina()



# fin señores


ventana = tk.Tk()
ventana.title("Cafetería Misha")
ventana.geometry("850x600")
ventana.configure(bg=COLOR_FONDO)

pantalla_login()

ventana.mainloop()