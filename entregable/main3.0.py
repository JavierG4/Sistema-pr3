import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import pygame
import random
import pymunk
import time

# Configuración de MediaPipe
model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
detection_result = None

def get_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global detection_result
    detection_result = result

# Configuración de Pygame
pygame.init()
disp_h = 800
disp_w = 800
display = pygame.display.set_mode((disp_w, disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0, -500)

collision_types = {
    "Enemigo": 1,
    "player": 2,
}

Vector_objetos_enemigos = []

def convert_coordinates(point):
    return int(point[0]), disp_h - int(point[1])

def remove_object_by_id(objects, id):
    for obj in objects:
        if obj.id == id:
            objects.remove(obj)
            break

# Función para terminar el juego al colisionar player con enemigo
def fin_del_juego(arbiter, space, data):
    print("Fin del juego")
    pygame.quit()
    exit()

# Configuración de colisiones
handler = space.add_collision_handler(collision_types["Enemigo"], collision_types["player"])
handler.begin = fin_del_juego

# Pelota controlada por MediaPipe
player_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
player_body.position = (300, 100)
player_shape = pymunk.Circle(player_body, 20)
player_shape.collision_type = collision_types["player"]
space.add(player_body, player_shape)

# Función para generar un nuevo cuadrado
def crear_cuadrado():
    x_position = random.randint(0, disp_w - 30)  # Posición horizontal aleatoria
    y_position = disp_h - 10  # Comienza cerca del techo
    size = 30
    body = pymunk.Body()
    body.position = (x_position, y_position)
    shape = pymunk.Poly.create_box(body, (size, size))
    shape.density = 1
    shape.id = len(Vector_objetos_enemigos) + 1
    shape.collision_type = collision_types["Enemigo"]
    Vector_objetos_enemigos.append(shape)
    space.add(body, shape)

# Configuración de MediaPipe HandLandmarker
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=get_result)

# Tiempo para generar nuevos cuadrados
tiempo_inicio = time.time()
intervalo_cuadrados = 2  # Segundos entre cada cuadrado

with HandLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    running = True

    while cap.isOpened() and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        success, image = cap.read()
        if not success:
            continue

        # Control del tiempo para generar nuevos cuadrados
        tiempo_actual = time.time()
        if tiempo_actual - tiempo_inicio > intervalo_cuadrados:
            crear_cuadrado()
            tiempo_inicio = tiempo_actual

        # Procesar imagen con MediaPipe
        image = cv2.flip(image, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        frame_timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, frame_timestamp_ms)

        # Control de la pelota con MediaPipe
        if detection_result is not None and len(detection_result.hand_landmarks) > 0:
            landmarks = detection_result.hand_landmarks[0]
            index_finger_tip = landmarks[8]
            screen_x = int(index_finger_tip.x * disp_w)
            screen_x = max(0, min(screen_x, disp_w))  # Mantener dentro de los límites
            player_body.position = screen_x, player_body.position.y  # Mover solo horizontalmente

        # Dibujar en Pygame
        display.fill((255, 255, 255))
        for obj in Vector_objetos_enemigos:
            vertices = [convert_coordinates(v.rotated(obj.body.angle) + obj.body.position) for v in obj.get_vertices()]
            pygame.draw.polygon(display, (255, 0, 255), vertices)

        pygame.draw.circle(display, (0, 0, 255), convert_coordinates(player_body.position), int(player_shape.radius))

        pygame.display.flip()
        clock.tick(60)

        # Actualizar simulación de Pymunk
        space.step(1 / 60.0)

    cap.release()
    pygame.quit()
    cv2.destroyAllWindows()