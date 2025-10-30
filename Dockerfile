FROM python:3.11-slim

# Instalar dependencias necesarias para SQL Server (ODBC Driver 18)
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https \
 && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft.list \
 && apt-get update && apt-get install -y msodbcsql18 unixodbc-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto en el que correrá la app
ENV PORT=10000

# Comando para arrancar la app en Render
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:${PORT}", "wsgi:app"]
