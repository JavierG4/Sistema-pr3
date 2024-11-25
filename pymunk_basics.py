import pygame
import pymunk

# Configuración de Pygame
pygame.init()
disp_h = 800
disp_w = 600
display = pygame.display.set_mode((disp_w,disp_h))
clock = pygame.time.Clock()

# Configuración de Pymunk
space = pymunk.Space() # Aqui se crea el espacio 

FPS = 60
running = True
while running:
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT: # X de la ventana
      running = False
  
  pygame.display.flip() # Se muestra los fps de la simulacion 
  clock.tick(FPS)

  space.step(1/FPS) # Para que se sincronice con la pantalla

pygame.quit()