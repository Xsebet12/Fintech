# Imagen base con Python 3.11
FROM python:3.11

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar todo el proyecto al contenedor
COPY . .

# Instalar las dependencias del proyecto
RUN pip install -r requirements.txt

# Cuando arranque el contenedor, correr el pipeline
CMD ["python", "pipeline.py"]