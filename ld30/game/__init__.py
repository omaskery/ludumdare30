__author__ = 'Oliver Maskery'


from .render_context import RenderContext
from .particles import ParticleSystem
from .player import Player
from .world import World
from .beam import Beam
import datetime
import pygame
import random


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

        self.status_string.set('initialising pygame')
        pygame.init()
        flags = 0
        if 'fullscreen' in self.settings.keys():
            if self.settings['fullscreen']:
                flags = pygame.FULLSCREEN

        resolution = (800, 600)
        if 'resolution' in self.settings.keys():
            resolution = tuple(self.settings['resolution'])
        self.screen = pygame.display.set_mode(resolution, flags)

        self.totem_sheet = pygame.transform.scale2x(pygame.image.load('data/sprites/totem.png').convert_alpha())
        self.particles = ParticleSystem()

        self.world = World(self.totem_sheet, self.particles)

        self.spawn_tile = random.choice([tile for tile in self.world.valid_tiles if not tile.blocked])
        if self.spawn_tile is None:
            print("spawned player in invalid tile")

        self.player = Player(self.dc, self.totem_sheet, self.particles)
        self.player.pos = [
            self.spawn_tile.pos[0] * self.world.tile_size[0],
            self.spawn_tile.pos[1] * self.world.tile_size[1] - 32
        ]
        print("spawning player in tile at %s, position: %s" % (self.spawn_tile.pos, self.player.pos))
        test_x, test_y = self.player.world_point()
        if self.world.tile_at_pos(test_x, test_y) is None:
            print("world tile is null at player feet")

        self.player.world = self.world

        self.context = RenderContext(self.screen)
        self.context.focus_on(self.player.pos)

        for index in range(20):
            x, y = self.player.pos
            if y - self.context.camera[1] < 0:
                break
            self.particles.add(Beam([x, y - (index * 64) - 4], self.totem_sheet))

    def think(self):
        self.world.think()

        self.player.think()

        self.particles.think()
        self.particle_count.quick_set(len(self.particles.particles))

        self.context.soft_focus_on(self.player.pos, 0.01)

        self.context.update()

    def draw(self, dest):
        dest.fill((128, 200, 255))

        self.world.put_in_draw_queue((self.player.world_point(), self.player))
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
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
