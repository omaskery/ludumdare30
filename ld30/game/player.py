__author__ = 'Oliver Maskery'


import datetime
import random
import pygame
import math


class Animation(object):

    def __init__(self, frames, loops, rate, flipped):
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
        anim = Animation(frames, loop, rate, flipped)
        self.animations[name] = anim
        if self.current is None:
            self.current = anim
            self.next_frame = datetime.datetime.now() + anim.period

    def set_animation(self, name, callback=None):
        self.current = self.animations[name]
        self.index = 0
        self.next_frame = datetime.datetime.now() + self.current.period
        if callback is not None:
            self.callback = callback

    def draw(self, context, x, y):
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

        dx = x - context.camera[0]
        dy = y - context.camera[1]
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


class Player(object):

    def __init__(self, debug_client, sheet, particles):
        self.dc = debug_client
        self.pos = [0, 0]
        self.animator = Animator(sheet)
        self.particles = particles
        self.totems = []

        idle_frames = [4, 5]
        walk_frames = [12, 13, 14, 15, 20, 21, 22]
        walk_rate = 10
        cough_frames = [28, 29, 30, 31]
        cough_rate = 4
        self.animator.add_animation('idle_right', idle_frames, True)
        self.animator.add_animation('idle_left', idle_frames, True, flipped=True)
        self.animator.add_animation('walk_right', walk_frames, True, rate=walk_rate)
        self.animator.add_animation('walk_left', walk_frames, True, flipped=True, rate=walk_rate)
        self.animator.add_animation('cough_right', cough_frames, False, rate=cough_rate)
        self.animator.add_animation('cough_left', cough_frames, False, flipped=True, rate=cough_rate)

        self.vel = [0, 0]
        self.friction = 0.8
        self.accel = 0.08

        default_page = self.dc.get_page('default')
        player_section = default_page.get_section('player')

        self.debug_pos = player_section.get_value('Position', 'vector2D', self.pos)

        self.moving = False
        self.dir_string = 'right'
        self.proximity = 0.0

    def think(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel[0] -= self.accel
            if not self.moving or self.dir_string != 'left':
                self.moving = True
                self.dir_string = 'left'
                self.animator.set_animation('walk_%s' % self.dir_string)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel[0] += self.accel
            if not self.moving or self.dir_string != 'right':
                self.moving = True
                self.dir_string = 'right'
                self.animator.set_animation('walk_%s' % self.dir_string)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel[1] -= self.accel
            if not self.moving:
                self.moving = True
                self.animator.set_animation('walk_%s' % self.dir_string)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel[1] += self.accel
            if not self.moving:
                self.moving = True
                self.animator.set_animation('walk_%s' % self.dir_string)

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] *= self.friction
        self.vel[1] *= self.friction

        if self.moving:
            movement_tolerance = 0.1
            if abs(self.vel[0]) < movement_tolerance and abs(self.vel[1]) < movement_tolerance:
                #print("stopping")
                self.moving = False
                self.animator.set_animation('idle_%s' % self.dir_string)
        elif random.random() <= 0.001:
            self.animator.set_animation('cough_%s' % self.dir_string, self.done_coughing)

        proximities = []
        for totem in self.totems:
            distance = math.hypot(self.pos[0] - totem.pos[0], self.pos[1] - totem.pos[1])
            sense_radius = 100.0
            if distance < sense_radius:
                percent = (sense_radius - distance) / sense_radius
                totem.intensity = percent
                proximities.append(percent)
            else:
                proximities.append(0.0)
                totem.intensity = 0.1
        if len(proximities) > 0:
            self.proximity = sum(proximities) / len(proximities)
        else:
            self.proximity = 0

    def done_coughing(self):
        self.animator.set_animation('idle_%s' % self.dir_string)

    def draw(self, context):
        context.camera_shake(self.proximity * 10.0)
        self.animator.draw(context, self.pos[0], self.pos[1])
