FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements-vps.txt ./
RUN pip install --no-cache-dir -r requirements-vps.txt
COPY . .
ENV RIFA_DB_PATH=/app/data/rifa.db
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
