__author__ = 'Oliver Maskery'


import datetime
import pygame


class Client(object):

    def __init__(self, target, debug_client, settings):
        self.target = target
        self.dc = debug_client
        self.settings = settings

        default_page = self.dc.get_page('default')
        framerates = default_page.get_section('Framerates')
        self.fps = framerates.get_value('FPS', 'int', 0)
        self.lps = framerates.get_value('LPS', 'int', 0)

        status = default_page.get_section('Status')
        self.status_string = status.get_value('Status', 'string', 'initialising')
        uuid = status.get_value('UUID', 'string', self.settings['uuid'])
        uuid.set(self.settings['uuid'])  # in case it didn't exist before!

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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if now >= next_think:
                next_think += think_period

                #

                logic_frames += 1

            if now >= next_draw:
                next_draw = now + draw_period
                screen.fill((0, 0, 0))

                #

                pygame.display.flip()
                draw_frames += 1

            if now >= next_stat:
                next_stat += stat_period
                seconds = stat_period.total_seconds()

                self.fps.set(draw_frames / seconds)
                self.lps.set(logic_frames / seconds)

                draw_frames = 0
                logic_frames = 0

        self.status_string.set('quitting pygame')
        pygame.quit()

        self.status_string.set('exiting cleanly')
