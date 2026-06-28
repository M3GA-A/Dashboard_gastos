#modulo de python que proporciona clases para manipular fechas y horas, como date y datetime.
from datetime import date, datetime
#modulo de python que proporciona clases para crear interfaces gráficas de usuario, como messagebox y ttk.
from tkinter import messagebox, ttk


import customtkinter as ctk
#database.py es el archivo que contiene las funciones para interactuar con la base de datos, como crear tablas, insertar, 
#actualizar y eliminar gastos, así como obtener el resumen de gastos y el presupuesto.
import database as db


CATEGORIAS = [
    "Alimentacion",
    "Transporte",
    "Vivienda",
    "Salud",
    "Ocio",
    "Educacion",
    "Compras",
    "Otros",
]

#tema de la aplicacion, se puede cambiar a "light" para modo claro o "dark" para modo oscuro.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

#class Dashboard es la clase principal de la aplicacion, 
#que hereda de ctk.CTk y contiene todos los metodos para crear la interfaz de usuario, manejar eventos y actualizar la pantalla.
class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard de gastos")
        self.geometry("950x650")
        self.minsize(800, 550)
        self.gasto_seleccionado = None

        db.crear_tablas()
        db.cargar_ejemplos()
        self.crear_interfaz()
        self.actualizar_pantalla()
        
