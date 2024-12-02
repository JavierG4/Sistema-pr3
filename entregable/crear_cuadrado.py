import pygame
import pymunk
import pymunk.pygame_util

def create_square(space, pos, size):
    """
    Crea un cuadrado en el espacio de Pymunk.

    Args:
        space (pymunk.Space): El espacio donde se añadirá el cuadrado.
        pos (tuple): Coordenadas iniciales (x, y) del cuadrado.
        size (int): Tamaño del lado del cuadrado.

    Returns:
        pymunk.Body: El cuerpo creado en Pymunk.
    """
    mass = 1
    moment = pymunk.moment_for_box(mass, (size, size))

    body = pymunk.Body(mass, moment)
    body.position = pos

    shape = pymunk.Poly.create_box(body, (size, size))
    shape.friction = 0.5  # Ajusta la fricción según sea necesario
    space.add(body, shape)

    return body

def main():
    # Inicialización de Pygame y Pymunk
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    # Crear espacio de Pymunk
    space = pymunk.Space()
    space.gravity = (0, 900)

    # Crear un suelo
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    static_line = pymunk.Segment(static_body, (50, 550), (750, 550), 5)
    static_line.friction = 1.0
    space.add(static_body, static_line)

    # Configuración para dibujar
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Crear un cuadrado
    create_square(space, (400, 100), 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar el espacio
        space.step(1 / 60.0)

        # Dibujar en la pantalla
        screen.fill((0, 0, 0))
        space.debug_draw(draw_options)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
