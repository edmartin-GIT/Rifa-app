# Control de Rifa

Aplicacion web para el control de venta de tickets de rifa por tickera: registro de transacciones, saldo pendiente, totales por modalidad de pago (CASH, SQUARE, ZELLE) y por tickera, y exportacion a Excel.

## Requisitos

- Python 3.9+
- pip

## Instalacion local

```bash
pip install -r requirements.txt
python app.py
```

La aplicacion queda disponible en `http://localhost:5000`. La base de datos SQLite (`rifa.db`) se crea automaticamente en el primer arranque.

## Estructura

- `app.py` - rutas y logica de la aplicacion (Flask)
- `db.py` - acceso a la base de datos SQLite y configuracion (precio por tickera)
- `templates/` - vistas HTML
- `static/` - CSS
- `passenger_wsgi.py` - punto de entrada para hosting compartido con Passenger (cPanel)

## Despliegue en hosting compartido tipo cPanel (Passenger)

La mayoria de los proveedores de hosting compartido (Namecheap, Hostinger, GoDaddy, etc.) ofrecen "Setup Python App" en cPanel, que usa Phusion Passenger para correr aplicaciones WSGI. Pasos generales:

1. En cPanel, ve a **Setup Python App** y crea una nueva aplicacion:
   - Python version: 3.9 o superior
   - Application root: la carpeta donde subiras este proyecto (ej. `rifa-app`)
   - Application URL: el subdominio o subcarpeta donde quieres que viva (ej. `rifa.curiositylogic.cloud` o `curiositylogic.cloud/rifa`)
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
2. Sube todos los archivos del proyecto a la carpeta de application root (via Git, FTP, o el File Manager de cPanel).
3. Activa el entorno virtual que cPanel genera y corre:
   ```bash
   pip install -r requirements.txt
   ```
4. Reinicia la aplicacion desde el panel de "Setup Python App".
5. La primera vez que arranca, `db.py` crea automaticamente `rifa.db` con las tablas necesarias.

**Importante sobre la base de datos:** SQLite guarda todo en el archivo `rifa.db` dentro de la carpeta de la app. Asegurate de que esa carpeta tenga permisos de escritura para el usuario de la aplicacion, y de incluir `rifa.db` en tus respaldos periodicos (no esta en el control de versiones por diseno).

## Despliegue en VPS (alternativa)

Si en cambio tienes acceso SSH a un servidor (VPS), se recomienda correr con Gunicorn detras de Nginx:

```bash
pip install -r requirements.txt gunicorn
gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

y configurar Nginx como proxy reverso hacia `127.0.0.1:8000`.

## Configuracion

Desde la pantalla **Configuracion** dentro de la aplicacion se puede ajustar el precio fijo por tickera (por defecto $100). Este valor aplica solo a las transacciones nuevas; las existentes conservan el precio con el que fueron creadas.
