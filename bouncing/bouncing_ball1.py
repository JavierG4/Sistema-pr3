import pygame
import pymunk

# Configuración de Pygame
pygame.init()
disp_h = 900
disp_w = 800
display = pygame.display.set_mode((disp_w,disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space()
space.gravity = (0,-500) # Añadimos gravedad a la simulacion
# En pygame el punto (0,0) es arriba ala izuqierda de un cuadrado
# En pymunk el (0,0) esta abajo izquierda
# Por lo que es imporante tener esto en cuenta para hacer la ocnversion de medidas
# restar el alto de la imagen con la y y asi ya tenemos el resultado para ambas
# Foto dia 18 nov 12:30

FPS = 60

# Body y shape de la pelota
# Hay tres tipos de bodys:
# Static como un suelo
# Dynamic pelota
# Kynematic
# Por defecto se crea dynamic
body = pymunk.Body()
body.position = (300,600)
shape = pymunk.Circle(body, 20) 
shape.density = 1 # Con la densidad, y a través del radio, pymunk calcula la masa
space.add(body,shape) # Añadimos a la simulacion el objeto

running = True
while running:
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  
  display.fill ((255,255,255)) # Color rgb del fondo la ventana de
  #En cada frame se actualizan los valores de la pelota, por lo que en cada frame, en ete caso el valor de y cambiara
  pygame.draw.circle(display, (255,0,0), (int(body.position.x), disp_h - int(body.position.y)), int(shape.radius)) # Aqui en y se esta haciendo la conversion y

  pygame.display.flip()
  clock.tick(FPS)

  space.step(1/FPS)

pygame.quit()