FROM python:3.12.10

WORKDIR /app

# evitar cache y archivos pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# copiamos requirements, modelo y codigo fuente
COPY mobilenetV2_flowers.keras .
COPY keras_grpc.proto .
COPY requirements.txt .
COPY main.py .

# instalar dependencias python
RUN pip install --no-cache-dir -r requirements.txt

# generar codigo gRPC desde el proto
RUN python -m grpc_tools.protoc -I . --python_out=.  --grpc_python_out=.  keras_grpc.proto

# exponer puerto gRPC
EXPOSE 50051

# ejecutar servidor
CMD ["python", "main.py"]