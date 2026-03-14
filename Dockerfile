# Imagen base
FROM python:3.12.10

# Directorio de trabajo
WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copiamos archivos del host al contenedor
COPY mobilenetV2_flowers.keras .
COPY keras_grpc.proto .
COPY requirements.txt .
COPY main.py .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Generamos codigo gRPC desde el fichero proto
RUN python -m grpc_tools.protoc -I . --python_out=.  --grpc_python_out=.  keras_grpc.proto

# Exponemos puerto del servicio
EXPOSE 50051

# Inciamos el servidor
CMD ["python", "main.py"]