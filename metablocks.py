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

class Cross(Box):

    def _draw(self, canvas):
        p1 = path.path(path.moveto(0.5, 0.0), path.lineto(0.5, 1.0))
        p2 = path.path(path.moveto(0.0, 0.5), path.lineto(1.0, 0.5))

        attrs = [trafo.scale(sx=self.width, sy=self.height),
                 trafo.translate(self.sw.x, self.sw.y)]

        canvas.stroke(p1, attrs)
        canvas.stroke(p2, attrs)

class Text(Box):

    """ A Text object is a collection of lines """

    def __init__(self,
                 lines=[],
                 alignment=Alignment.center,
                 size=text.size.normal):

        super().__init__(border=None)
        self.lines = lines if lines else []
        self.alignment = alignment
        self.size = size

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

class TextBox(Box):

    """ A TextBox object is a Text contained in a Box """

    def __init__(self,
                 text,
                 alignment=Alignment.center,
                 **kwargs):

        super().__init__(**kwargs)

        self.text = text
        self.alignment = alignment

        self.initialize()

    def initialize(self):

        self.width = max(self.width, self.text.width)
        self.height = max(self.height, self.text.height)

        self.add_child(self.text)

        if self.alignment is Alignment.center:
            self.text.c = self.c
        elif self.alignment is Alignment.middle:
            self.text.c = self.c
        elif self.alignment is Alignment.left:
            self.text.w = self.w
        elif self.alignment is Alignment.right:
            self.text.e = self.e
        elif self.alignment is Alignment.top:
            self.text.n = self.n
        elif self.alignment is Alignment.bottom:
            self.text.s = self.s
        else:
            pass

    def __getitem__(self, key):
        return self.children[0].__getitem__(key)

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

def create_label(name, size=text.size.LARGE):
    return TextBox([name], Alignment.center, size, border=None)

""" a coordinate system """
class XY(Box):

    def __init__(self, n_x_ticks, n_y_ticks, x_name, y_name, delta=1.5):
        super().__init__(border=None)
        self.n_x_ticks = n_x_ticks
        self.n_y_ticks = n_y_ticks
        self.x_name = x_name
        self.y_name = y_name
        self.delta  = delta
        self.axes = {}

        self.width = delta * n_x_ticks + 2
        self.height = delta * n_y_ticks + 2

        self.initialize()

    def initialize(self):

        x_axis = Connection([self.nw, self.ne])
        y_axis = Connection([self.nw, self.sw])
        for axis in x_axis, y_axis:
            axis.add_style_element(deco.earrow(size=0.5))
            self.add_child(axis)
        self.axes['x'] = x_axis
        self.axes['y'] = y_axis

        x_label = create_label(self.x_name)
        y_label = create_label(self.y_name)
        x_label.w = x_axis.e
        y_label.n = y_axis.s
        self.add_child(x_label)
        self.add_child(y_label)

    def add_x_tick(self, tick, x):
        """ disgusting """
        x = self.delta*x + 1
        tick.s = Point(x, self.axes['x'].s.y)
        self.add_child(tick)

    def add_y_tick(self, tick, y):
        """ disgusting """
        y = self.delta * self.n_y_ticks + 1 - self.delta*y
        tick.e = Point(self.axes['y'].w.x, y)
        self.add_child(tick)

    def add_object(self, box, x, y):

        x_coord = self.delta*x + 1
        y_coord = self.delta*self.n_y_ticks + 1 - self.delta*y

        box.c = Point(x_coord, y_coord)
        self.add_child(box)

""" A labeled arrow horizontal only ... """
class LabeledArrow(Box):

    def __init__(self, label, width=2, height=1, border=None):

        super().__init__(width, height, border)
        self.label = label
        self.initialize()

    def initialize(self):

        arrow = Connection([self.w, self.e])
        arrow.add_style_element(deco.earrow(size=0.3))
        self.add_child(arrow)

        labeltext = Line(self.label)
        arrow.width = labeltext.width
        labeltext.s = arrow.n + (0, 0.2)
        self.add_child(labeltext)

        self.stretch(0.1)

    def colour(self, kleur):
        self.children[0].add_style_element(kleur)
