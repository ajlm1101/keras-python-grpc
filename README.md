# Keras gRPC Server

## Descripción general

Este proyecto implementa un **servidor gRPC para clasificación de imágenes de flores** utilizando un modelo de **Deep Learning basado en MobileNetV2** entrenado con TensorFlow/Keras.

El servidor permite enviar una imagen mediante una petición **gRPC** y recibir como respuesta la **clase de flor predicha junto con su nivel de confianza**.

El modelo cargado (`mobilenetV2_flowers.keras`) ha sido entrenado para clasificar imágenes en cinco categorías de flores:

* Dandelion
* Daisy
* Tulips
* Sunflowers
* Roses

El servicio recibe una imagen en formato binario, la procesa para adaptarla al formato requerido por el modelo y devuelve la predicción correspondiente.

---

# Arquitectura del sistema

El flujo de ejecución del sistema es el siguiente:

1. Se inicia el servidor gRPC y se carga el modelo de TensorFlow.
2. Un cliente envía una petición gRPC al método `Predict`.
3. La imagen se preprocesa para que tenga el formato requerido por MobileNetV2.
4. El modelo realiza la predicción.
5. El servidor devuelve la clase predicha y la probabilidad asociada.

```
Cliente gRPC -> Servidor gRPC -> Preprocesado imagen -> Modelo MobileNetV2 -> Predicción -> Respuesta gRPC
```

---

# Librerías utilizadas

* **TensorFlow**: framework de Deep Learning utilizado para cargar el modelo y realizar predicciones.
* **NumPy**: manipulación de arrays y cálculo de la clase con mayor probabilidad.
* **Pillow (PIL)**: apertura, conversión y redimensionamiento de imágenes.
* **gRPC**: framework de comunicación de alto rendimiento basado en RPC.
* **concurrent.futures**: gestión del pool de hilos del servidor gRPC.
* **logging**: registro de eventos y errores de la aplicación.
* **io**: manejo de datos binarios de la imagen recibida.

Además se utiliza:

`tensorflow.keras.applications.mobilenet_v2.preprocess_input`

para aplicar el preprocesamiento necesario para el modelo MobileNetV2.

También se utilizan los módulos generados a partir de **Protocol Buffers**:

* `keras_grpc_pb2`
* `keras_grpc_pb2_grpc`

Estos archivos definen los **mensajes y servicios gRPC** utilizados por el servidor.

---

# Ejecución del proyecto

Este proyecto requiere **Python 3.12.10**.

## Instalación de dependencias

Las dependencias necesarias se encuentran en el archivo `requirements.txt`.

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar el servidor gRPC

Para iniciar el servidor ejecutar:

```bash
python main.py
```

El servidor gRPC quedará escuchando en el puerto:

```
localhost:50051
```

---

# Explicación del código

## Configuración del modelo

El código define algunas constantes principales:

```python
CLASS_NAMES = ["dandelion", "daisy", "tulips", "sunflowers", "roses"]
MODEL_PATH = "mobilenetV2_flowers.keras"
IMG_SIZE = (160, 160)
```

**CLASS_NAMES:** Lista de clases que el modelo puede predecir.

**MODEL_PATH:** Ruta del archivo del modelo entrenado en formato `.keras`.

**IMG_SIZE:** Tamaño al que se redimensionan todas las imágenes antes de enviarlas al modelo.

## Carga del modelo

Durante el arranque del servidor, el modelo se carga en memoria:

```python
model = tf.keras.models.load_model(MODEL_PATH)
```

Esto permite que las predicciones posteriores sean rápidas, evitando recargar el modelo en cada petición.

## Funciones del código

### preprocess_image()

```python
def preprocess_image(image_bytes):
```

Esta función se encarga de **preparar la imagen recibida para ser utilizada por el modelo de Deep Learning**.

#### Parámetros

* `image_bytes`: imagen recibida en formato binario.

#### Proceso que realiza

1. Abre la imagen desde los bytes recibidos.
2. Convierte la imagen a formato RGB.
3. Redimensiona la imagen a `160x160`.
4. Convierte la imagen en un array de NumPy.
5. Aplica el preprocesado requerido por MobileNetV2.
6. Añade una dimensión adicional para representar el batch.

