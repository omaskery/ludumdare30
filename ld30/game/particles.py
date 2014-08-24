__author__ = 'Oliver Maskery'


import datetime
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


class FireParticle(object):

    def __init__(self, wind, particles, sheet, x, y):
        self.particles = particles
        self.sheet = sheet
        self.wind = wind
        self.xvel = 0
        self.x = x
        self.y = y
        self.index_x = random.randint(0, 3)
        self.index_y = random.choice([3, 4])
        self.dead = False
        self.lifetime = datetime.timedelta(seconds=random.random() * 1.0)
        self.die_time = datetime.datetime.now() + self.lifetime

    def update(self):
        self.xvel += self.wind.accel
        self.xvel *= 0.99
        self.x += self.xvel
        self.y -= 0.4
        if not self.dead and datetime.datetime.now() >= self.die_time:
            self.dead = True
            if random.random() <= 0.2:
                self.particles.add(SmokeParticle(self.wind, self.sheet, self.x, self.y))

    def draw(self, context):
        dx = self.x - context.camera[0]
        dy = self.y - context.camera[1]
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index_x*6), self.index_y*6, 3, 3))


class SmokeParticle(object):

    def __init__(self, wind, sheet, x, y):
        self.sheet = sheet
        self.wind = wind
        self.xvel = 0
        self.x = x
        self.y = y
        self.index_x = random.randint(0, 3)
        self.index_y = random.choice([1, 2])
        self.dead = False

    def update(self):
        self.xvel += self.wind.accel
        self.xvel *= 0.99
        self.x += self.xvel
        self.y -= 0.4
        if random.random() <= 0.005:
            self.dead = True

    def draw(self, context):
        dx = self.x - context.camera[0]
        dy = self.y - context.camera[1]
        if dy < 0:
            self.dead = True
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index_x*6), self.index_y*6, 3, 3))
