from metapyx import *
from metalayout import *

class Circle(Box):

    def _draw(self, canvas, level=0):

        if not self.border:
            return

        sw = self.get('sw', level)
        p = path.circle(0, 0, 0.5) # radius is required
        self.style.append(trafo.scale(sx=self.width, sy=self.height))
        self.style.append(trafo.translate(sw.x + self.width/2,
                                          sw.y + self.height/2))
        canvas.stroke(p, self.style)

class Text(Box):

    """ A Text object is a collection of lines """

    def __init__(self,
                 lines=[],
                 alignment=Alignment.center):

        super().__init__(border=None)
        self.lines = lines if lines else []
        self.alignment = alignment

        self.dict_ = {}

        self.initialize()

    def initialize(self):

        golden = (1 + 5**0.5) / 2

        for line in self.lines:
            self.dict_[line.string] = line
            self.add_child(line)

        height = max(child.height for child in self.children)
        delta  = 0.66*(golden - 1) * height

        top_to_bottom(self.alignment, delta, self.children[0],
                *self.children[1:])

        self.stretch(delta)

    def __getitem__(self, key):
        return self.dict_[key]

def manhattan_connection_x(from_, to_):
    x, y = to_.x, from_.y
    return Connection([from_, Point(x, y), to_])

def manhattan_connection_y(from_, to_):
    x, y = from_.x, to_.y
    return Connection([from_, Point(x, y), to_])

def staircase_connection_x(from_, to_):
    x1, y1 = (from_.x + to_.x)/2, from_.y
    x2, y2 = x1, to_.y
    return Connection([from_, Point(x1, y1), Point(x2, y2), to_])

def staircase_connection_y(from_, to_):
    x1, y1 = from_.x, (from_.y + to_.y)/2
    x2, y2 = to_.x, y1
    return Connection([from_, Point(x1, y1), Point(x2, y2), to_])
