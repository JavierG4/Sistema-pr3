import pygame
import mediapipe as mp
import numpy as np
import cv2
import time

# Configuración para MediaPipe
model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
detection_result = None

tips_id = [4, 8, 12, 16, 20]

def get_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global detection_result
    detection_result = result

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

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=get_result)

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Crear el espacio de Pygame
space = pygame.Surface((800, 600))
running = True

# Crear el círculo controlable por el dedo índice
circle_radius = 30
circle_color = (255, 0, 0)  # Rojo
circle_x, circle_y = 400, 300  # Posición inicial

with HandLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)

    while cap.isOpened() and running:
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
            
            if len(detection_result.hand_landmarks) > 0:
                landmarks = detection_result.hand_landmarks[0]
                # Obtener coordenadas normalizadas del punto 8 (dedo índice)
                index_finger_tip = landmarks[8]
                
                # Convertir las coordenadas normalizadas a píxeles
                height, width, _ = image.shape
                finger_x = int(index_finger_tip.x * width)
                finger_y = int(index_finger_tip.y * height)

                # Actualizar la posición del círculo en Pygame
                circle_x, circle_y = finger_x, finger_y

        # Dibujar el círculo en la nueva posición
        screen.fill((0, 0, 0))  # Limpiar pantalla
        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

        # Mostrar la pantalla de Pygame
        pygame.display.flip()
        clock.tick(30)  # Control de FPS

        # Manejo de eventos (cerrar la ventana)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    cap.release()
    pygame.quit()
    cv2.destroyAllWindows()
