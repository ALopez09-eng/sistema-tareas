FROM python:3.9-slim

# Etiquetas de metadata
LABEL maintainer="proyectoricardo21@gmail.com"
LABEL version="1.0"
LABEL description="Sistema de Gestión de Tareas con Flask"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de la aplicación
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios y establecer permisos
RUN mkdir -p database static templates \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Cambiar a usuario no-root
USER appuser

# Inicializar base de datos
RUN python -c "from app import init_db; init_db()"

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Comando de ejecución
CMD ["python", "app.py"]