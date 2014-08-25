__author__ = 'Oliver Maskery'


from .animator import Animator
from .pedestal import Pedestal
import datetime
import random
import pygame
import math


class Player(object):

    def __init__(self, debug_client, sheet, particles):
        self.dc = debug_client
        self.pos = [0, 0]
        self.animator = Animator(sheet)
        self.particles = particles
        self.world = None
        self.near_totem = None

        idle_frames = [4, 5]
        walk_frames = [12, 13, 14, 15, 20, 21, 22]
        walk_rate = 10
        cough_frames = [28, 29, 30, 31]
        cough_rate = 4
        kneel_frames = [5, 6, 7]
        kneel_rate = 2
        pray_frames = [7]
        extinguish_frames = [36, 37, 38, 39]
        self.animator.add_animation('idle_right', idle_frames, True)
        self.animator.add_animation('idle_left', idle_frames, True, flipped=True)
        self.animator.add_animation('walk_right', walk_frames, True, rate=walk_rate)
        self.animator.add_animation('walk_left', walk_frames, True, flipped=True, rate=walk_rate)
        self.animator.add_animation('cough_right', cough_frames, False, rate=cough_rate)
        self.animator.add_animation('cough_left', cough_frames, False, flipped=True, rate=cough_rate)
        self.animator.add_animation('kneel_right', kneel_frames, False, rate=kneel_rate)
        self.animator.add_animation('kneel_left', kneel_frames, False, flipped=True, rate=kneel_rate)
        self.animator.add_animation('pray_right', pray_frames, True, rate=1)
        self.animator.add_animation('pray_left', pray_frames, True, flipped=True, rate=1)
        self.animator.add_animation('extinguish_right', extinguish_frames, False, rate=3)
        self.animator.add_animation('extinguish_left', extinguish_frames, False, flipped=True, rate=3)

        self.animator.set_animation('pray_right')

        self.vel = [0, 0]
        self.friction = 0.8
        self.accel = 0.08

        default_page = self.dc.get_page('default')
        player_section = default_page.get_section('player')

        self.debug_pos = player_section.get_value('Position', 'vector2D', self.pos)

        self.moving = False
        self.dir_string = 'right'
        self.proximity = 0.0

        self.teleport_request = None

    def world_point(self):
        return (self.pos[0] + 32, self.pos[1] + 58)

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

        if self.world is not None:
            test_x, test_y = self.world_point()
            test_x += self.vel[0]
            test_y += self.vel[1]
            new_tile_under = self.world.tile_at_pos(test_x, test_y)
            if new_tile_under is not None and not self.check_detail_collision():
                self.pos[0] += self.vel[0]
                self.pos[1] += self.vel[1]
            else:
                self.vel = [0, 0]
        self.vel[0] *= self.friction
        self.vel[1] *= self.friction

        if self.world is not None:
            proximities = []
            near_totem_this_tick = False
            nearest_totem = None
            for totem in self.world.totems:
                distance = math.hypot(self.pos[0] - totem.pos[0], self.pos[1] - totem.pos[1])
                sense_radius = 50.0
                teleport_radius = 40.0
                if nearest_totem is None or nearest_totem[0] > distance:
                    nearest_totem = (distance, totem)
                if distance < sense_radius:
                    percent = (sense_radius - distance) / sense_radius
                    totem.intensity = percent
                    proximities.append(percent)
                    if distance < teleport_radius and not self.moving:
                        near_totem_this_tick = True
                        if self.near_totem is None and not self.praying_animation():
                            print("kneeling to pray")
                            self.animator.set_animation('kneel_%s' % self.dir_string, self.done_kneeling)
                            self.near_totem = datetime.datetime.now()
                else:
                    proximities.append(0.0)
                    totem.intensity = 0.1
            if self.near_totem is not None:
                if datetime.datetime.now() - self.near_totem >= datetime.timedelta(seconds=5.0):
                    if self.teleport_request is not None:
                        print("issuing teleport request")
                        self.teleport_request(nearest_totem[1])
                    self.near_totem = None
                elif not near_totem_this_tick:
                    if self.near_totem is not None:
                        print("moved away from totem")
                    self.near_totem = None

            if len(proximities) > 0:
                self.proximity = sum(proximities) / len(proximities)
            else:
                self.proximity = 0

            for detail in self.world.details:
                if not isinstance(detail, Pedestal):
                    continue

                distance = math.hypot(self.pos[0] - detail.pos[0], self.pos[1] - detail.pos[1])
                sense_radius = 50.0

                if distance < sense_radius and self.animator.current_name().startswith('idle_') and detail.lit:
                    extinguish_done = lambda: self.done_extinguishing(detail)
                    self.animator.set_animation('extinguish_%s' % self.dir_string, extinguish_done)
                    break

        if self.moving:
            movement_tolerance = 0.1
            if abs(self.vel[0]) < movement_tolerance and abs(self.vel[1]) < movement_tolerance:
                #print("stopping")
                self.moving = False
                self.animator.set_animation('idle_%s' % self.dir_string)
        elif self.animator.current_name().startswith('idle_') and random.random() <= 0.001:
            self.animator.set_animation('cough_%s' % self.dir_string, self.done_coughing)

        self.debug_pos.quick_set(self.pos)

    def done_extinguishing(self, pedestal):
        pedestal.extinguish()
        self.animator.set_animation('idle_%s' % self.dir_string)

    def praying_animation(self):
        anim = self.animator.current_name()
        return anim.startswith('pray_') or anim.startswith('kneel_')

    def check_detail_collision(self):
        test_x = self.pos[0] + self.vel[0]
        test_y = self.pos[1] + self.vel[1]
        for detail in self.world.details:
            delta = [test_x - detail.pos[0], test_y - detail.pos[1]]
            distance = math.hypot(delta[0], delta[1])
            touch_radius = 15
            if distance <= touch_radius:
                return True
        return False

    def done_coughing(self):
        print("ahem")
        self.animator.set_animation('idle_%s' % self.dir_string)

    def done_kneeling(self):
        print("praying")
        self.animator.set_animation('pray_%s' % self.dir_string)

    def draw(self, context):
        if self.animator.current_name().startswith('pray_'):
            context.camera_shake(self.proximity * 10.0)
        self.animator.draw(context, self.pos[0], self.pos[1])
