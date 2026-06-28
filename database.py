import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("gastos.db")

#conectarse a la base de datos
def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion

#crear_tablas() crea las tablas necesarias en la base de datos si no existen
def crear_tablas():
    with conectar() as conexion:
        conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                importe REAL NOT NULL CHECK (importe > 0),
                categoria TEXT NOT NULL,
                fecha TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
            """
        )

#listar_gastos() devuelve una lista de gastos que coinciden con la búsqueda proporcionada
def listar_gastos(busqueda=""):
    texto = f"%{busqueda.strip()}%"
    with conectar() as conexion:
        return conexion.execute(
            """
            SELECT * FROM gastos
            WHERE descripcion LIKE ?
               OR categoria LIKE ?
               OR fecha LIKE ?
            ORDER BY fecha DESC, id DESC
            """,
            (texto, texto, texto),
        ).fetchall()

#insertar_gasto() inserta un nuevo gasto en la base de datos
def insertar_gasto(descripcion, importe, categoria, fecha):
    with conectar() as conexion:
        conexion.execute(
            """
            INSERT INTO gastos (descripcion, importe, categoria, fecha)
            VALUES (?, ?, ?, ?)
            """,
            (descripcion, importe, categoria, fecha),
        )

#actualizar_gasto() actualiza un gasto existente en la base de datos
def actualizar_gasto(gasto_id, descripcion, importe, categoria, fecha):
    with conectar() as conexion:
        conexion.execute(
            """
            UPDATE gastos
            SET descripcion = ?, importe = ?, categoria = ?, fecha = ?
            WHERE id = ?
            """,
            (descripcion, importe, categoria, fecha, gasto_id),
        )

#eliminar_gasto() elimina un gasto de la base de datos según su ID
def eliminar_gasto(gasto_id):
    with conectar() as conexion:
        conexion.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))

#obtener_resumen() devuelve el total y la cantidad de gastos para un mes específico
def obtener_resumen(mes):
    with conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT COALESCE(SUM(importe), 0) AS total, COUNT(*) AS cantidad
            FROM gastos
            WHERE substr(fecha, 1, 7) = ?
            """,
            (mes,),
        ).fetchone()
    return float(fila["total"]), fila["cantidad"]

#obtener_presupuesto() devuelve el valor del presupuesto almacenado en la base de datos
def obtener_presupuesto():
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT valor FROM configuracion WHERE clave = 'presupuesto'"
        ).fetchone()
    return float(fila["valor"]) if fila else 0.0

#guardar_presupuesto() guarda o actualiza el valor del presupuesto en la base de datos
def guardar_presupuesto(importe):
    with conectar() as conexion:
        conexion.execute(
            """
            INSERT INTO configuracion (clave, valor)
            VALUES ('presupuesto', ?)
            ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor
            """,
            (importe,),
        )

#cargar_ejemplos() inserta ejemplos de gastos en la base de datos si no se han insertado previamente
def cargar_ejemplos():
    ejemplos = [
        ("Supermercado", 9.10, "Alimentacion", "2026-06-09"),
        ("Carga T-mobilitat", 40.00, "Transporte", "2026-06-02"),
        ("Restaurante", 27.70, "Ocio", "2026-06-07"),
        ("Alquiler", 350.00, "Vivienda", "2026-06-01"),
        ("Seguro medico", 30.00, "Salud", "2026-06-03"),
        ("Libros", 15.00, "Educacion", "2026-06-06"),
        ("Indumentaria", 68.50, "Compras", "2026-06-08"),
        ("Arreglo caldera", 100.00, "Otros", "2026-06-06"),
    ]
    with conectar() as conexion:
        inicializado = conexion.execute(
            "SELECT 1 FROM configuracion WHERE clave = 'datos_iniciales'"
        ).fetchone()
        if not inicializado:
            conexion.executemany(
                """
                INSERT INTO gastos (descripcion, importe, categoria, fecha)
                VALUES (?, ?, ?, ?)
                """,
                ejemplos,
            )
            conexion.execute(
                "INSERT OR IGNORE INTO configuracion VALUES ('presupuesto', '800')"
            )
            conexion.execute(
                "INSERT INTO configuracion VALUES ('datos_iniciales', 'si')"
            )
