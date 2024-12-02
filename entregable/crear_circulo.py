import mediapipe as mp
import numpy as np
import cv2
import pygame
import time

# Configuración de MediaPipe
model_path = 'hand_landmarker.task'  # Asegúrate de que este archivo esté en la ubicación correcta

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
detection_result = None

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))  # Tamaño de la ventana Pygame
clock = pygame.time.Clock()

# Parámetros del círculo
circle_radius = 30
circle_color = (255, 0, 0)  # Rojo
circle_x, circle_y = 400, 300  # Posición inicial del círculo

# Función para procesar los resultados de MediaPipe
def get_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global detection_result
    detection_result = result

# Función para dibujar los puntos de la mano en la imagen
def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

    return annotated_image

# Opciones para el HandLandmarker
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=get_result)

with HandLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        image = cv2.flip(image, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        frame_timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, frame_timestamp_ms)

        if detection_result is not None:
            image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)

            # Si se han detectado manos
            if len(detection_result.hand_landmarks) > 0:
                landmarks = detection_result.hand_landmarks[0]
                # Obtener las coordenadas del punto 8 (dedo índice)
                index_finger_tip = landmarks[8]

                # Convertir las coordenadas normalizadas a píxeles
                height, width, _ = image.shape
                finger_x = int(index_finger_tip.x * width)
                finger_y = int(index_finger_tip.y * height)

                # Actualizar la posición del círculo en Pygame
                circle_x, circle_y = finger_x, finger_y

        # Limpiar la pantalla de Pygame
        screen.fill((0, 0, 0))

        # Dibujar el círculo en la nueva posición
        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

        # Mostrar la pantalla de Pygame
        pygame.display.flip()
        clock.tick(30)  # Control de FPS (30 FPS en este caso)

        # Manejo de eventos (cerrar la ventana)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                cv2.destroyAllWindows()
                exit()
