__author__ = 'Oliver Maskery'


from .particles import ParticleSystem
from .totem import Totem
import datetime
import pygame
import random
import math


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

        self.status_string.quick_set('initialising pygame')
        pygame.init()
        self.screen = screen = pygame.display.set_mode((800, 600))

        self.totem_sheet = pygame.transform.scale2x(pygame.image.load('data/sprites/totem.png').convert_alpha())
        self.totems = []
        self.particles = ParticleSystem()

        for index in range(3):
            totem = Totem(self.totem_sheet, self.particles)
            angle = random.random() * (2 * math.pi)
            radius = 100 + random.gauss(100, 10)
            totem.pos[0] = 400 + math.cos(angle) * radius
            totem.pos[1] = 300 + math.sin(angle) * radius
            self.totems.append(totem)

    def think(self):
        for totem in self.totems:
            totem.think()

        self.particles.think()
        self.particle_count.quick_set(len(self.particles.particles))

    def draw(self, dest):
        dest.fill((128, 200, 255))

        for totem in self.totems:
            totem.draw(dest)

        self.particles.draw(dest)

    def run(self):
        screen = self.screen
        running = True

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
