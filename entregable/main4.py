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
space.gravity = (0, -800)

collision_types = {
    "Enemigo": 1,
    "power_up": 2,
    "bottom": 3,
    "player": 4,
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

def remove_object(arbiter, space, data):
  print ("Colisión")
  shape = arbiter.shapes[0]
  space.remove(shape, shape.body)
  remove_object_by_id(Vector_objetos_enemigos, shape.id)
  return True

# Configuración de colisiones
handler = space.add_collision_handler(collision_types["Enemigo"], collision_types["player"])
handler.begin = fin_del_juego

# Configuración de colisiones
handler = space.add_collision_handler(collision_types["Enemigo"], collision_types["bottom"])
handler.begin = remove_object

# Pelota controlada por MediaPipe
player_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
player_body.position = (300, 100)
player_shape = pymunk.Circle(player_body, 20)
player_shape.collision_type = collision_types["player"]
space.add(player_body, player_shape)

# Body y shape de techo
segment_body = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body, (0, disp_h), (disp_w, disp_h), 10)
space.add(segment_body, segment_shape)

# Body y shape de la pared derecha
segment_body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape2 = pymunk.Segment(segment_body2, (disp_w, disp_h), (disp_w, 0), 10)
space.add(segment_body2, segment_shape2)

# Body y shape de la pared izquierda
segment_body3 = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape3 = pymunk.Segment(segment_body3, (0, disp_h), (0, 0), 10)
space.add(segment_body3, segment_shape3)

# Body y shape del suelo (sensor)
floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
floor_shape = pymunk.Segment(floor_body, (0, 0), (disp_w, 0), 10)
floor_shape.sensor = True
floor_shape.collision_type = collision_types["bottom"]
space.add(floor_body, floor_shape)

# Añadimos soporte para flechas y power-ups
# Configuración iniciales, librerías y código proporcionado arriba

# Variables adicionales
power_up_active = False  # Indica si el jugador tiene un power-up activo
last_power_up_time = time.time()
flechas = []

# Función para crear un power-up
def crear_power_up():
    x_position = random.randint(30, disp_w - 30)  # Posición horizontal aleatoria
    y_position = disp_h - 30
    size = 40
    body = pymunk.Body()
    body.position = (x_position, y_position)
    shape = pymunk.Poly.create_box(body, (size, size))
    shape.collision_type = collision_types["power_up"]
    space.add(body, shape)
    return shape

# Función para disparar una flecha
def disparar_flecha(x, y):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = (x, y)
    shape = pymunk.Segment(body, (0, 0), (0, -20), 5)  # Flecha vertical
    shape.collision_type = collision_types["Enemigo"]  # Se aprovecha este tipo para manejar colisiones
    space.add(body, shape)
    flechas.append((body, shape))

# Colisiones para recoger el power-up
def recoger_power_up(arbiter, space, data):
    global power_up_active
    shape = arbiter.shapes[0]
    space.remove(shape, shape.body)
    power_up_active = True
    return True

# Colisiones para las flechas
def flecha_colision(arbiter, space, data):
    shape1, shape2 = arbiter.shapes
    space.remove(shape1, shape1.body)  # Eliminar flecha
    space.remove(shape2, shape2.body)  # Eliminar cuadrado
    remove_object_by_id(Vector_objetos_enemigos, shape2.id)
    return True

# Configuración de manejadores de colisiones
handler_power_up = space.add_collision_handler(collision_types["power_up"], collision_types["player"])
handler_power_up.begin = recoger_power_up

handler_flechas = space.add_collision_handler(collision_types["Enemigo"], collision_types["Enemigo"])
handler_flechas.begin = flecha_colision

# Función para generar un nuevo cuadrado
def crear_cuadrado():
    x_position = random.randint(30, disp_w - 30)  # Posición horizontal aleatoria
    y_position = disp_h - 30  # Comienza cerca del techo
    size = 60
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
intervalo_cuadrados = 0.5  # Segundos entre cada cuadrado

# Bucle principal con soporte para flechas y power-ups
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

        # Crear un power-up cada 10 segundos
        if time.time() - last_power_up_time > 10:
            crear_power_up()
            last_power_up_time = time.time()

        # Procesar imagen con MediaPipe
        image = cv2.flip(image, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        frame_timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, frame_timestamp_ms)

        # Control de la pelota con MediaPipe
        if detection_result is not None and len(detection_result.hand_landmarks) > 0:
            landmarks = detection_result.hand_landmarks[0]
            index_finger_tip = landmarks[8]
            fist_detected = all(landmarks[i].y > landmarks[9].y for i in [5, 9, 13, 17])  # Detección básica de puño

            screen_x = int(index_finger_tip.x * disp_w)
            screen_x = max(0, min(screen_x, disp_w))  # Mantener dentro de los límites
            player_body.position = screen_x, player_body.position.y  # Mover solo horizontalmente

            # Disparar flechas si hay power-up activo y se detecta un puño
            if power_up_active and fist_detected:
                disparar_flecha(screen_x, player_body.position.y)

        # Dibujar en Pygame
        display.fill((255, 255, 255))
        for obj in Vector_objetos_enemigos:
            vertices = [convert_coordinates(v.rotated(obj.body.angle) + obj.body.position) for v in obj.get_vertices()]
            pygame.draw.polygon(display, (255, 0, 255), vertices)

        pygame.draw.circle(display, (0, 0, 255), convert_coordinates(player_body.position), int(player_shape.radius))
        pygame.draw.line(display, (0, 0, 0), convert_coordinates((0, disp_h)), convert_coordinates((disp_w, disp_h)), 10)
        pygame.draw.line(display, (0, 0, 0), (disp_w, disp_h), (disp_w, 0), 15)
        pygame.draw.line(display, (0, 0, 0), (0, disp_h), (0, 0), 10)
        pygame.draw.line(display, (255, 0, 0), convert_coordinates((0, 0)), convert_coordinates((disp_w, 0)), 10)

        # Dibujar flechas
        for body, shape in flechas:
            x, y = body.position
            pygame.draw.line(display, (0, 255, 0), (x, y), (x, y - 20), 5)

        pygame.display.flip()
        clock.tick(60)

        # Actualizar simulación de Pymunk
        space.step(1 / 60.0)