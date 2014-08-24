__author__ = 'Oliver Maskery'


from .particles import BaseParticle
from .animator import Animator
import datetime


class Beam(BaseParticle):

    def __init__(self, pos, sheet, intensity=0):
        super().__init__(sheet, pos[0], pos[1])

        self.animator = Animator(sheet)
        self.intensity = intensity

        self.startup_duration = datetime.timedelta(seconds=0.01)
        self.decay_duration = datetime.timedelta(seconds=0.2)
        self.starting = True

        self.next_event = datetime.datetime.now() + self.startup_duration

        pulse_rate = 10
        self.animator.add_animation(3, [16, 17], True, rate=pulse_rate)
        self.animator.add_animation(2, [24, 25], True, rate=pulse_rate)
        self.animator.add_animation(1, [32, 33], True, rate=pulse_rate)
        self.animator.add_animation(0, [40, 41], True, rate=pulse_rate)

        self.set_intensity(self.intensity)

    def increase_intensity(self):
        self.set_intensity(min(self.intensity + 1, 3))

    def decrease_intensity(self):
        self.set_intensity(max(self.intensity - 1, 0))

    def set_intensity(self, intensity):
        self.intensity = intensity
        self.animator.set_animation(self.intensity)

    def update(self):
        if datetime.datetime.now() >= self.next_event:
            if self.starting:
                self.increase_intensity()
                if self.intensity >= 3:
                    self.next_event += self.decay_duration
                    self.starting = False
                else:
                    self.next_event += self.startup_duration
            elif self.intensity > 0:
                self.decrease_intensity()
                self.next_event += self.decay_duration
            else:
                self.die()

    def draw(self, context):
        context.camera_shake(self.intensity / 2)
        self.animator.draw(context, self.x, self.y)
