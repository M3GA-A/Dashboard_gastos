"""Interfaz principal del gestor de gastos.

La aplicación usa SQLite mediante ``database.py``. La navegación y la
distribución visual están inspiradas en Dashboard_gastos y emplean una paleta
oscura con acentos violetas.
"""

import tkinter as tk
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

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

# Paleta moderna de alto contraste: negro, grafito, violeta y pequeños
# acentos brillantes para los gráficos. Todas las pantallas la comparten.
COLOR_FONDO = "#070809"
COLOR_SIDEBAR = "#181818"
COLOR_TARJETA = "#222124"
COLOR_TARJETA_ALT = "#302A35"
COLOR_BORDE = "#4B3A52"
COLOR_PRIMARIO = "#9D2DBD"
COLOR_PRIMARIO_HOVER = "#B83ADA"
COLOR_ACENTO = "#C026D3"
COLOR_ACENTO_HOVER = "#D946EF"
COLOR_PRESUPUESTO = "#74409A"
COLOR_DISPONIBLE = "#22C7B8"
COLOR_PELIGRO = "#E5485D"
COLOR_PELIGRO_HOVER = "#F05A6D"
COLOR_TEXTO = "#F5F3F7"
COLOR_TEXTO_SECUNDARIO = "#A8A3AC"

CATEGORIA_COLORES = {
    "Alimentacion": "#8B3BB0",
    "Alimentación": "#8B3BB0",
    "Transporte": "#DD27D5",
    "Vivienda": "#55257D",
    "Salud": "#EC4899",
    "Ocio": "#A855F7",
    "Educacion": "#7C3AED",
    "Educación": "#7C3AED",
    "Compras": "#C026D3",
    "Otros": "#22D3C5",
}

NOMBRES_MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def formatear_importe(importe):
    """Devuelve un importe con formato español."""
    return f"{importe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def fecha_valida(texto):
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def como_diccionario(fila):
    """Convierte una sqlite3.Row en un diccionario normal para la interfaz."""
    return dict(fila)


