__author__ = 'Oliver Maskery'


from .particles import FireParticle
import random


class Pedestal(object):

    def __init__(self, wind, sheet, particles):
        self.wind = wind
        self.sheet = sheet
        self.particles = particles
        self.pos = [0, 0]
        self.lit = True

    def extinguish(self):
        self.lit = False

    def world_point(self):
        return (self.pos[0] + 32, self.pos[1] + 56)

    def think(self):
        x = self.pos[0]+32-2
        y = self.pos[1]+16

        if self.lit and random.random() <= 0.9:
            particle = FireParticle(self.wind, self.particles, self.sheet, x + random.gauss(0.0, 2.0), y + 18)
            self.particles.add(particle)

    def draw(self, context):
        dx = self.pos[0] - context.camera[0]
        dy = self.pos[1] - context.camera[1]
        context.dest.blit(self.sheet, (dx, dy), (192, 0, 64, 64))
