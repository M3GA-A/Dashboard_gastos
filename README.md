# Dashboard de gastos

Proyecto corto para practicar Python, CustomTkinter, Tkinter y SQLite.

## Funciones

- Agregar, editar y eliminar gastos.
- Buscar por descripción, categoría o fecha.
- Guardar un presupuesto mensual.
- Mostrar total gastado y dinero disponible.
- Validar descripción, importe positivo y fecha.

## Abrir el proyecto

1. Abre la carpeta `Dashboard` con Visual Studio Code.
2. En VS Code, selecciona `Terminal > Nueva terminal`.
3. Comprueba que la terminal está situada en el proyecto:

```bash
cd "/Users/naiaramega/Desktop/Dashboard"
```

## Ejecutar la aplicación

Activa el entorno virtual:

```bash
source venv/bin/activate
```

Después ejecuta:

```bash
python main.py
```

También se puede ejecutar directamente, sin activar el entorno:

```bash
venv/bin/python main.py
```

Para detener el programa, cierra su ventana o pulsa `Ctrl + C` en la terminal.

## Instalar CustomTkinter

Este paso solo es necesario si aparece un error indicando que no existe
`customtkinter`:

```bash
python3 -m pip install -r requirements.txt
```

## Ver la base de datos

La base de datos se guarda en el archivo `gastos.db` y se crea automáticamente.

Desde una terminal situada en la carpeta del proyecto, ejecuta:

```bash
sqlite3 gastos.db
```

Una vez dentro de SQLite, puedes usar estos comandos:

```sql
.tables
.schema gastos
SELECT * FROM gastos;
SELECT * FROM configuracion;
.quit
```

- `.tables`: muestra las tablas.
- `.schema gastos`: muestra la estructura de la tabla.
- `SELECT * FROM gastos;`: muestra todos los gastos.
- `SELECT * FROM configuracion;`: muestra el presupuesto.
- `.quit`: cierra SQLite.

## Archivos principales

- `main.py`: interfaz y validaciones.
- `database.py`: conexión y operaciones con SQLite.
- `gastos.db`: base de datos.
- `requirements.txt`: dependencias del proyecto.
