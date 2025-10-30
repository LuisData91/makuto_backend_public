FROM python:3.11-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg apt-transport-https ca-certificates unixodbc-dev

# Instalar ODBC Driver 18 para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/microsoft.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Variable de entorno para Render
ENV PORT=10000

# Ejecutar con Gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:${PORT}", "wsgi:app"]
