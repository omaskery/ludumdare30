__author__ = 'Oliver Maskery'


import random
import math


class ParticleSystem(object):

    def __init__(self):
        self.particles = []

    def add(self, particle):
        self.particles.append(particle)

    def think(self):
        for particle in self.particles:
            particle.update()
        self.particles = [particle for particle in self.particles if particle.y >= 0]

    def draw(self, dest):
        for particle in self.particles:
            particle.draw(dest)


class TotemParticle(object):

    def __init__(self, sheet, x, y, index):
        self.sheet = sheet
        self.x = x
        self.y = y
        self.dx = self.x
        self.t = random.random() * 10.0
        self.index = index

    def update(self):
        self.dx = self.x + math.cos(self.t) * 1.5
        self.t += 0.02 + random.gauss(0.0, 0.01)
        self.y -= 0.4

    def draw(self, dest):
        dest.blit(self.sheet, (self.dx, self.y), (128+(self.index*6), 0, 3, 3))

