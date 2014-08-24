__author__ = 'Oliver Maskery'


import random
import math


class RenderContext(object):

    def __init__(self, screen):
        self.dest = screen
        self.size = screen.get_size()
        self.half_size = (int(self.size[0] / 2), int(self.size[1] / 2))
        self.camera = [0, 0]
        self.shake = [0, 0]

    def camera_shake(self, amount):
        angle = random.random() * (math.pi * 2)
        self.shake[0] += math.cos(angle) * amount
        self.shake[1] += math.sin(angle) * amount

    def focus_on(self, point):
        self.camera = [point[0] - self.half_size[0], point[1] - self.half_size[1]]

    def soft_focus_on(self, point, alpha):
        cx, cy = self.camera
        px, py = point
        px -= self.half_size[0]
        py -= self.half_size[1]
        dx, dy = px - cx, py - cy
        self.camera[0] += dx * alpha
        self.camera[1] += dy * alpha

    def update(self):
        self.camera[0] += self.shake[0]
        self.camera[1] += self.shake[1]
        self.shake = [0, 0]
