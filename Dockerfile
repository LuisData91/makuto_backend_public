FROM python:3.11-slim

# Evitar prompts interactivos durante instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias para ODBC y herramientas básicas
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https software-properties-common unixodbc-dev

# Agregar repositorio de Microsoft y su clave GPG
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/microsoft.list

# Instalar el driver ODBC 18 para SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias del proyecto
COPY requirements.txt .

# Instalar librerías Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Configurar variable de entorno para Render
ENV PORT=10000

# Comando de inicio con Gunicorn (Render lo ejecutará)
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:${PORT}", "wsgi:app"]
