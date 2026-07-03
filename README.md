# Control de gastos

Aplicación de escritorio para gestionar gastos personales, creada con Python,
CustomTkinter y SQLite.

## Funciones

- Dashboard mensual con total gastado, presupuesto y saldo disponible.
- Selectores de año (desde 2026) y mes para consultar el historial.
- Gráficos de actividad diaria y distribución por categoría.
- Alta, edición y eliminación de gastos.
- Búsqueda por descripción, categoría o fecha dentro del mes seleccionado.
- Presupuesto mensual persistente.
- Validación de importes y fechas.
- Navegación por secciones mediante un menú lateral.

## Tecnologías

- Python 3
- CustomTkinter
- Tkinter
- SQLite

## Instalación

Clona el repositorio, entra en su carpeta y crea un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

En Windows, activa el entorno con:

```powershell
venv\Scripts\activate
```

## Ejecución

```bash
python main.py
```

La base de datos `gastos.db` se crea y configura automáticamente. La aplicación
incluye datos de ejemplo únicamente durante la primera inicialización.

## Estructura

```text
Dashboard/
├── main.py          # Interfaz, navegación, gráficos y validaciones
├── database.py      # Acceso y operaciones SQLite
├── gastos.db        # Base de datos local
├── requirements.txt # Dependencias
└── README.md
```

Los archivos `datos.json` y `config.json` se conservan como datos heredados,
pero la aplicación actual utiliza exclusivamente SQLite.

<img width="1511" height="936" alt="Dash1" src="https://github.com/user-attachments/assets/ccb1f6ed-742f-4107-938a-bd573e7f6299" />

<img width="1512" height="938" alt="Dash2" src="https://github.com/user-attachments/assets/7101ef2b-3c4b-4e19-a127-683f5dea6c2f" />

<img width="1512" height="942" alt="Dash3" src="https://github.com/user-attachments/assets/b7d2c9a8-2926-457b-8792-07df1b265523" />


<img width="1510" height="940" alt="Dash4" src="https://github.com/user-attachments/assets/2d534935-c8c1-4a41-a049-5204d9429b96" />












