import math
import pygame as pg
from pygameUtils import rotate, calc_sides
from dotenv import load_dotenv
import os

CAR_HEIGHT = 100
CAR_WIDTH = 100
RADAR_COLOR = (0, 0, 255)
WHITE_COLOR = (255, 255, 255, 255)
load_dotenv()


class Car(object):
    """Clase Carro para la simulación con pygame"""

    def __init__(self, game_map):
        self.game_map = game_map
        self.surface = pg.image.load('car1.png')
        self.surface = pg.transform.scale(
            self.surface, (CAR_WIDTH, CAR_HEIGHT)
        )
        self.rotate_surface = self.surface
        self.x_pos = 600
        self.y_pos = 655
        self.angle = 0
        self.speed = 7
        self.distance = 0
        self.collided = False
        self.collision_points = []
        self.radars = []
        self.center = [
            self.x_pos + 50, self.y_pos + 50
        ]

    def draw(self, screen):
        """Dibuja el carro en la pantalla"""
        screen.blit(self.rotate_surface, [self.x_pos, self.y_pos])
        self.draw_radar(screen)

    def update(self):
        """Actualiza el estado del carro"""
        #self.x_pos += dif_x
        #self.y_pos += dif_y
        self.distance += self.speed
        #self.angle += dif_angle
        self.x_pos += math.cos(math.radians(360-self.angle)) * self.speed
        self.y_pos += math.sin(math.radians(360-self.angle)) * self.speed
        self.center = [int(self.x_pos + 50), int(self.y_pos + 50)]
        self.rotate_surface = rotate(self.surface, self.angle)

        # Limpia los radares que ya se usaron
        self.update_collision_points()
        self.check_collision()
        self.radars.clear()

        sensoresList = []
        if (int(os.getenv("NUM_SENSORES")) == 3):
            sensoresList = list(range(-90, 120, 90))
        elif (int(os.getenv("NUM_SENSORES")) == 4):
            sensoresList = list(range(-90, 120, 60))
        elif (int(os.getenv("NUM_SENSORES")) == 5):
            sensoresList = list(range(-90, 120, 45))
        elif (int(os.getenv("NUM_SENSORES")) == 9):
            sensoresList = list(range(-90, 120, 25))
        elif (int(os.getenv("NUM_SENSORES")) == 11):
            sensoresList = list(range(-90, 120, 20))

        # Dibuja los radares en los ángulos dados
        for degree in sensoresList:
            self.update_radar(degree)

    def update_radar(self, degree):
        """Actualiza los radares del carro y los agrega a la lista"""
        length = 0

        # Calcula el centro en x del carro, considerando su rotación
        x_len = int(
            self.center[0] + math.cos(
                math.radians(360 - (self.angle + degree))
            ) * length
        )
        # Calcula el centro en y del carro, considerando su rotación
        y_len = int(
            self.center[1] + math.sin(
                math.radians(360 - (self.angle + degree))
            ) * length
        )

        # Verifica que el píxel no esté fuera de rango
        try:
            pixel = self.game_map.get_at((x_len, y_len))
        except IndexError:
            pixel = WHITE_COLOR

        # Verifica si uno de los lados está fuera de la pista
        while pixel != WHITE_COLOR and length < 300:

            try:
                # Intenta obtener el píxel más lejano en el mapa
                pixel = self.game_map.get_at((x_len, y_len))
            except IndexError:
                # Si falla, lo pone como color blanco
                pixel = WHITE_COLOR
            else:
                # Cambia la longitud y actualiza x e y
                length = length + 1

            # Actualiza valores de x
            x_len = int(
                self.center[0] + math.cos(
                    math.radians(360 - (self.angle + degree))
                ) * length
            )

            # Actualiza valores de y
            y_len = int(
                self.center[1] + math.sin(
                    math.radians(360 - (self.angle + degree))
                ) * length
            )

        # Obtiene los lados vertical y horizontal del carro
        horizontal = math.pow(x_len - self.center[0], 2)
        vertical = math.pow(y_len - self.center[1], 2)

        # Si obtenemos la hipotenusa del triángulo, también obtenemos
        # la distancia del radar
        distance = int(math.sqrt(horizontal + vertical))
        self.radars.append([(x_len, y_len), distance])

    def draw_radar(self, screen):
        """Dibuja los radares en la pantalla"""
        self.get_data()
        for radar in self.radars:
            position, _ = radar
            pg.draw.line(screen, RADAR_COLOR, self.center, position, 1)
            pg.draw.circle(screen, RADAR_COLOR, position, 2)

    def update_collision_points(self):
        """Llama a calc_sides para obtener los lados del carro"""
        self.collision_points = calc_sides(self.center, self.angle)

    def check_collision(self):
        """Verifica si alguno de los puntos de colisión del carro es un píxel blanco,
           lo que significa que salió de la pista"""
        self.collided = False

        for point in self.collision_points:

            try:
                if self.game_map.get_at((
                    int(point[0]), int(point[1])
                )) == WHITE_COLOR:
                    self.collided = True
                    break
            except:
                self.collided = True

    def get_collided(self):
        """Devuelve si el carro ha colisionado o no"""
        return self.collided

    def get_reward(self):
        return self.distance/50.0

    def get_data(self):
        inputLayer = []
        for i in range(int(os.getenv("NUM_SENSORES"))):
            inputLayer.append(0)

        for i, radar in enumerate(self.radars):
            inputLayer[i] = int(radar[1]/30)
        return inputLayer