def formatear_mes(mes):
    """Convierte 2026-07 en Julio 2026."""
    anio, numero_mes = (int(parte) for parte in mes.split("-"))
    return f"{NOMBRES_MESES[numero_mes - 1]} {anio}"


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control de gastos")
        self.geometry("1180x760")
        self.minsize(950, 620)
        self.configure(fg_color=COLOR_FONDO)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        db.crear_tablas()
        db.cargar_ejemplos()
        self.mes_seleccionado = self.obtener_mes_inicial()
        self.seccion_actual = "dashboard"

        self.sidebar = ctk.CTkFrame(
            self, width=210, corner_radius=0, fg_color=COLOR_SIDEBAR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)

        ctk.CTkLabel(
            self.sidebar,
            text="Mis gastos",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=25, weight="bold"),
        ).pack(padx=20, pady=(35, 8))
        ctk.CTkLabel(
            self.sidebar, text="Control personal", text_color=COLOR_PRIMARIO
        ).pack(pady=(0, 28))

        self.botones_menu = {}
        opciones = [
            ("dashboard", "📊  Dashboard", self.mostrar_dashboard),
            ("agregar", "➕  Agregar gasto", self.mostrar_agregar),
            ("presupuesto", "💰  Presupuesto", self.mostrar_presupuesto),
            ("buscar", "🔍  Buscar gastos", self.mostrar_buscar),
        ]
        for clave, texto, comando in opciones:
            boton = ctk.CTkButton(
                self.sidebar,
                text=texto,
                height=44,
                anchor="w",
                fg_color=COLOR_TARJETA_ALT,
                hover_color=COLOR_PRIMARIO_HOVER,
                border_width=1,
                border_color=COLOR_BORDE,
                text_color=COLOR_TEXTO,
                command=comando,
            )
            boton.pack(fill="x", padx=18, pady=6)
            self.botones_menu[clave] = boton

        selector_anio = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        selector_anio.pack(side="bottom", fill="x", padx=18, pady=24)
        ctk.CTkLabel(
            selector_anio,
            text="Cambiar de año",
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", pady=(0, 7))
        self.entrada_anio = ctk.CTkComboBox(
            selector_anio,
            values=[str(anio) for anio in range(2026, 2032)],
            height=36,
            state="readonly",
            fg_color=COLOR_TARJETA_ALT,
            border_color=COLOR_BORDE,
            button_color=COLOR_PRIMARIO,
            button_hover_color=COLOR_PRIMARIO_HOVER,
            dropdown_fg_color=COLOR_TARJETA,
            dropdown_hover_color=COLOR_PRIMARIO_HOVER,
            command=self.cambiar_anio,
        )
        self.entrada_anio.set(self.mes_seleccionado[:4])
        self.entrada_anio.pack(fill="x")
        self.mostrar_dashboard()

    def activar_menu(self, clave):
        self.seccion_actual = clave
        for nombre, boton in self.botones_menu.items():
            boton.configure(
                fg_color=COLOR_PRIMARIO if nombre == clave else COLOR_TARJETA_ALT
            )

    def limpiar_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def crear_titulo(self, titulo, subtitulo, padre=None):
        padre = padre or self.content
        ctk.CTkLabel(
            padre,
            text=titulo,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            padre, text=subtitulo, text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(4, 22))

    def gastos(self, busqueda=""):
        return [como_diccionario(fila) for fila in db.listar_gastos(busqueda)]

    def meses_disponibles(self):
        """Devuelve los doce meses del año seleccionado."""
        anio = int(self.mes_seleccionado[:4])
        return [
            f"{anio:04d}-{numero_mes:02d}"
            for numero_mes in range(12, 0, -1)
        ]

    def obtener_mes_inicial(self):
        """Usa el mes actual o, si está vacío, el último mes con movimientos."""
        mes_actual = date.today().strftime("%Y-%m")
        meses_con_gastos = sorted(
            {
                gasto["fecha"][:7]
                for gasto in self.gastos()
                if fecha_valida(gasto["fecha"])
            },
            reverse=True,
        )
        return mes_actual if mes_actual in meses_con_gastos else (
            meses_con_gastos[0] if meses_con_gastos else mes_actual
        )

    def crear_selector_mes(self, padre, comando):
        meses = self.meses_disponibles()
        meses_por_etiqueta = {formatear_mes(mes): mes for mes in meses}
        selector = ctk.CTkFrame(padre, fg_color="transparent")
        selector.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            selector,
            text="Mes analizado",
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left")
        combo = ctk.CTkComboBox(
            selector,
            values=list(meses_por_etiqueta),
            width=165,
            state="readonly",
            fg_color=COLOR_TARJETA_ALT,
            border_color=COLOR_BORDE,
            button_color=COLOR_PRIMARIO,
            button_hover_color=COLOR_PRIMARIO_HOVER,
            dropdown_fg_color=COLOR_TARJETA,
            dropdown_hover_color=COLOR_PRIMARIO_HOVER,
            command=lambda etiqueta: comando(meses_por_etiqueta[etiqueta]),
        )
        combo.set(formatear_mes(self.mes_seleccionado))
        combo.pack(side="left", padx=(10, 0))

    def cambiar_mes_dashboard(self, mes):
        self.mes_seleccionado = mes
        self.mostrar_dashboard()

    def cambiar_mes_presupuesto(self, mes):
        self.mes_seleccionado = mes
        self.mostrar_presupuesto()

    def cambiar_mes_busqueda(self, mes):
        self.mes_seleccionado = mes
        self.mostrar_buscar()

    def cambiar_anio(self, anio):
        """Cambia de año sin perder el mes ni la sección que está abierta."""
        numero_mes = self.mes_seleccionado[5:7]
        self.mes_seleccionado = f"{int(anio):04d}-{numero_mes}"
        acciones = {
            "dashboard": self.mostrar_dashboard,
            "agregar": self.mostrar_agregar,
            "presupuesto": self.mostrar_presupuesto,
            "buscar": self.mostrar_buscar,
        }
        acciones.get(self.seccion_actual, self.mostrar_dashboard)()

    def gastos_del_mes(self, busqueda=""):
        return [
            gasto
            for gasto in self.gastos(busqueda)
            if gasto["fecha"].startswith(self.mes_seleccionado)
        ]

    def mostrar_dashboard(self):
        self.activar_menu("dashboard")
        self.limpiar_content()
        panel = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COLOR_PRIMARIO,
            scrollbar_button_hover_color=COLOR_PRIMARIO_HOVER,
        )
        panel.pack(expand=True, fill="both")
        self.crear_titulo("Dashboard", "Resumen de tus gastos personales", panel)
        self.crear_selector_mes(panel, self.cambiar_mes_dashboard)

        gastos_mes = self.gastos_del_mes()
        total_mes = sum(gasto["importe"] for gasto in gastos_mes)
        presupuesto = db.obtener_presupuesto()
        disponible = presupuesto - total_mes

        tarjetas = ctk.CTkFrame(panel, fg_color="transparent")
        tarjetas.pack(fill="x")
        for columna in range(4):
            tarjetas.grid_columnconfigure(columna, weight=1)

        resumen = [
            ("Total del mes", formatear_importe(total_mes), COLOR_ACENTO),
            ("Presupuesto", formatear_importe(presupuesto), COLOR_PRESUPUESTO),
            ("Disponible", formatear_importe(disponible), COLOR_DISPONIBLE),
            ("Categoría principal", self.obtener_categoria_principal(gastos_mes), COLOR_PRIMARIO),
        ]
        for columna, (titulo, valor, color) in enumerate(resumen):
            tarjeta = ctk.CTkFrame(
                tarjetas, fg_color=COLOR_TARJETA, border_width=1, border_color=color
            )
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=(0 if columna == 0 else 6, 0 if columna == 3 else 6),
            )
            ctk.CTkLabel(
                tarjeta, text=titulo, text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w", padx=16, pady=(15, 5))
            ctk.CTkLabel(
                tarjeta,
                text=valor,
                text_color=COLOR_TEXTO,
                font=ctk.CTkFont(size=20, weight="bold"),
                wraplength=150,
            ).pack(anchor="w", padx=16, pady=(0, 15))

        progreso = ctk.CTkFrame(
            panel, fg_color=COLOR_TARJETA, border_width=1, border_color=COLOR_BORDE
        )
        progreso.pack(fill="x", pady=(16, 0))
        porcentaje = total_mes / presupuesto if presupuesto > 0 else 0
        texto = (
            f"Has utilizado {porcentaje:.0%} de tu presupuesto mensual"
            if presupuesto > 0
            else "Define un presupuesto mensual desde el menú"
        )
        ctk.CTkLabel(
            progreso,
            text=texto,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(14, 8))
        barra = ctk.CTkProgressBar(
            progreso,
            height=12,
            fg_color=COLOR_TARJETA_ALT,
            progress_color=COLOR_PRIMARIO if porcentaje <= 1 else COLOR_PELIGRO,
        )
        barra.pack(fill="x", padx=18, pady=(0, 18))
        barra.set(min(max(porcentaje, 0), 1))

        graficos = ctk.CTkFrame(panel, fg_color="transparent")
        graficos.pack(fill="x", pady=(22, 0))
        graficos.grid_columnconfigure(0, weight=3)
        graficos.grid_columnconfigure(1, weight=2)

        actividad, lienzo_actividad = self.crear_panel_grafico(
            graficos, 0, "Actividad del mes", "Gastos acumulados por día"
        )
        actividad.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        categorias, lienzo_categorias = self.crear_panel_grafico(
            graficos, 1, "Gastos por categoría", "Distribución del mes actual"
        )
        categorias.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        lienzo_actividad.bind(
            "<Configure>", lambda _evento: self.dibujar_actividad(lienzo_actividad, gastos_mes)
        )
        lienzo_categorias.bind(
            "<Configure>", lambda _evento: self.dibujar_categorias(lienzo_categorias, gastos_mes)
        )

    def crear_panel_grafico(self, padre, _columna, titulo, subtitulo):
        marco = ctk.CTkFrame(
            padre,
            height=280,
            fg_color=COLOR_TARJETA,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        marco.grid_propagate(False)
        ctk.CTkLabel(
            marco,
            text=titulo,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 0))
        ctk.CTkLabel(
            marco, text=subtitulo, text_color=COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w", padx=18, pady=(2, 4))
        lienzo = tk.Canvas(marco, height=195, bg=COLOR_TARJETA, highlightthickness=0)
        lienzo.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        return marco, lienzo

    def dibujar_actividad(self, lienzo, datos):
        lienzo.delete("all")
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
        if ancho < 80 or alto < 80:
            return
        if not datos:
            lienzo.create_text(
                ancho / 2,
                alto / 2,
                text="Agrega gastos para ver la actividad",
                fill=COLOR_TEXTO_SECUNDARIO,
                font=("Arial", 12),
            )
            return

        anio, mes = (int(parte) for parte in self.mes_seleccionado.split("-"))
        dias_mes = monthrange(anio, mes)[1]
        totales = defaultdict(float)
        for gasto in datos:
            totales[datetime.strptime(gasto["fecha"], "%Y-%m-%d").day] += gasto["importe"]
        valores = [totales[dia] for dia in range(1, dias_mes + 1)]
        maximo = max(valores) or 1
        izquierda, derecha, superior, inferior = 42, 18, 18, 30
        area_ancho = ancho - izquierda - derecha
        area_alto = alto - superior - inferior

        for paso in range(4):
            y = superior + area_alto * paso / 3
            lienzo.create_line(izquierda, y, ancho - derecha, y, fill=COLOR_TARJETA_ALT)
            lienzo.create_text(
                izquierda - 7,
                y,
                text=f"{maximo * (3 - paso) / 3:.0f}€",
                fill=COLOR_TEXTO_SECUNDARIO,
                anchor="e",
                font=("Arial", 9),
            )

        puntos = []
        for indice, valor in enumerate(valores):
            x = izquierda + area_ancho * indice / max(dias_mes - 1, 1)
            y = superior + area_alto * (1 - valor / maximo)
            puntos.extend((x, y))
        area = [izquierda, superior + area_alto, *puntos, ancho - derecha, superior + area_alto]
        lienzo.create_polygon(area, fill=COLOR_BORDE, outline="", smooth=True)
        lienzo.create_line(puntos, fill=COLOR_PRIMARIO, width=3, smooth=True)

        for dia in [1, 8, 15, 22, dias_mes]:
            x = izquierda + area_ancho * (dia - 1) / max(dias_mes - 1, 1)
            lienzo.create_text(
                x, alto - 12, text=str(dia), fill=COLOR_TEXTO_SECUNDARIO, font=("Arial", 9)
            )

    def dibujar_categorias(self, lienzo, datos):
        lienzo.delete("all")
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
        if ancho < 80 or alto < 80:
            return
        totales = defaultdict(float)
        for gasto in datos:
            totales[gasto["categoria"]] += gasto["importe"]
        total = sum(totales.values())
        if total <= 0:
            lienzo.create_text(
                ancho / 2,
                alto / 2,
                text="Sin gastos este mes",
                fill=COLOR_TEXTO_SECUNDARIO,
                font=("Arial", 12),
            )
            return

        diametro = min(alto - 34, ancho * 0.42)
        x1, y1, inicio = 14, (alto - diametro) / 2, 90
        ordenados = sorted(totales.items(), key=lambda item: item[1], reverse=True)
        for categoria, importe in ordenados:
            extension = -(importe / total) * 360
            lienzo.create_arc(
                x1,
                y1,
                x1 + diametro,
                y1 + diametro,
                start=inicio,
                extent=extension,
                fill=CATEGORIA_COLORES.get(categoria, "#22D3C5"),
                outline=COLOR_TARJETA,
                width=2,
            )
            inicio += extension
        hueco = diametro * 0.56
        margen = (diametro - hueco) / 2
        lienzo.create_oval(
            x1 + margen,
            y1 + margen,
            x1 + margen + hueco,
            y1 + margen + hueco,
            fill=COLOR_TARJETA,
            outline="",
        )
        lienzo.create_text(
            x1 + diametro / 2,
            y1 + diametro / 2,
            text=formatear_importe(total),
            fill=COLOR_TEXTO,
            font=("Arial", 11, "bold"),
        )
        leyenda_x = x1 + diametro + 18
        for indice, (categoria, importe) in enumerate(ordenados[:5]):
            y = 24 + indice * 30
            color = CATEGORIA_COLORES.get(categoria, "#22D3C5")
            lienzo.create_oval(leyenda_x, y - 5, leyenda_x + 10, y + 5, fill=color, outline="")
            lienzo.create_text(
                leyenda_x + 17,
                y,
                text=categoria,
                fill=COLOR_TEXTO,
                anchor="w",
                font=("Arial", 10),
            )
            lienzo.create_text(
                ancho - 8,
                y,
                text=f"{importe / total:.0%}",
                fill=COLOR_TEXTO_SECUNDARIO,
                anchor="e",
                font=("Arial", 10),
            )

    @staticmethod
    def obtener_categoria_principal(datos):
        if not datos:
            return "Sin datos"
        totales = defaultdict(float)
        for gasto in datos:
            totales[gasto["categoria"]] += gasto["importe"]
        return max(totales, key=totales.get)

    def mostrar_agregar(self):
        self.activar_menu("agregar")
        self.mostrar_formulario(
            "Agregar gasto", "Registra un nuevo movimiento", "Guardar gasto", self.guardar_registro
        )

    def mostrar_formulario(self, titulo, subtitulo, texto_boton, comando, registro=None):
        self.limpiar_content()
        self.crear_titulo(titulo, subtitulo)
        formulario = ctk.CTkFrame(
            self.content, fg_color=COLOR_TARJETA, border_width=1, border_color=COLOR_BORDE
        )
        formulario.pack(fill="x")
        formulario.grid_columnconfigure((0, 1), weight=1)

        campos = [
            ("Descripción", 0, 0),
            ("Importe (€)", 0, 1),
            ("Categoría", 2, 0),
            ("Fecha (AAAA-MM-DD)", 2, 1),
        ]
        for texto, fila, columna in campos:
            ctk.CTkLabel(formulario, text=texto, text_color=COLOR_TEXTO).grid(
                row=fila, column=columna, sticky="w", padx=22, pady=(22 if fila == 0 else 4, 6)
            )

        self.entrada_descripcion = self.crear_entrada(
            formulario, "Ejemplo: Compra del supermercado", 1, 0
        )
        self.entrada_importe = self.crear_entrada(formulario, "Ejemplo: 24,50", 1, 1)
        self.entrada_categoria = ctk.CTkComboBox(
            formulario,
            values=CATEGORIAS,
            height=40,
            state="readonly",
            fg_color=COLOR_TARJETA_ALT,
            border_color=COLOR_BORDE,
            button_color=COLOR_PRIMARIO,
            button_hover_color=COLOR_PRIMARIO_HOVER,
            dropdown_fg_color=COLOR_TARJETA,
            dropdown_hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.entrada_categoria.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 24))
        self.entrada_categoria.set("Otros")
        self.entrada_fecha = self.crear_entrada(formulario, "AAAA-MM-DD", 3, 1, pady=(0, 24))
        self.entrada_fecha.insert(0, date.today().isoformat())

        if registro:
            self.poner_texto(self.entrada_descripcion, registro["descripcion"])
            self.poner_texto(self.entrada_importe, str(registro["importe"]))
            self.entrada_categoria.set(registro["categoria"])
            self.poner_texto(self.entrada_fecha, registro["fecha"])

        botones = ctk.CTkFrame(self.content, fg_color="transparent")
        botones.pack(anchor="e", pady=18)
        ctk.CTkButton(
            botones,
            text="Cancelar",
            width=110,
            fg_color=COLOR_TARJETA_ALT,
            hover_color=COLOR_ACENTO_HOVER,
            border_width=1,
            border_color=COLOR_ACENTO,
            command=self.mostrar_dashboard,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            botones,
            text=texto_boton,
            width=140,
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            command=comando,
        ).pack(side="left")

    def crear_entrada(self, padre, placeholder, fila, columna, pady=(0, 14)):
        entrada = ctk.CTkEntry(
            padre,
            placeholder_text=placeholder,
            height=40,
            fg_color=COLOR_TARJETA_ALT,
            border_color=COLOR_BORDE,
        )
        entrada.grid(row=fila, column=columna, sticky="ew", padx=22, pady=pady)
        return entrada

    @staticmethod
    def poner_texto(entrada, texto):
        entrada.delete(0, "end")
        entrada.insert(0, texto)

    def leer_formulario(self):
        descripcion = self.entrada_descripcion.get().strip()
        categoria = self.entrada_categoria.get()
        fecha = self.entrada_fecha.get().strip()
        if not descripcion:
            messagebox.showwarning("Dato obligatorio", "Escribe una descripción.")
            return None
        try:
            importe = round(float(self.entrada_importe.get().strip().replace(",", ".")), 2)
            if importe <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Importe incorrecto", "El importe debe ser mayor que cero.")
            return None
        if not fecha_valida(fecha):
            messagebox.showwarning("Fecha incorrecta", "Usa el formato AAAA-MM-DD.")
            return None
        return descripcion, importe, categoria, fecha

    def guardar_registro(self):
        datos = self.leer_formulario()
        if datos:
            db.insertar_gasto(*datos)
            self.mes_seleccionado = datos[3][:7]
            messagebox.showinfo("Gasto guardado", "El gasto se guardó correctamente.")
            self.mostrar_dashboard()

    def editar_registro(self, gasto_id):
        registro = next((gasto for gasto in self.gastos() if gasto["id"] == gasto_id), None)
        if registro is None:
            messagebox.showwarning("Gasto no encontrado", "El gasto ya no existe.")
            self.mostrar_buscar()
            return
        self.activar_menu("buscar")
        self.mostrar_formulario(
            "Editar gasto",
            "Actualiza los datos del movimiento",
            "Guardar cambios",
            lambda: self.actualizar_registro(gasto_id),
            registro,
        )

    def actualizar_registro(self, gasto_id):
        datos = self.leer_formulario()
        if datos:
            db.actualizar_gasto(gasto_id, *datos)
            self.mostrar_buscar()

    def eliminar_registro(self, gasto_id, descripcion):
        if messagebox.askyesno("Confirmar eliminación", f"¿Quieres eliminar «{descripcion}»?"):
            db.eliminar_gasto(gasto_id)
            self.mostrar_buscar()

    def mostrar_presupuesto(self):
        self.activar_menu("presupuesto")
        self.limpiar_content()
        self.crear_titulo(
            "Presupuesto mensual", "Define cuánto quieres gastar como máximo cada mes"
        )
        self.crear_selector_mes(self.content, self.cambiar_mes_presupuesto)
        presupuesto = db.obtener_presupuesto()
        total_mes = sum(gasto["importe"] for gasto in self.gastos_del_mes())
        disponible = presupuesto - total_mes

        resumen = ctk.CTkFrame(
            self.content, fg_color=COLOR_TARJETA, border_width=1, border_color=COLOR_BORDE
        )
        resumen.pack(fill="x", pady=(0, 18))
        resumen.grid_columnconfigure((0, 1, 2), weight=1)
        valores = [
            ("Presupuesto actual", presupuesto),
            ("Gastado este mes", total_mes),
            ("Disponible", disponible),
        ]
        for columna, (titulo, valor) in enumerate(valores):
            tarjeta = ctk.CTkFrame(
                resumen, fg_color=COLOR_TARJETA_ALT, border_width=1, border_color=COLOR_BORDE
            )
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=16, pady=16)
            ctk.CTkLabel(
                tarjeta, text=titulo, text_color=COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w", padx=14, pady=(12, 0))
            ctk.CTkLabel(
                tarjeta,
                text=formatear_importe(valor),
                text_color=COLOR_TEXTO,
                font=ctk.CTkFont(size=22, weight="bold"),
            ).pack(anchor="w", padx=14, pady=(5, 12))

        formulario = ctk.CTkFrame(
            self.content, fg_color=COLOR_TARJETA, border_width=1, border_color=COLOR_BORDE
        )
        formulario.pack(fill="x")
        ctk.CTkLabel(
            formulario,
            text="Nuevo presupuesto (€)",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(22, 8))
        self.entrada_presupuesto = ctk.CTkEntry(
            formulario,
            placeholder_text="Ejemplo: 800",
            height=42,
            fg_color=COLOR_TARJETA_ALT,
            border_color=COLOR_BORDE,
        )
        self.entrada_presupuesto.pack(fill="x", padx=22)
        if presupuesto > 0:
            self.entrada_presupuesto.insert(0, str(presupuesto))
        ctk.CTkButton(
            formulario,
            text="Guardar presupuesto",
            height=42,
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            command=self.guardar_presupuesto,
        ).pack(anchor="e", padx=22, pady=22)

    def guardar_presupuesto(self):
        try:
            presupuesto = round(float(self.entrada_presupuesto.get().replace(",", ".")), 2)
            if presupuesto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Presupuesto incorrecto", "Escribe un importe mayor que cero.")
            return
        db.guardar_presupuesto(presupuesto)
        messagebox.showinfo("Presupuesto guardado", "El presupuesto se guardó correctamente.")
        self.mostrar_presupuesto()

    def mostrar_buscar(self):
        self.activar_menu("buscar")
        self.limpiar_content()
        self.crear_titulo("Buscar gastos", "Filtra por descripción, categoría o fecha")
        self.crear_selector_mes(self.content, self.cambiar_mes_busqueda)
        buscador = ctk.CTkFrame(self.content, fg_color="transparent")
        buscador.pack(fill="x", pady=(0, 14))
        self.entrada_busqueda = ctk.CTkEntry(
            buscador,
            placeholder_text="Ejemplo: transporte, 2026-06 o supermercado",
            height=42,
            fg_color=COLOR_TARJETA,
            border_color=COLOR_BORDE,
        )
        self.entrada_busqueda.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entrada_busqueda.bind("<KeyRelease>", self.actualizar_busqueda)
        ctk.CTkButton(
            buscador,
            text="Limpiar",
            width=100,
            height=42,
            fg_color=COLOR_ACENTO,
            hover_color=COLOR_ACENTO_HOVER,
            command=self.limpiar_busqueda,
        ).pack(side="right")

        self.resultados_busqueda = ctk.CTkScrollableFrame(
            self.content,
            fg_color=COLOR_SIDEBAR,
            border_width=1,
            border_color=COLOR_BORDE,
            scrollbar_button_color=COLOR_PRIMARIO,
            scrollbar_button_hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.resultados_busqueda.pack(expand=True, fill="both")
        self.mostrar_resultados(self.gastos_del_mes())
        self.entrada_busqueda.focus()

    def actualizar_busqueda(self, _evento=None):
        self.mostrar_resultados(self.gastos_del_mes(self.entrada_busqueda.get()))

    def limpiar_busqueda(self):
        self.entrada_busqueda.delete(0, "end")
        self.mostrar_resultados(self.gastos_del_mes())

    def mostrar_resultados(self, datos):
        for widget in self.resultados_busqueda.winfo_children():
            widget.destroy()
        if not datos:
            ctk.CTkLabel(
                self.resultados_busqueda,
                text="No se encontraron gastos.",
                text_color=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=45)
            return
        for registro in datos:
            self.crear_fila_gasto(registro)

    def crear_fila_gasto(self, registro):
        fila = ctk.CTkFrame(
            self.resultados_busqueda,
            fg_color=COLOR_TARJETA,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        fila.pack(fill="x", padx=4, pady=5)
        informacion = ctk.CTkFrame(fila, fg_color="transparent")
        informacion.pack(side="left", expand=True, fill="x", padx=14, pady=10)
        ctk.CTkLabel(
            informacion,
            text=registro["descripcion"],
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            informacion,
            text=f"{registro['categoria']} · {registro['fecha']}",
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            fila,
            text=formatear_importe(registro["importe"]),
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=110,
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            fila,
            text="Eliminar",
            width=90,
            fg_color=COLOR_PELIGRO,
            hover_color=COLOR_PELIGRO_HOVER,
            command=lambda: self.eliminar_registro(registro["id"], registro["descripcion"]),
        ).pack(side="right", padx=(0, 8))
        ctk.CTkButton(
            fila,
            text="Editar",
            width=90,
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            command=lambda: self.editar_registro(registro["id"]),
        ).pack(side="right", padx=(0, 8))


if __name__ == "__main__":
    Dashboard().mainloop()
