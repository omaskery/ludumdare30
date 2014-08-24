__author__ = 'Oliver Maskery'


from .particles import TotemParticle
import random


class Totem(object):

    def __init__(self, sheet, particles):
        self.sheet = sheet
        self.particles = particles
        self.pos = [0, 0]
        self.glowing = False

    def think(self):
        if random.random() <= 0.02:
            self.glowing = not self.glowing
        types = [0, 1, 2, 3]

        x = self.pos[0]+32-2
        y = self.pos[1]+16
        if random.random() <= 0.05:
            particle = TotemParticle(self.sheet, x + random.gauss(0.0, 2.0), y, random.choice(types))
            self.particles.add(particle)
        if random.random() <= 0.005:
            side_x = x
            if random.random() <= 0.5:
                side_x -= 16
            else:
                side_x += 16
            particle = TotemParticle(self.sheet, side_x + random.gauss(0.0, 2.0), y+40, random.choice(types))
            self.particles.add(particle)

    def draw(self, dest):
        if self.glowing:
            src_x = 64
        else:
            src_x = 0

        dest.blit(self.sheet, self.pos, (src_x, 64, 64, 64))
        for index in range(1, 30):
            dy = self.pos[1] - (64 * index)
            dest.blit(self.sheet, (self.pos[0], dy), (src_x, 0, 64, 64))
            if dy < 0:
                break

