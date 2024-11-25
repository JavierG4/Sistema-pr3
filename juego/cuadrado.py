import pygame
import pymunk
import random

# Configuración de Pygame
pygame.init()
disp_h = 800
disp_w = 600
display = pygame.display.set_mode((disp_w,disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0,-500)

FPS = 60

def convert_coordinates (point):
  return int(point[0]), disp_h - int(point[1])

class Cuadrado():
  def __init__(self,x,y, radio = 10, lado = 20, collision_type = 1, color = pygame.Color("red")):
    self.radio = radio
    self.collision_type = collision_type
    self.body = pymunk.Body()
    self.body.position = x,y
    # Definir la forma del cuadrado como un polígono
    half_lado = lado / 2
    points = [
      (-half_lado, -half_lado),
      (half_lado, -half_lado),
      (half_lado, half_lado),
      (-half_lado, half_lado)
    ]
    self.shape = pymunk.Poly(self.body, points)
    self.shape.elasticity = 1
    self.shape.density = 1
    self.shape.color = color

  def draw(self):
    # Dibujar el cuadrado en Pygame
    points = [convert_coordinates(self.body.local_to_world(vertex)) for vertex in self.shape.get_vertices()]
    pygame.draw.polygon(display, self.shape.color, points)

# Crear un cuadrado
cuadrado = Cuadrado(300,450)
cuadrado2 = Cuadrado(200,150, color = pygame.Color("blue"))

# Visualizar el cuadrado
running = True

while running:
    
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
    
    display.fill ((255,255,255))
    cuadrado.draw()
    cuadrado2.draw()
    pygame.display.flip()
    clock.tick(FPS)
    