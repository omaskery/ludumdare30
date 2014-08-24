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
        self.particles = [particle for particle in self.particles if not particle.dead]

    def draw(self, dest):
        for particle in self.particles:
            particle.draw(dest)


class TotemParticle(object):

    def __init__(self, sheet, x, y):
        self.sheet = sheet
        self.x = x
        self.y = y
        self.dx = self.x
        self.t = random.random() * 10.0
        self.index = random.randint(0, 3)
        self.dead = False

    def update(self):
        self.dx = self.x + math.cos(self.t) * 1.5
        self.t += 0.02 + random.gauss(0.0, 0.01)
        self.y -= 0.6

    def draw(self, context):
        dx = self.dx - context.camera[0]
        dy = self.y - context.camera[1]
        if dy < 0:
            self.dead = True
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index*6), 0, 3, 3))


class WorldParticle(object):

    def __init__(self, sheet, x, y):
        self.sheet = sheet
        self.x = x
        self.y = y
        self.dx = self.x
        self.t = random.random() * 10.0
        self.index = random.randint(0, 3)
        self.dead = False

    def update(self):
        self.dx = self.x + math.cos(self.t) * 1.5
        self.t += 0.02 + random.gauss(0.0, 0.01)
        self.y -= 0.4

    def draw(self, context):
        dx = self.dx - context.camera[0]
        dy = self.y - context.camera[1]
        if dy < 0:
            self.dead = True
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index*6), 6, 3, 3))

