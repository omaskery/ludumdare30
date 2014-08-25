__author__ = 'Oliver Maskery'


from .particles import TotemParticle
import random


class Totem(object):

    def __init__(self, sheet, particles, direction):
        self.direction = direction
        self.sheet = sheet
        self.particles = particles
        self.pos = [0, 0]
        self.intensity = 0.1

    def world_point(self):
        return (self.pos[0] + 32, self.pos[1] + 64)

    def think(self):
        x = self.pos[0]+32-2
        y = self.pos[1]+16
        if random.random() <= (0.2 * self.intensity):
            particle = TotemParticle(self.sheet, x + random.gauss(0.0, 2.0), y, self.intensity)
            self.particles.add(particle)
        if random.random() <= (0.05 * self.intensity):
            side_x = x
            if random.random() <= 0.5:
                side_x -= 16
            else:
                side_x += 16
            particle = TotemParticle(self.sheet, side_x + random.gauss(0.0, 2.0), y+40, self.intensity)
            self.particles.add(particle)

    def draw(self, context):
        dx = self.pos[0] - context.camera[0]
        dy = self.pos[1] - context.camera[1]
        context.dest.blit(self.sheet, (dx, dy), (0, 64, 64, 64))
        for index in range(1, 30):
            dy = self.pos[1] - (64 * index) - context.camera[1]
            context.dest.blit(self.sheet, (dx, dy), (0, 0, 64, 64))
            if dy < 0:
                break

