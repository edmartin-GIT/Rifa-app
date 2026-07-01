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
- `passenger_wsgi.py` - punto de entrada alternativo para hosting compartido con Passenger (no aplica a hosting solo-web/cloud sin Python; se deja por si en el futuro se usa cPanel con soporte Python)
- `deploy/rifa-app.service` - unidad systemd para correr la app con Gunicorn en el VPS
- `deploy/nginx-rifa-app.conf` - configuracion de ejemplo de Nginx como proxy reverso
- `requirements-vps.txt` - dependencias de produccion (incluye Gunicorn, solo funciona en Linux)

## Despliegue en VPS (curiositylogic.cloud)

CuriosityLogic.cloud confirmo que el hosting web/cloud normal no soporta apps Python y que se necesita el VPS asociado a la cuenta. Pasos para desplegar ahi via SSH:

1. **Conectarse por SSH** al VPS (tu proveedor te dara el usuario, IP y clave/contrasena).

2. **Instalar Python y Nginx** (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip nginx git
   ```

3. **Clonar el repositorio** en el servidor:
   ```bash
   sudo mkdir -p /var/www/rifa-app
   sudo chown $USER:$USER /var/www/rifa-app
   git clone https://github.com/edmartin-GIT/Rifa-app.git /var/www/rifa-app
   cd /var/www/rifa-app
   ```

4. **Crear entorno virtual e instalar dependencias** (incluye Gunicorn):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-vps.txt
   deactivate
   ```

5. **Configurar el servicio systemd** para que la app corra siempre en segundo plano y arranque con el servidor:
   ```bash
   sudo cp deploy/rifa-app.service /etc/systemd/system/rifa-app.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now rifa-app
   sudo systemctl status rifa-app
   ```
   Si el usuario del servicio (`www-data` en el archivo de ejemplo) no tiene permisos de escritura en `/var/www/rifa-app` (necesarios para crear `rifa.db`), ajusta el dueno de la carpeta:
   ```bash
   sudo chown -R www-data:www-data /var/www/rifa-app
   ```

6. **Configurar Nginx** como proxy reverso hacia Gunicorn:
   ```bash
   sudo cp deploy/nginx-rifa-app.conf /etc/nginx/sites-available/rifa-app
   sudo ln -s /etc/nginx/sites-available/rifa-app /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```
   Antes de esto, crea en tu proveedor de DNS un registro **A** para el subdominio (ej. `rifa.curiositylogic.cloud`) apuntando a la IP del VPS.

7. **Activar HTTPS** con Let's Encrypt:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d rifa.curiositylogic.cloud
   ```

8. La app quedara disponible en `https://rifa.curiositylogic.cloud`. Para futuras actualizaciones de codigo:
   ```bash
   cd /var/www/rifa-app
   git pull
   source .venv/bin/activate
   pip install -r requirements-vps.txt
   deactivate
   sudo systemctl restart rifa-app
   ```

**Importante sobre la base de datos:** SQLite guarda todo en el archivo `rifa.db` dentro de la carpeta de la app (no esta en el control de versiones por diseno). Configura respaldos periodicos de ese archivo, por ejemplo con un cron job que lo copie a otro directorio o a almacenamiento externo.

## Configuracion

Desde la pantalla **Configuracion** dentro de la aplicacion se puede ajustar el precio fijo por tickera (por defecto $100). Este valor aplica solo a las transacciones nuevas; las existentes conservan el precio con el que fueron creadas.
