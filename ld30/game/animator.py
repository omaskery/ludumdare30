__author__ = 'Oliver Maskery'


import datetime
import pygame


class Animation(object):

    def __init__(self, name, frames, loops, rate, flipped):
        self.name = name
        self.frames = frames
        self.loops = loops
        self.flipped = flipped
        self.period = datetime.timedelta(seconds=1.0 / rate)


class Animator(object):

    def __init__(self, sheet):
        self.sheet = sheet
        self.rsheet = pygame.transform.flip(self.sheet, True, False)
        self.tile_size = 64
        self.animations = {}
        self.current = None
        self.index = 0
        self.width = int(self.sheet.get_size()[0] / self.tile_size)
        self.next_frame = datetime.datetime.now()
        self.callback = None

    def add_animation(self, name, frames, loop=False, rate=1.0, flipped=False):
        anim = Animation(name, frames, loop, rate, flipped)
        self.animations[name] = anim
        if self.current is None:
            self.current = anim
            self.next_frame = datetime.datetime.now() + anim.period

    def current_name(self):
        if self.current is not None:
            return self.current.name
        return ''

    def set_animation(self, name, callback=None):
        if self.current is not None and self.current.name == name:
            return

        self.current = self.animations[name]
        self.index = 0
        self.next_frame = datetime.datetime.now() + self.current.period
        if callback is not None:
            self.callback = callback

    def draw(self, context, x, y, ignore_camera=False):
        if self.current is None:
            return

        if datetime.datetime.now() >= self.next_frame:
            self.index += 1
            self.next_frame += self.current.period
            if self.index >= len(self.current.frames):
                if self.current.loops:
                    self.index = 0
                else:
                    self.current = None
                    if self.callback is not None:
                        self.callback()
                        self.callback = None
                    if self.current is None:
                        return

        if not ignore_camera:
            dx = x - context.camera[0]
            dy = y - context.camera[1]
        else:
            dx = x
            dy = y
        sprite_id = self.current.frames[self.index]
        if not self.current.flipped:
            area_x = int(sprite_id % self.width) * self.tile_size
        else:
            area_x = (self.width - 1 - int(sprite_id % self.width)) * self.tile_size
        area_y = int(sprite_id / self.width) * self.tile_size
        #print("sprite %s, width %s, x %s, y %s" % (sprite_id, self.width, area_x, area_y))
        area = (area_x, area_y, self.tile_size, self.tile_size)
        if not self.current.flipped:
            context.dest.blit(self.sheet, (dx, dy), area)
        else:
            context.dest.blit(self.rsheet, (dx, dy), area)

    def is_frame(self, sprite_id):
        if self.current is None:
            return False
        return self.current.frames[self.index] == sprite_id