#crear_interfaz es el metodo que crea la interfaz de usuario, incluyendo el encabezado, el resumen de gastos, 
#el formulario para agregar gastos y la tabla para mostrar los gastos.
    def crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="#24352F",
            border_width=1,
            border_color="#3E5C50",
        )
        encabezado.grid(row=0, column=0, padx=25, pady=(20, 8), sticky="ew")

        ctk.CTkLabel(
            encabezado,
            text="Control de gastos",
            text_color="#E5F2EC",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(pady=13)

        self.crear_resumen()
        self.crear_formulario()
        self.crear_tabla()

#crear_resumen es el metodo que crea el resumen de gastos, mostrando el total gastado este mes, el presupuesto y el disponible. 
#Cada uno de estos valores se muestra en una tarjeta con un color diferente.
    def crear_resumen(self):
        marco = ctk.CTkFrame(self)
        marco.grid(row=1, column=0, padx=25, pady=10, sticky="ew")
        marco.grid_columnconfigure((0, 1, 2), weight=1)

        self.lbl_total = self.crear_tarjeta(
            marco, "Gastado este mes", 0, "#0F766E"
        )
        self.lbl_presupuesto = self.crear_tarjeta(
            marco, "Presupuesto", 1, "#55407A"
        )
        self.lbl_disponible = self.crear_tarjeta(
            marco, "Disponible", 2, "#35664A"
        )

#crear_tarjeta es el metodo que crea una tarjeta con un titulo y un valor, y la coloca en la columna especificada del marco padre. 
# El color de fondo de la tarjeta se puede personalizar.
    def crear_tarjeta(self, padre, titulo, columna, color):
        tarjeta = ctk.CTkFrame(padre, fg_color=color)
        tarjeta.grid(row=0, column=columna, padx=8, pady=10, sticky="ew")
        ctk.CTkLabel(tarjeta, text=titulo, text_color="#E8FFF8").pack(
            pady=(12, 2)
        )
        valor = ctk.CTkLabel(
            tarjeta,
            text="0,00 EUR",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        valor.pack(pady=(2, 12))
        return valor

#crear_formulario es el metodo que crea el formulario para agregar o actualizar gastos, 
#incluyendo campos para la descripcion, importe, categoria y fecha. Tambien incluye botones para guardar, limpiar, eliminar y pedir presupuesto.
    def crear_formulario(self):
        marco = ctk.CTkFrame(self)
        marco.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        marco.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.descripcion = ctk.CTkEntry(marco, placeholder_text="Descripcion")
        self.descripcion.grid(row=0, column=0, padx=8, pady=12, sticky="ew")

        self.importe = ctk.CTkEntry(marco, placeholder_text="Importe")
        self.importe.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        self.categoria = ctk.CTkComboBox(
            marco, values=CATEGORIAS, state="readonly"
        )
        self.categoria.set("Otros")
        self.categoria.grid(row=0, column=2, padx=8, pady=12, sticky="ew")

        self.fecha = ctk.CTkEntry(marco, placeholder_text="AAAA-MM-DD")
        self.fecha.insert(0, date.today().isoformat())
        self.fecha.grid(row=0, column=3, padx=8, pady=12, sticky="ew")

        self.btn_guardar = ctk.CTkButton(
            marco, text="Agregar", command=self.guardar
        )
        self.btn_guardar.grid(row=1, column=0, padx=8, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            marco, text="Limpiar", fg_color="#555555", command=self.limpiar_formulario
        ).grid(row=1, column=1, padx=8, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            marco, text="Eliminar", fg_color="#B23A48", command=self.eliminar
        ).grid(row=1, column=2, padx=8, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            marco, text="Presupuesto", command=self.pedir_presupuesto
        ).grid(row=1, column=3, padx=8, pady=(0, 12), sticky="ew")

#crear_tabla es el metodo que crea la tabla para mostrar los gastos, incluyendo un campo de busqueda para filtrar los resultados. 
#La tabla tiene columnas para la descripcion, importe, categoria y fecha, y permite seleccionar un gasto para actualizarlo o eliminarlo.
    def crear_tabla(self):
        zona = ctk.CTkFrame(self)
        zona.grid(row=3, column=0, padx=25, pady=(5, 20), sticky="nsew")
        zona.grid_columnconfigure(0, weight=1)
        zona.grid_rowconfigure(1, weight=1)

        self.buscar = ctk.CTkEntry(zona, placeholder_text="Buscar gasto...")
        self.buscar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.buscar.bind("<KeyRelease>", lambda _evento: self.cargar_tabla())

        columnas = ("descripcion", "importe", "categoria", "fecha")
        self.tabla = ttk.Treeview(zona, columns=columnas, show="headings")
        self.tabla.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_seleccion)

        titulos = {
            "descripcion": "Descripcion",
            "importe": "Importe",
            "categoria": "Categoria",
            "fecha": "Fecha",
        }
        for columna in columnas:
            self.tabla.heading(columna, text=titulos[columna])
        self.tabla.column("descripcion", width=280)
        self.tabla.column("importe", width=100, anchor="center")
        self.tabla.column("categoria", width=140, anchor="center")
        self.tabla.column("fecha", width=110, anchor="center")

#leer_formulario es el metodo que lee los datos del formulario, valida que sean correctos y devuelve una tupla con la descripcion, importe, categoria y fecha. 
#Si algun dato no es valido, muestra un mensaje de advertencia y devuelve None.
    def leer_formulario(self):
        descripcion = self.descripcion.get().strip()
        categoria = self.categoria.get()
        fecha = self.fecha.get().strip()

        if not descripcion:
            messagebox.showwarning("Validacion", "La descripcion es obligatoria.")
            return None
        try:
            importe = round(float(self.importe.get().replace(",", ".")), 2)
            if importe <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validacion", "El importe debe ser mayor que cero.")
            return None
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validacion", "La fecha debe ser AAAA-MM-DD.")
            return None

        return descripcion, importe, categoria, fecha

#guardar es el metodo que guarda un gasto en la base de datos. 
#Si hay un gasto seleccionado, lo actualiza; si no, lo inserta como un nuevo gasto. Luego limpia el formulario y actualiza la pantalla.
    def guardar(self):
        datos = self.leer_formulario()
        if not datos:
            return

        if self.gasto_seleccionado:
            db.actualizar_gasto(self.gasto_seleccionado, *datos)
        else:
            db.insertar_gasto(*datos)

        self.limpiar_formulario()
        self.actualizar_pantalla()

#eliminar es el metodo que elimina un gasto seleccionado de la base de datos. Si no hay un gasto seleccionado, muestra un mensaje de advertencia. 
# Si hay uno, pide confirmacion antes de eliminarlo. Luego limpia el formulario y actualiza la pantalla.
    def eliminar(self):
        if not self.gasto_seleccionado:
            messagebox.showwarning("Eliminar", "Selecciona un gasto de la tabla.")
            return
        if messagebox.askyesno("Eliminar", "Seguro que quieres eliminarlo?"):
            db.eliminar_gasto(self.gasto_seleccionado)
            self.limpiar_formulario()
            self.actualizar_pantalla()

#cargar_seleccion es el metodo que carga los datos de un gasto seleccionado en la tabla al formulario, para poder actualizarlo. Si no hay un gasto seleccionado, no hace nada.
    def cargar_seleccion(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        self.gasto_seleccionado = int(seleccion[0])
        descripcion, importe, categoria, fecha = self.tabla.item(
            seleccion[0], "values"
        )
        self.poner_texto(self.descripcion, descripcion)
        self.poner_texto(self.importe, importe)
        self.categoria.set(categoria)
        self.poner_texto(self.fecha, fecha)
        self.btn_guardar.configure(text="Actualizar")

#limpiar_formulario es el metodo que limpia los campos del formulario y resetea el estado de la aplicacion, para poder agregar un nuevo gasto. 
#Tambien deselecciona cualquier gasto seleccionado en la tabla.
    def limpiar_formulario(self):
        self.gasto_seleccionado = None
        self.poner_texto(self.descripcion, "")
        self.poner_texto(self.importe, "")
        self.categoria.set("Otros")
        self.poner_texto(self.fecha, date.today().isoformat())
        self.btn_guardar.configure(text="Agregar")
        self.tabla.selection_remove(self.tabla.selection())

#static method sirve para poder usar la funcion sin necesidad de instanciar la clase, es decir, se puede llamar directamente desde la clase sin crear un objeto de la misma.
    @staticmethod
    def poner_texto(entrada, texto):
        entrada.delete(0, "end")
        entrada.insert(0, texto)

#cargar_tabla es el metodo que carga los gastos de la base de datos en la tabla, filtrando por el texto de busqueda. 
#Primero borra todas las filas de la tabla, luego obtiene los gastos que coinciden con la busqueda y los inserta en la tabla con sus valores correspondientes.
    def cargar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        for gasto in db.listar_gastos(self.buscar.get()):
            self.tabla.insert(
                "",
                "end",
                iid=gasto["id"],
                values=(
                    gasto["descripcion"],
                    f"{gasto['importe']:.2f}",
                    gasto["categoria"],
                    gasto["fecha"],
                ),
            )

#pedir_presupuesto es el metodo que pide al usuario que introduzca un presupuesto mensual en euros, mediante un cuadro de dialogo.
#Si el usuario introduce un valor valido, lo guarda en la base de datos y actualiza
    def pedir_presupuesto(self):
        ventana = ctk.CTkInputDialog(
            title="Presupuesto mensual",
            text="Escribe el presupuesto en EUR:",
        )
        texto = ventana.get_input()
        if texto is None:
            return
        try:
            importe = round(float(texto.replace(",", ".")), 2)
            if importe <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validacion", "Introduce un importe mayor que cero.")
            return
        db.guardar_presupuesto(importe)
        self.actualizar_resumen()

#actualizar_resumen es el metodo que actualiza los valores del resumen de gastos, mostrando el total gastado este mes, el presupuesto y el disponible.
#Calcula el disponible restando el total del presupuesto.
    def actualizar_resumen(self):
        mes = date.today().strftime("%Y-%m")
        total, _cantidad = db.obtener_resumen(mes)
        presupuesto = db.obtener_presupuesto()
        disponible = presupuesto - total

        self.lbl_total.configure(text=f"{total:.2f} EUR")
        self.lbl_presupuesto.configure(text=f"{presupuesto:.2f} EUR")
        self.lbl_disponible.configure(
            text=f"{disponible:.2f} EUR",
            text_color="#FF6B6B" if disponible < 0 else "#FFFFFF",
        )

#actualizar_pantalla es el metodo que actualiza toda la pantalla, cargando la tabla y el resumen de gastos.
    def actualizar_pantalla(self):
        self.cargar_tabla()
        self.actualizar_resumen()


if __name__ == "__main__":
    Dashboard().mainloop()
