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
- `db.py` - acceso a la base de datos SQLite y configuracion (precio por tickera). Respeta la variable de entorno `RIFA_DB_PATH` para ubicar el archivo de base de datos (usado en Docker para apuntar a un volumen persistente).
- `templates/` - vistas HTML
- `static/` - CSS
- `Dockerfile` - imagen de produccion (Gunicorn) usada en el despliegue con Docker + Traefik
- `passenger_wsgi.py` - punto de entrada alternativo para hosting compartido con Passenger (no aplica a hosting solo-web/cloud sin Python)
- `deploy/rifa-app.service` + `deploy/nginx-rifa-app.conf` - alternativa con systemd + Nginx, para un VPS *sin* Docker/Traefik
- `requirements-vps.txt` - dependencias de produccion (incluye Gunicorn, solo funciona en Linux)

## Despliegue en el VPS de curiositylogic.cloud (Docker + Traefik)

Este VPS ya corre **Traefik** (reverse proxy en Docker) gestionando otros servicios (n8n, orqagent) desde un `docker-compose.yml` central en `/root/docker-compose.yml`. Traefik detecta automaticamente los contenedores por sus labels y emite certificados HTTPS via Let's Encrypt. Rifa-app se agrega como un servicio mas de ese mismo compose, sin tocar los demas.

1. **Clonar el repo en el servidor:**
   ```bash
   git clone https://github.com/edmartin-GIT/Rifa-app.git /var/www/rifa-app
   ```

2. **Agregar el servicio `rifa-app` a `/root/docker-compose.yml`** (junto a los servicios existentes `traefik`, `n8n`, `orqagent`):
   ```yaml
     rifa-app:
       build: /var/www/rifa-app
       restart: always
       volumes:
         - rifa_data:/app/data
       labels:
         - traefik.enable=true
         - traefik.http.routers.rifa-app.rule=Host(`rifa.curiositylogic.cloud`)
         - traefik.http.routers.rifa-app.tls=true
         - traefik.http.routers.rifa-app.entrypoints=web,websecure
         - traefik.http.routers.rifa-app.tls.certresolver=mytlschallenge
         - traefik.http.services.rifa-app.loadbalancer.server.port=8000
   ```
   Y agregar `rifa_data:` a la seccion `volumes:` al final del archivo (volumen para persistir `rifa.db` entre reconstrucciones del contenedor).

3. **Crear el registro DNS** tipo A: `rifa.curiositylogic.cloud` -> IP del VPS (necesario para que Traefik pueda emitir el certificado TLS).

4. **Levantar el nuevo servicio** (no afecta a n8n/orqagent, que siguen corriendo):
   ```bash
   cd /root
   docker compose up -d --build rifa-app
   ```

5. La app queda disponible en `https://rifa.curiositylogic.cloud`. Para actualizaciones futuras:
   ```bash
   cd /var/www/rifa-app && git pull
   cd /root && docker compose up -d --build rifa-app
   ```

**Importante sobre la base de datos:** dentro del contenedor, `rifa.db` vive en `/app/data/rifa.db` (variable `RIFA_DB_PATH`), respaldado por el volumen Docker `rifa_data` para que sobreviva a reconstrucciones de la imagen. Aun asi, conviene respaldar ese volumen periodicamente (`docker run --rm -v rifa_data:/data -v $(pwd):/backup alpine tar czf /backup/rifa_data_backup.tar.gz /data`).

## Despliegue alternativo en VPS sin Docker (Nginx + systemd)

Si en el futuro se despliega en un VPS tradicional sin Docker/Traefik, se puede usar Gunicorn + systemd + Nginx con los archivos en `deploy/`:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nginx git
git clone https://github.com/edmartin-GIT/Rifa-app.git /var/www/rifa-app
cd /var/www/rifa-app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-vps.txt
deactivate
sudo cp deploy/rifa-app.service /etc/systemd/system/rifa-app.service
sudo systemctl daemon-reload && sudo systemctl enable --now rifa-app
sudo cp deploy/nginx-rifa-app.conf /etc/nginx/sites-available/rifa-app
sudo ln -s /etc/nginx/sites-available/rifa-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d rifa.curiositylogic.cloud
```

## Configuracion

Desde la pantalla **Configuracion** dentro de la aplicacion se puede ajustar el precio fijo por tickera (por defecto $100). Este valor aplica solo a las transacciones nuevas; las existentes conservan el precio con el que fueron creadas.
