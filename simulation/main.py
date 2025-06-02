import sys
import pygame
from car import Car
import neat
from dotenv import load_dotenv
import os

# Variables constantes
SCREEN_HEIGHT = 1500
SCREEN_WIDTH = 800
GENERATION = 0

load_dotenv()

# Configuración de la ventana
pygame.display.set_caption('Tesla')
icon = pygame.image.load('car1.png')
pygame.display.set_icon(icon)

# Mapa a probar
env_map = os.getenv('MAP')

if env_map == '1':
    game_map = pygame.image.load('practice_track.png')
elif env_map == '2':
    game_map = pygame.image.load('track1.png')
elif env_map == '3':
    game_map = pygame.image.load('track2.png')
else:
    game_map = pygame.image.load('practice_track.png')



def main():
    """Método principal para ejecutar la ventana de pygame"""

    car = Car(game_map)

    dif_x = 0
    dif_y = 0
    dif_angle = 0
    car_speed = 6

    running = True
    while running:
        # RGB - Rojo, Verde, Azul
        # screen.fill((40, 40, 40))
        screen.blit(game_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Teclas (arriba, abajo, izquierda y derecha)
            if event.type == pygame.KEYDOWN:
                # Vertical
                if event.key == pygame.K_LEFT:
                    #dif_x = -car_speed
                    dif_angle = -car_speed
                if event.key == pygame.K_RIGHT:
                    #dif_x = car_speed
                    dif_angle = car_speed

                # Horizontal
                if event.key == pygame.K_DOWN:
                    dif_y = car_speed
                if event.key == pygame.K_UP:
                    dif_y = -car_speed

                if event.key == pygame.K_SPACE:
                    dif_angle = car_speed

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    dif_x = 0
                    dif_angle = 0

                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    dif_y = 0

                if event.key == pygame.K_SPACE:
                    dif_angle = 0

        # Actualizar métodos del coche
        car.update(dif_x, dif_y, dif_angle)

        if not car.get_collided():
            car.draw(screen)

        # Actualizar pantalla
        pygame.display.update()


def run_car(genomes, config):

    # Inicializar NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Inicializar coches
        cars.append(Car(game_map))

    # Inicializar juego
    pygame.init()
    screen = pygame.display.set_mode((
        SCREEN_HEIGHT, SCREEN_WIDTH
    ))

    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)
    #map = pygame.image.load('map.png')

    # Bucle principal
    global GENERATION
    GENERATION += 1
    while True:
        screen.blit(game_map, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Ingresar datos y obtener resultado de la red
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Actualizar coche y fitness
        remain_cars = 0
        for i, car in enumerate(cars):
            if not(car.get_collided()):
                remain_cars += 1
                car.update()
                genomes[i][1].fitness += car.get_reward()

        # Verificar
        if remain_cars == 0:
            break

        # Dibujar
        screen.blit(game_map, (0, 0))
        for car in cars:
            if not(car.get_collided()):
                car.draw(screen)

        text = generation_font.render(
            "Generación : " + str(GENERATION), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH + 300, 150)
        screen.blit(text, text_rect)

        text = font.render("Coches restantes : " +
                           str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH + 300, 200)
        screen.blit(text, text_rect)

        text = font.render("Número de sensores : " +
                           str(os.getenv("NUM_SENSORES")), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH + 300, 230)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)


if __name__ == "__main__":
    # Establecer archivo de configuración
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Crear clase principal del algoritmo evolutivo
    p = neat.Population(config)

    # Añadir reportero para resultados estadísticos
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Ejecutar NEAT
    p.run(run_car, 1000)
