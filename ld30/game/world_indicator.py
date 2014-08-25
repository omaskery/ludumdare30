__author__ = 'Oliver Maskery'


from .animator import Animator


class WorldIndicator(object):

    def __init__(self, sheet, pos):
        self.animator = Animator(sheet)
        self.pos = pos
        self.active = False
        self.animator.add_animation('active', [35], True, rate=1)
        self.animator.add_animation('inactive', [34], True, rate=1)
        self.make_inactive()

    def make_active(self):
        self.active = True
        self.animator.set_animation('active')

    def make_inactive(self):
        self.active = False
        self.animator.set_animation('inactive')

    def draw(self, context):
        self.animator.draw(context, self.pos[0], self.pos[1], ignore_camera=True)


class WorldBar(object):

    def __init__(self, sheet, count, centre_pos, max_width):
        self.sheet = sheet
        self.count = count
        self.centre_pos = centre_pos
        self.max_width = max_width
        self.spacing = max_width / self.count
        left_x = self.centre_pos[0] - (self.max_width / 2)
        y = self.centre_pos[1] - 32
        self.indicators = [
            WorldIndicator(sheet, [left_x + self.spacing * index, y])
            for index in range(count)
        ]

    def make_active(self, index):
        if 0 <= index < self.count:
            for indicator in self.indicators:
                indicator.make_inactive()
            self.indicators[index].make_active()

    def draw(self, context):
        for indicator in self.indicators:
            indicator.draw(context)
