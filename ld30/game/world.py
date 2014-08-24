__author__ = 'Oliver Maskery'


from .particles import WorldParticle
from .pedestal import Pedestal
from .totem import Totem
import random
import pygame


class Wind(object):

    def __init__(self):
        self.accel = 0.0

    def update(self):
        self.accel = random.gauss(0.0, 0.01)


class World(object):

    def __init__(self, sheet, particles):
        self.sheet = sheet
        self.particles = particles
        self.size = (100, 30)
        self.tiles = [None] * (self.size[0] * self.size[1])
        self.valid_tiles = []
        self.totems = []
        self.details = []
        self.tile_size = (62, 32)
        self.pixel_size = self.tile_size[0] * self.size[0], self.tile_size[1] * self.size[1]
        self.centre_offset = int(self.pixel_size[0] / 2), int(self.pixel_size[1] / 2)

        self.wind = Wind()
        self.draw_queue = []

        centre_tile = int(self.size[0] / 2), int(self.size[1] / 2)
        self.set_tile_at(centre_tile[0], centre_tile[1], Tile(random.randint(0, 3), None))

        generations = 10
        for step in range(generations):
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    if self.tile_at(x, y) is None:
                        continue

                    tile_value = random.randint(0, 5)

                    if x > 0 and random.random() <= 0.25:
                        self.set_tile_at(x-1, y, Tile(tile_value, None))
                    if x < (self.size[0]-1) and random.random() <= 0.25:
                        self.set_tile_at(x+1, y, Tile(tile_value, None))
                    if y > 0 and random.random() <= 0.25:
                        self.set_tile_at(x, y-1, Tile(tile_value, None))
                    if y < (self.size[1]-1) and random.random() <= 0.25:
                        self.set_tile_at(x, y+1, Tile(tile_value, None))

        self.valid_tiles = [tile for tile in self.tiles if tile is not None]
        choices = self.valid_tiles[0:]
        while len(self.totems) < 3:
            chosen = random.choice(choices)
            choices.remove(chosen)
            x, y = chosen.pos
            chosen.blocked = True

            totem = Totem(sheet, particles)
            totem.pos[0] = x * self.tile_size[0] + int(random.gauss(1, 2))
            totem.pos[1] = y * self.tile_size[1] - 40 + int(random.gauss(0, 2))
            chosen.object = totem
            self.totems.append(totem)
            self.details.append(totem)

        for x in range(random.randint(0, 3)):
            chosen = random.choice(choices)
            choices.remove(chosen)
            x, y = chosen.pos
            chosen.blocked = True

            pedestal = Pedestal(self.wind, sheet, particles)
            pedestal.pos[0] = x * self.tile_size[0] + int(random.gauss(0, 3))
            pedestal.pos[1] = y * self.tile_size[1] - 40 + int(random.gauss(0, 2))
            chosen.object = pedestal
            self.details.append(pedestal)

    def tile_at(self, x, y):
        return self.tiles[y * self.size[0] + x]

    def set_tile_at(self, x, y, value):
        self.tiles[y * self.size[0] + x] = value
        value.pos = [x, y]

    def tile_at_pos(self, x, y):
        tile_x = int(x / self.tile_size[0])
        tile_y = int(y / self.tile_size[1])
        if 0 <= tile_x < self.tile_size[0] and 0 <= tile_y < self.tile_size[1]:
            return self.tile_at(tile_x, tile_y)
        else:
            return None

    def think(self):
        self.wind.update()

        for totem in self.totems:
            totem.think()
        for detail in self.details:
            detail.think()

        if random.random() <= 0.01:
            tile = random.choice(self.valid_tiles)
            px = tile.pos[0] * self.tile_size[0] + (self.tile_size[0] / 2)
            py = tile.pos[1] * self.tile_size[1] + (self.tile_size[1] / 2)
            px += random.gauss(0, self.tile_size[0] / 4)
            py += random.gauss(0, self.tile_size[1] / 4)
            self.particles.add(WorldParticle(self.sheet, px, py))

    def put_in_draw_queue(self, object):
        self.draw_queue.append(object)

    def draw(self, context):
        tile_mappings = [
            (128, 64,  64, 64),
            (128, 128, 64, 64),
            (192, 64,  64, 64),
            (192, 128, 64, 64),
            (128, 192, 64, 64),
            (192, 192, 64, 64),
        ]

        for detail in self.details:
            self.put_in_draw_queue((detail.world_point(), detail))

        self.draw_queue.sort(key=lambda x: x[0][1])

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                tile = self.tile_at(x, y)

                if tile is None:
                    continue

                tx = x * self.tile_size[0] + tile.offset[0]
                ty = y * self.tile_size[1] + tile.offset[1]
                dx = tx - context.camera[0]
                dy = ty - context.camera[1]

                context.dest.blit(self.sheet, (dx, dy), tile_mappings[tile.value])
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                tile = self.tile_at(x, y)

                if tile is None:
                    continue

                tx = x * self.tile_size[0] + tile.offset[0]
                ty = y * self.tile_size[1] + tile.offset[1]

                for point, object in self.draw_queue[0:]:
                    h_hit = tx - 1 <= point[0] < tx + self.tile_size[0] + 1
                    v_hit = ty - 1 <= point[1] < ty + self.tile_size[1] + 1
                    if h_hit and v_hit:
                        object.draw(context)
                        self.draw_queue.remove((point, object))
        self.draw_queue = []


class Tile(object):

    def __init__(self, value, pos):
        self.offset = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.value = value
        self.pos = pos
        self.blocked = False
        self.object = None
