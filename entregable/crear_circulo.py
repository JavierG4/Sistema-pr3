import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import pygame
import pymunk
import time

# Configuración del modelo MediaPipe
model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
detection_result = None

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0, 0)  # Sin gravedad para movimiento libre

# Crear un círculo en Pymunk
body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
body.position = (320, 240)  # Posición inicial
circle = pymunk.Circle(body, 20)
space.add(body, circle)

# Función para procesar los resultados de MediaPipe
def get_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global detection_result
    detection_result = result

# Función para dibujar marcas en la imagen
def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    annotated_image = np.copy(rgb_image)

    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
            mp.solutions.drawing_styles.get_default_hand_connections_style())
    return annotated_image

# Configurar opciones para MediaPipe
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=get_result)

# Usar MediaPipe HandLandmarker
with HandLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    running = True

    while cap.isOpened() and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # Procesar imagen con MediaPipe
        image = cv2.flip(image, 1)  # Voltear horizontalmente
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        frame_timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, frame_timestamp_ms)

        if detection_result is not None:
            image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)

            # Si se detecta la mano
            if len(detection_result.hand_landmarks) > 0:
                landmarks = detection_result.hand_landmarks[0]
                index_finger_tip = landmarks[8]

                # Convertir coordenadas normalizadas a píxeles
                screen_x = int(index_finger_tip.x * 640)

                # Mantener el circulo dentro de los límites de la pantalla
                screen_x = max(0, min(screen_x, 640))

                # Actualizar posición del círculo
                body.position = screen_x, 240 # Posicion fija en el eje x

        # Actualizar simulación de Pymunk
        space.step(1 / 60.0)

        # Dibujar en Pygame
        screen.fill((255, 255, 255))  # Fondo blanco
        pygame.draw.circle(screen, (0, 0, 255), (int(body.position.x), int(body.position.y)), int(circle.radius))

        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)  # Control de FPS

        # Mostrar imagen de cámara
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:  # Presionar "Esc" para salir
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
