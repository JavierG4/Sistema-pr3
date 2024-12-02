import pygame
import random
import pymunk
from entregable.crear_cuadrado import create_square


# Crear listas de  
def remove_object_by_id(objects, id):
  for obj in objects:
    if obj.id == id:
      objects.remove(obj)
      break

collision_types = {
  "Enemigo": 1,
  "power_up": 2,
  "bottom": 3,
  "player": 4,
}

Vector_objetos_enemigos = []

FPS = 60

def convert_coordinates(point):
  return int(point[0]), disp_h - int(point[1])

# Configuración de Pygame
pygame.init()
disp_h = 800
disp_w = 800
display = pygame.display.set_mode((disp_w, disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0, -500)  # Añadimos gravedad a la simulacion

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

def remove_object(arbiter, space, data):
  print ("Colisión")
  shape = arbiter.shapes[0]
  space.remove(shape, shape.body)
  remove_object_by_id(Vector_objetos_enemigos, shape.id)
  return True

# Configuración de colisiones
handler = space.add_collision_handler(collision_types["Enemigo"], collision_types["bottom"])
handler.begin = remove_object

# Body y shape de la pelota Temporal
bodyp = pymunk.Body()
bodyp.position = (300, 600)
shapep = pymunk.Circle(bodyp, 20)
shapep.density = 1
shapep.collision_type = collision_types["player"]
space.add(bodyp, shapep)

running = True

#Creacion de cuadrados
for i in range(5):
  x_position = random.randint(0, disp_w)
  y_position = disp_h - 10  # Cerca del techo
  size = 30  # Tamaño del cuadrado
  body = pymunk.Body()
  body.position = (x_position, y_position)
  shape = pymunk.Poly.create_box(body, (size, size))
  shape.density = 1
  shape.id = i + 2  # IDs únicos para cada cuadrado
  shape.collision_type = collision_types["Enemigo"]
  Vector_objetos_enemigos.append(shape)
  space.add(body, shape)

while running:

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  display.fill((255, 255, 255))
  for obj in Vector_objetos_enemigos:
    vertices = [convert_coordinates(v.rotated(obj.body.angle) + obj.body.position) for v in obj.get_vertices()]
    pygame.draw.polygon(display, (255, 0,255), vertices)
  
  pygame.draw.circle(display, (255, 0, 0), convert_coordinates(bodyp.position), int(shapep.radius))
  pygame.draw.line(display, (0, 0, 0), convert_coordinates((0, disp_h)), convert_coordinates((disp_w, disp_h)), 10)
  pygame.draw.line(display, (0, 0, 0), (disp_w, disp_h), (disp_w, 0), 10)
  pygame.draw.line(display, (0, 0, 0), (0, disp_h), (0, 0), 10)
  pygame.draw.line(display, (255, 0, 0), convert_coordinates((0, 0)), convert_coordinates((disp_w, 0)), 10)
  pygame.display.flip()
  clock.tick(FPS)

  space.step(1 / FPS)
  # Vector para guardar objetos
  objects = [shape]
