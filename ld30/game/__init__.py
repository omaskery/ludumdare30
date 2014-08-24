__author__ = 'Oliver Maskery'


from .particles import ParticleSystem
from .world import World
import datetime
import pygame


class RenderContext(object):

    def __init__(self, screen):
        self.dest = screen
        self.size = screen.get_size()
        self.half_size = (int(self.size[0] / 2), int(self.size[1] / 2))
        self.camera = [0, 0]

    def focus_on(self, point):
        self.camera = [point[0] - self.half_size[0], point[1] - self.half_size[1]]


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
        self.screen = pygame.display.set_mode((800, 600))

        self.totem_sheet = pygame.transform.scale2x(pygame.image.load('data/sprites/totem.png').convert_alpha())
        self.particles = ParticleSystem()

        self.world = World(self.totem_sheet, self.particles)

        self.context = RenderContext(self.screen)
        self.context.focus_on(self.world.centre_offset)

    def think(self):
        self.world.think()

        self.particles.think()
        self.particle_count.quick_set(len(self.particles.particles))

    def draw(self, dest):
        dest.fill((128, 200, 255))

        self.world.draw(self.context)

        self.particles.draw(self.context)

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
