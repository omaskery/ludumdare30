__author__ = 'Oliver Maskery'


import datetime
import pygame
import random
import math


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


class Game(object):

    def __init__(self, debug_client, settings):
        self.dc = debug_client
        self.settings = settings

        default_page = self.dc.get_page('default')
        framerates = default_page.get_section('Framerates')
        self.fps = framerates.get_value('FPS', 'int', 0)
        self.lps = framerates.get_value('LPS', 'int', 0)

        status = default_page.get_section('Status')
        self.status_string = status.get_value('Status', 'string', 'initialising')
        uuid = status.get_value('UUID', 'string', self.settings['uuid'])
        uuid.set(self.settings['uuid'])  # in case it existed before!

        rendering = default_page.get_section('Rendering')
        self.particle_count = rendering.get_value('Particle Count', 'int', 0)

        self.totem_sheet = None
        self.totems = []
        self.particles = []

        for index in range(3):
            angle = random.random() * (2 * math.pi)
            radius = 100 + random.gauss(100, 10)
            x = 400 + math.cos(angle) * radius
            y = 300 + math.sin(angle) * radius
            self.totems.append([x, y, False])

    def think(self):
        types = [0, 1, 2, 3]
        for totem in self.totems:
            x = totem[0]+32-2
            y = totem[1]+16
            if random.random() <= 0.05:
                particle = TotemParticle(self.totem_sheet, x + random.gauss(0.0, 2.0), y, random.choice(types))
                self.particles.append(particle)
            if random.random() <= 0.005:
                side_x = x
                if random.random() <= 0.5:
                    side_x -= 16
                else:
                    side_x += 16
                particle = TotemParticle(self.totem_sheet, side_x + random.gauss(0.0, 2.0), y+40, random.choice(types))
                self.particles.append(particle)
        self.particle_count.quick_set(len(self.particles))
        for particle in self.particles:
            particle.update()
        self.particles = [particle for particle in self.particles if particle.y >= 0]

    def draw(self, dest):
        dest.fill((128, 128, 128))

        for totem in self.totems:
            if random.random() <= 0.02:
                totem[2] = not totem[2]

            if totem[2]:
                src_x = 64
            else:
                src_x = 0

            dest.blit(self.totem_sheet, (totem[0], totem[1]), (src_x, 64, 64, 64))
            for index in range(1, 30):
                dy = totem[1] - (64 * index)
                dest.blit(self.totem_sheet, (totem[0], dy), (src_x, 0, 64, 64))
                if dy < 0:
                    break
        for particle in self.particles:
            particle.draw(dest)

    def run(self):
        self.status_string.quick_set('initialising pygame')

        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        running = True

        self.totem_sheet = pygame.transform.scale2x(pygame.image.load('data/sprites/totem.png').convert_alpha())

        draw_frames = 0
        logic_frames = 0

        self.status_string.quick_set('configuring timers')
        stat_period = datetime.timedelta(seconds=1.0)
        next_stat = datetime.datetime.now() + stat_period

        think_period = datetime.timedelta(seconds=1.0/100.0)
        next_think = datetime.datetime.now()

        draw_period = datetime.timedelta(seconds=1.0/60.0)
        next_draw = datetime.datetime.now()

        self.status_string.quick_set('running main loop')
        while running:
            now = datetime.datetime.now()

            self.dc.set_non_blocking(0.001)
            self.dc.disgard()
            self.dc.handle.setblocking(True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if now >= next_think:
                next_think += think_period

                self.think()

                logic_frames += 1

            if now >= next_draw:
                next_draw = now + draw_period

                self.draw(screen)

                pygame.display.flip()
                draw_frames += 1

            if now >= next_stat:
                next_stat += stat_period
                seconds = stat_period.total_seconds()

                self.fps.quick_set(draw_frames / seconds)
                self.lps.quick_set(logic_frames / seconds)

                draw_frames = 0
                logic_frames = 0

        self.status_string.quick_set('saving state')

        self.status_string.quick_set('quitting pygame')
        pygame.quit()

        self.status_string.set('exiting cleanly')
