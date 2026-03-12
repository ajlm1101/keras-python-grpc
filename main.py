import io
import grpc
import logging
import numpy as np
import tensorflow as tf
from PIL import Image
from concurrent import futures
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

logging.basicConfig(level = logging.INFO)
log = logging.getLogger("Keras_gRPC")
log.info("Iniciando Keras gRPC...")

import keras_grpc_pb2
import keras_grpc_pb2_grpc

CLASS_NAMES = ["dandelion", "daisy", "tulips", "sunflowers", "roses"]
MODEL_PATH = "mobilenetV2_flowers.keras"
IMG_SIZE = (160, 160)

log.info("Cargando modelo...")
model = tf.keras.models.load_model(MODEL_PATH)
log.info("Modelo cargado con exito!")

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image, dtype=np.float32)
    image_array = preprocess_input(image_array)
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

class KerasPredictionService(keras_grpc_pb2_grpc.KerasPredictionServicer):

    def Predict(self, request, context):
        img = preprocess_image(request.image)
        preds = model.predict(img)
        idx = np.argmax(preds[0])
        predicted_class = CLASS_NAMES[idx]
        confidence = float(preds[0][idx])
        return keras_grpc_pb2.PredictionResponse(
            filename=request.filename,
            predicted_class=predicted_class,
            confidence=confidence
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    keras_grpc_pb2_grpc.add_KerasPredictionServicer_to_server(
        KerasPredictionService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    log.info("Servicor gRPC corriendo en puerto 50051. Esperando peticiones...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()