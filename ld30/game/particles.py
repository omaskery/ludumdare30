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


class BaseParticle(object):

    def __init__(self, sheet, x, y):
        self.sheet = sheet
        self.x = x
        self.y = y
        self.x_index = 0
        self.y_index = 0
        self.dead = False

    def set_index(self, x, y):
        self.x_index = x
        self.y_index = y

    def die(self):
        self.dead = True

    def update(self):
        pass

    def draw(self, context):
        dx = self.x - context.camera[0]
        dy = self.y - context.camera[1]
        context.dest.blit(self.sheet, (dx, dy), (128+(self.x_index*6), self.y_index*6, 6, 6))


class TotemParticle(BaseParticle):

    def __init__(self, sheet, x, y, intensity):
        super().__init__(sheet, x, y)

        self.intensity = intensity
        self.base_x = self.x
        self.t = random.random() * 10.0

        self.set_index(random.randint(0, 3), 0)

    def update(self):
        self.x = self.base_x + math.cos(self.t) * 1.5
        self.t += 0.02 + random.gauss(0.0, 0.01)
        self.y -= max(self.intensity, 0.4)

    def draw(self, context):
        if self.y - context.camera[1] < 0:
            self.die()
        else:
            super().draw(context)


class WorldParticle(BaseParticle):

    def __init__(self, sheet, x, y):
        super().__init__(sheet, x, y)

        self.yspeed = random.gauss(0.5, 0.02)
        self.base_x = self.x
        self.t = random.random() * 10.0

        self.set_index(random.randint(0, 3), 1)

    def update(self):
        self.x = self.base_x + math.cos(self.t) * 1.5
        self.t += 0.02 + random.gauss(0.0, 0.01)
        self.y -= max(self.yspeed, 0.01)

    def draw(self, context):
        if self.y - context.camera[1] < 0:
            self.die()
        else:
            super().draw(context)


class FireParticle(object):

    def __init__(self, wind, particles, sheet, x, y):
        self.particles = particles
        self.sheet = sheet
        self.wind = wind
        self.xvel = 0
        self.x = x
        self.y = y
        self.yspeed = 0.1 + random.random() * 0.8
        self.index_x = random.randint(0, 3)
        self.index_y = random.choice([3, 4])
        self.dead = False
        self.lifetime = datetime.timedelta(seconds=random.gauss(0.5, 0.5) * 1.0)
        self.die_time = datetime.datetime.now() + self.lifetime
        self.coefficient = random.random()

    def update(self):
        self.xvel += self.wind.accel * self.coefficient
        self.xvel *= 0.99
        self.x += self.xvel
        self.y -= self.yspeed
        if not self.dead and datetime.datetime.now() >= self.die_time:
            self.dead = True
            if random.random() <= 0.4:
                self.particles.add(SmokeParticle(self.wind, self.sheet, self.x, self.y))

    def draw(self, context):
        dx = self.x - context.camera[0]
        dy = self.y - context.camera[1]
        if dy < 0:
            self.dead = True
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index_x*6), self.index_y*6, 6, 6))


class SmokeParticle(object):

    def __init__(self, wind, sheet, x, y):
        self.sheet = sheet
        self.wind = wind
        self.xvel = 0
        self.x = x
        self.y = y
        self.yspeed = 0.1 + random.random() * 0.4
        self.index_x = random.randint(0, 3)
        self.index_y = random.choice([1, 2])
        self.dead = False

    def update(self):
        self.xvel += self.wind.accel
        self.xvel *= 0.999
        self.x += self.xvel
        self.y -= self.yspeed
        if random.random() <= 0.005:
            self.dead = True

    def draw(self, context):
        dx = self.x - context.camera[0]
        dy = self.y - context.camera[1]
        if dy < 0:
            self.dead = True
        context.dest.blit(self.sheet, (dx, dy), (128+(self.index_x*6), self.index_y*6, 6, 6))