#### Salida

Devuelve un tensor con forma:

```
(1, 160, 160, 3)
```

Este formato es el esperado por el modelo para realizar predicciones.

---

# Servicio gRPC

El servicio gRPC se implementa mediante la clase:

```python
class KerasPredictionService(keras_grpc_pb2_grpc.KerasPredictionServicer):
```

Esta clase implementa los métodos definidos en el servicio descrito en **Protocol Buffers**.

## Método Predict

### RPC `Predict`

Este método recibe una imagen y devuelve la predicción del modelo.

#### Parámetros de entrada

La petición (`PredictionRequest`) contiene:

* `filename`: nombre del archivo enviado
* `image`: imagen en formato binario

#### Proceso interno

1. Se preprocesa la imagen recibida.
2. Se ejecuta la predicción con el modelo.
3. Se obtiene la clase con mayor probabilidad.
4. Se construye la respuesta gRPC.

#### Código principal

```python
preds = model.predict(img)
idx = np.argmax(preds[0])
predicted_class = CLASS_NAMES[idx]
confidence = float(preds[0][idx])
```

#### Respuesta

El servidor devuelve un mensaje `PredictionResponse` con la siguiente información:

* `filename`: nombre del archivo recibido
* `predicted_class`: clase predicha por el modelo
* `confidence`: probabilidad de la predicción

---

# Servidor gRPC

El servidor se crea mediante la función `serve()`:

```python
def serve():
```

En esta función se realizan las siguientes operaciones:

1. Se crea un servidor gRPC con un **pool de hilos**.
2. Se registra el servicio de predicción.
3. Se configura el puerto de escucha.
4. Se inicia el servidor y queda esperando peticiones.

### Creación del servidor

```python
server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
```

El servidor utiliza un **pool de 3 hilos** para procesar peticiones concurrentes.

### Registro del servicio

```python
keras_grpc_pb2_grpc.add_KerasPredictionServicer_to_server(
    KerasPredictionService(), server
)
```

Esto conecta la implementación del servicio con el servidor gRPC.

### Puerto de escucha

```python
server.add_insecure_port("[::]:50051")
```

El servidor escucha en el **puerto 50051**, que es el puerto habitual utilizado por servicios gRPC.

### Inicio del servidor

```python
server.start()
server.wait_for_termination()
```

El servidor se inicia y permanece activo esperando nuevas peticiones de clientes gRPC.

---

# Dockerización y despliegue

Para facilitar el despliegue y asegurar que el servidor gRPC se ejecute en un entorno controlado, el proyecto puede ejecutarse dentro de un **contenedor Docker**.

## Dockerfile

El proyecto incluye un `Dockerfile` que permite construir la imagen del servidor gRP. Este archivo:

* Utiliza **Python 3.12.10** como imagen base.
* Copia el **modelo**, el archivo **.proto**, las dependencias y el código fuente al contenedor.
* Instala las librerías definidas en `requirements.txt`.
* Genera el código gRPC a partir del archivo `.proto`.
* Expone el puerto **50051**, que es el puerto en el que el servidor gRPC escucha.
* Ejecuta el servidor gRPC con `python main.py`.

---

## Construcción de la imagen

Para construir la imagen Docker, ejecutar:

```bash
docker build -t keras-grpc:v1 .
```

Esto generará una imagen llamada **keras-grpc:v1** con el servidor y todas sus dependencias.

---

## Ejecución del contenedor

Para iniciar el contenedor:

```bash
docker run --name keras-grpc -p 50051:50051 keras-grpc:v1
```

Esto expone el servidor gRPC en el **puerto 50051 del host**, permitiendo que los clientes gRPC se conecten.

---

## Acceso al servidor gRPC

Una vez iniciado el contenedor, el servidor estará disponible en:

```
localhost:50051
```

Los clientes pueden enviar peticiones gRPC al método `Predict` definido en `keras_grpc.proto`.

---

# Posibles mejoras

* Añadir validación del tipo de imagen.
* Implementar predicción por lotes.
* Añadir métricas de rendimiento del servicio.
* Implementar autenticación en las peticiones gRPC.
* Añadir soporte para múltiples versiones del modelo.
