__author__ = 'Oliver Maskery'


from . import networking
from .. import common
import datetime
import socket
import pygame

class Drawable(object):

    def __init__(self):
        self.entity = None

    def draw(self, dest):
        pass


class PlayerDrawable(Drawable):

    def __init__(self, player):
        super().__init__()
        self.entity = player

    def draw(self, dest):
        if self.entity is None:
            return

        if self.entity.pos is not None:
            pygame.draw.rect(dest, (255, 0, 0), (self.entity.pos, (32, 32)))


class Client(object):

    def __init__(self, target, debug_client, settings):
        self.target = target
        self.dc = debug_client
        self.settings = settings
        self.networking = networking.Client(self, self.target, self.dc)

        self.player = common.Player()
        self.player.pos = None

        self.renderables = []
        self.renderables.append(PlayerDrawable(self.player))

        if 'player' in self.settings.keys():
            self.player.unblob(self.settings['player'])

        default_page = self.dc.get_page('default')
        framerates = default_page.get_section('Framerates')
        self.fps = framerates.get_value('FPS', 'int', 0)
        self.lps = framerates.get_value('LPS', 'int', 0)

        status = default_page.get_section('Status')
        self.status_string = status.get_value('Status', 'string', 'initialising')
        uuid = status.get_value('UUID', 'string', self.settings['uuid'])
        uuid.set(self.settings['uuid'])  # in case it existed before!

        player = default_page.get_section('Player')
        name = player.get_value('Name', 'string', " ".join(self.player.name))
        name.set(" ".join(self.player.name))  # in case it existed before
        self.debug_pos = player.get_value('Position', 'vector2D', None)
        self.debug_vel = player.get_value('Velocity', 'vector2D', [0, 0])

        self.player_vel = [0, 0]

        self.handlers = {
            'connect': self.handle_msg_connect
        }

        self.accepted = False

        self.debug_counter = 0

    def handle_message(self, message):
        print("networking reports message:", message)
        if 'ack' not in message.keys():
            return
        if message['ack'] not in self.handlers.keys():
            return
        self.handlers[message['ack']](message)

    def handle_msg_connect(self, message):
        if not message['success']:
            raise Exception("server refused connection")
        self.player.pos = message['pos']
        self.accepted = True

    def handle_connected(self, target, local_server):
        print("networking reports connection to %s (local server: %s)" % (target, local_server))
        self.networking.send_message(cmd='connect', player=self.player.blob())

    def think(self):
        debug_interval = 100

        player_accel = 0.5
        player_friction = 0.8

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            self.player_vel[0] -= player_accel
        elif pressed[pygame.K_RIGHT]:
            self.player_vel[0] += player_accel
        if pressed[pygame.K_UP]:
            self.player_vel[1] -= player_accel
        elif pressed[pygame.K_DOWN]:
            self.player_vel[1] += player_accel

        self.player.pos[0] += self.player_vel[0]
        self.player.pos[1] += self.player_vel[1]
        self.player_vel[0] *= player_friction
        self.player_vel[1] *= player_friction

        self.debug_counter += 1
        if self.debug_counter >= debug_interval:
            self.debug_counter = 0

            self.debug_pos.quick_set(self.player.pos)
            self.debug_vel.quick_set(self.player_vel)

    def run(self):
        self.status_string.set('initialising pygame')

        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        running = True

        draw_frames = 0
        logic_frames = 0

        self.status_string.set('configuring timers')
        stat_period = datetime.timedelta(seconds=1.0)
        next_stat = datetime.datetime.now() + stat_period

        think_period = datetime.timedelta(seconds=1.0/100.0)
        next_think = datetime.datetime.now()

        draw_period = datetime.timedelta(seconds=1.0/60.0)
        next_draw = datetime.datetime.now()

        self.status_string.set('running main loop')
        while running:
            now = datetime.datetime.now()

            self.networking.poll()
            self.dc.set_non_blocking(0.01)
            self.dc.disgard()
            self.dc.handle.setblocking(True)

            if self.networking.should_exit():
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if now >= next_think:
                next_think += think_period

                if self.accepted:
                    self.think()

                logic_frames += 1

            if now >= next_draw:
                next_draw = now + draw_period
                screen.fill((0, 0, 0))

                for drawable in self.renderables:
                    drawable.draw(screen)

                pygame.display.flip()
                draw_frames += 1

            if now >= next_stat:
                next_stat += stat_period
                seconds = stat_period.total_seconds()

                self.fps.set(draw_frames / seconds)
                self.lps.set(logic_frames / seconds)

                draw_frames = 0
                logic_frames = 0

        self.status_string.set('shutting down networking')
        self.networking.stop()

        self.status_string.set('saving state')
        self.settings['player'] = self.player.blob()

        self.status_string.set('quitting pygame')
        pygame.quit()

        self.status_string.set('exiting cleanly')