import pygame
import pymunk
import random

# Configuración de Pygame
pygame.init()
disp_h = 800
disp_w = 600
display = pygame.display.set_mode((disp_w, disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0, -500)  # Gravedad hacia abajo

FPS = 60

def convert_coordinates(point):
    return int(point[0]), disp_h - int(point[1])

class Cuadrado:
    def __init__(self, x, y, lado=20, collision_type=1, color=pygame.Color("red")):
        self.lado = lado
        self.collision_type = collision_type
        self.body = pymunk.Body(1, pymunk.moment_for_box(1, (lado, lado)))
        self.body.position = x, y
        # Definir la forma del cuadrado como un polígono
        half_lado = lado / 2
        points = [
            (-half_lado, -half_lado),
            (half_lado, -half_lado),
            (half_lado, half_lado),
            (-half_lado, half_lado)
        ]
        self.shape = pymunk.Poly(self.body, points)
        self.shape.elasticity = 0.8  # Rebote
        self.shape.density = 1
        self.shape.color = color
        self.shape.collision_type = collision_type
        space.add(self.body, self.shape)

    def draw(self):
        # Obtener las coordenadas de los vértices transformados
        points = [convert_coordinates(self.body.local_to_world(vertex)) for vertex in self.shape.get_vertices()]
        pygame.draw.polygon(display, self.shape.color, points)

# Crear cuadrados
cuadrados = []
ultima_posicion_x = None

def crear_cuadrado():
    global ultima_posicion_x
    while True:
        x = random.randint(50, disp_w - 50)  # Posición horizontal aleatoria
        if x != ultima_posicion_x:  # Evitar que coincida con la posición anterior
            ultima_posicion_x = x
            break
    y = disp_h - 50  # Siempre se crea en la parte superior
    lado = random.randint(20, 50)  # Tamaño aleatorio
    color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    cuadrados.append(Cuadrado(x, y, lado=lado, color=color))

# Suelo estático
suelo_body = pymunk.Body(body_type=pymunk.Body.STATIC)
suelo_shape = pymunk.Segment(suelo_body, (0, 10), (disp_w, 10), 5)
suelo_shape.elasticity = 0.8
suelo_shape.collision_type = 2  # Tipo de colisión para el suelo
space.add(suelo_body, suelo_shape)

# Función de colisión: eliminar cuadrados al tocar el suelo
def colision_suelo(arbiter, space, data):
    shape_cuadrado, _ = arbiter.shapes
    # Eliminar la forma y el cuerpo del cuadrado
    space.remove(shape_cuadrado, shape_cuadrado.body)
    # Retirar el cuadrado de la lista para no intentar dibujarlo
    global cuadrados
    cuadrados = [c for c in cuadrados if c.shape != shape_cuadrado]
    return True

# Configurar handler de colisiones
handler = space.add_collision_handler(1, 2)  # Colisión entre cuadrados (1) y suelo (2)
handler.separate = colision_suelo

# Temporizador para crear cuadrados
TIEMPO_CREACION = 1000  # Cada 1000 ms (1 segundo)
pygame.time.set_timer(pygame.USEREVENT, TIEMPO_CREACION)

# Visualizar los cuadrados
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            crear_cuadrado()  # Crear un nuevo cuadrado
    
    # Simular el espacio físico
    space.step(1 / FPS)

    # Dibujar
    display.fill((255, 255, 255))
    for cuadrado in cuadrados:
        cuadrado.draw()
    
    # Dibujar el suelo
    pygame.draw.line(display, pygame.Color("black"), (0, disp_h - 10), (disp_w, disp_h - 10), 5)
    
    pygame.display.flip()
    clock.tick(FPS)
